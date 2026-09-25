import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright

# Load environment variables
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
UI_REGRESSION_DIR = ROOT_DIR / "ui_regression"

# Ensure root and ui_regression are in sys.path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(UI_REGRESSION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_REGRESSION_DIR))

# Auth storage path
AUTH_DIR = ROOT_DIR / "auth"
AUTH_STATE = AUTH_DIR / "auth_state.json"
if not AUTH_STATE.exists() and (ROOT_DIR / "auth_state.json").exists():
    AUTH_STATE = ROOT_DIR / "auth_state.json"


# ============================================================
# BASELINE & LIVE URL FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def base_url():
    value = os.getenv("BASELINE_URL") or os.getenv("BASE_URL")
    if not value:
        raise RuntimeError(
            "BASELINE_URL (or legacy BASE_URL) is missing from .env"
        )
    return value


@pytest.fixture(scope="session")
def baseline_url(base_url):
    return os.getenv("BASELINE_URL") or base_url


@pytest.fixture(scope="session")
def live_url(base_url):
    return os.getenv("LIVE_URL") or base_url


# ============================================================
# BROWSER
# ============================================================

@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    browser_instance = playwright.chromium.launch(
        headless=False,
        slow_mo=300,
    )
    yield browser_instance
    browser_instance.close()


# ============================================================
# AUTHENTICATE ONCE (BACKWARD-COMPATIBLE FIXTURE)
# ============================================================

@pytest.fixture(scope="session")
def authenticated_state(
    browser,
    base_url,
):
    # --------------------------------------------------------
    # Reuse existing authentication state
    # --------------------------------------------------------
    if (
        AUTH_STATE.exists()
        and AUTH_STATE.stat().st_size > 0
    ):
        return str(AUTH_STATE)

    # --------------------------------------------------------
    # Credentials
    # --------------------------------------------------------
    email = os.getenv("BASELINE_TEST_USER_EMAIL") or os.getenv("TEST_USER_EMAIL")
    password = os.getenv("BASELINE_TEST_USER_PASSWORD") or os.getenv("TEST_USER_PASSWORD")

    if not email:
        raise RuntimeError(
            "BASELINE_TEST_USER_EMAIL is missing from .env"
        )
    if not password:
        raise RuntimeError(
            "BASELINE_TEST_USER_PASSWORD is missing from .env"
        )

    # --------------------------------------------------------
    # Create context
    # --------------------------------------------------------
    context = browser.new_context()
    page = context.new_page()

    # --------------------------------------------------------
    # Login flow
    # --------------------------------------------------------
    page.goto(base_url, wait_until="domcontentloaded", timeout=60000)

    email_input = page.locator("#email, input[name='email'], input[type='email']").first
    password_input = page.locator("#password, input[name='password'], input[type='password']").first
    login_btn = page.locator('button.xn-btn-login[type="submit"], button[type="submit"]').first

    email_input.wait_for(state="visible", timeout=15000)
    password_input.wait_for(state="visible", timeout=15000)

    email_input.fill(email)
    password_input.fill(password)

    remember_me = page.locator("#inputCheckbox, input[type='checkbox']").first
    try:
        if remember_me.is_visible() and not remember_me.is_checked():
            remember_me.check()
    except Exception:
        pass

    login_btn.click()

    # --------------------------------------------------------
    # Verify authentication
    # --------------------------------------------------------
    post_login_url = os.getenv("BASELINE_POST_LOGIN_URL_PATTERN") or os.getenv(
        "POST_LOGIN_URL_PATTERN"
    )
    post_login_selector = os.getenv("POST_LOGIN_SELECTOR")

    if post_login_url:
        page.wait_for_url(post_login_url, timeout=15000)
    elif post_login_selector:
        page.locator(post_login_selector).first.wait_for(state="visible", timeout=15000)
    else:
        password_input.wait_for(state="hidden", timeout=15000)

    # --------------------------------------------------------
    # Save authentication state
    # --------------------------------------------------------
    AUTH_STATE.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(AUTH_STATE))
    context.close()

    return str(AUTH_STATE)


# ============================================================
# AUTHENTICATED PAGE
# ============================================================

from ui_regression.crawler.crawler_config import VIEWPORTS, DEFAULT_VIEWPORT

@pytest.fixture(scope="module")
def authenticated_page(
    browser,
    authenticated_state,
    base_url,
):
    context = browser.new_context(
        storage_state=authenticated_state,
        viewport=VIEWPORTS[DEFAULT_VIEWPORT],
    )
    page = context.new_page()
    page.goto(
        base_url,
        wait_until="domcontentloaded",
        timeout=60000,
    )
    yield page
    context.close()


# ============================================================
# TRADING FLAG
# ============================================================

@pytest.fixture
def trade_enabled():
    return (
        os.getenv(
            "ENABLE_TRADE_TESTS",
            "false",
        ).lower()
        == "true"
    )


# ============================================================
# DIAGNOSTIC HOOK: TEST FAILURE CAPTURE
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution outcome (setup, call, teardown).
    Attaches the result to request.node as rep_setup, rep_call, rep_teardown
    so fixtures can detect test failure and trigger automatic screenshots & tracing.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

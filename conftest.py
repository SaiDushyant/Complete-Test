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


def pytest_addoption(parser):
    """Register CLI options for browser execution."""
    try:
        parser.addoption(
            "--headed",
            action="store_true",
            default=False,
            help="Run tests in headed browser mode (default: headless)",
        )
    except Exception:
        pass
    try:
        parser.addoption(
            "--slowmo",
            action="store",
            default=None,
            help="Slow down test execution in milliseconds",
        )
    except Exception:
        pass


# ============================================================
# PLAYWRIGHT & BROWSER
# ============================================================

from playwright.sync_api import Playwright, sync_playwright

@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright: Playwright, pytestconfig: pytest.Config):
    headed_flag = False
    try:
        headed_flag = bool(pytestconfig.getoption("--headed"))
    except Exception:
        pass

    from config.settings import settings
    headless = False if headed_flag else settings.browser.headless
    slow_mo = 0 if headless else (settings.browser.slow_mo or 300)

    browser_instance = playwright.chromium.launch(
        headless=headless,
        slow_mo=slow_mo,
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


def pytest_sessionstart(session):
    """Archive prior test runs and prepare fresh log session on test startup."""
    if not hasattr(session.config, "workerinput"):
        try:
            from config.settings import settings
            from workflows.shared.utils.test_logger import GlobalTestLogger
            import sys
            target_hint = None
            markexpr = getattr(getattr(session.config, "option", None), "markexpr", "") or ""
            cmd_str = " ".join(sys.argv)
            is_mock = "mock" in markexpr or "mock" in cmd_str or "test_mock_" in cmd_str or "/mock" in cmd_str
            is_val = "validation" in markexpr or "validation" in cmd_str or "test_val_" in cmd_str
            if hasattr(session.config, "args"):
                for arg in session.config.args:
                    if "test_mock_" in arg or "/mock" in arg:
                        is_mock = True
                    elif "test_val_" in arg or "validation" in arg:
                        is_val = True
                    if "test_" in arg and not target_hint:
                        target_hint = Path(arg.split("::")[0]).stem

            if is_mock:
                suite_dir = settings.mock_reports_dir
            elif is_val:
                suite_dir = settings.validation_reports_dir
            else:
                suite_dir = settings.workflow_reports_dir

            GlobalTestLogger.get_instance(suite_dir=suite_dir).prepare_fresh_session(run_type_hint=target_hint)
        except Exception:
            pass


# ============================================================
# DIAGNOSTIC HOOK: TEST FAILURE CAPTURE & TELEMETRY
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution outcome (setup, call, teardown).
    Attaches the result to request.node as rep_setup, rep_call, rep_teardown
    so fixtures can detect test failure and trigger automatic screenshots & tracing.
    Also records test outcomes and runtime diagnostics to GlobalTestLogger.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    should_record = (rep.when == "call") or (rep.when == "setup" and rep.failed)
    if should_record:
        try:
            from workflows.shared.utils.test_logger import (
                GlobalTestLogger,
                extract_test_meaning,
            )

            meaning = extract_test_meaning(item)
            captured = ""
            if hasattr(rep, "capstdout") and rep.capstdout:
                captured += f"--- STDOUT ---\n{rep.capstdout}\n"
            if hasattr(rep, "capstderr") and rep.capstderr:
                captured += f"--- STDERR ---\n{rep.capstderr}\n"

            if rep.passed:
                status = "PASSED"
                reason = "Test completed successfully"
                error_tb = ""
            elif rep.skipped:
                status = "SKIPPED"
                reason = getattr(rep, "wasxfail", None) or "Test skipped"
                error_tb = str(rep.longrepr) if hasattr(rep, "longrepr") else ""
            else:
                status = "FAILED"
                long_text = str(getattr(rep, "longreprtext", rep.longrepr))
                lines = [l.strip() for l in long_text.splitlines() if l.strip()]
                reason = lines[-1] if lines else "Test execution failed"
                if rep.when == "setup":
                    reason = f"Setup failure: {reason}"
                error_tb = long_text

            # Extract runtime diagnostics telemetry from page if available
            diag_data = {}
            try:
                page_obj = None
                if hasattr(item, "funcargs"):
                    for val in item.funcargs.values():
                        if hasattr(val, "_diagnostics"):
                            page_obj = val
                            break
                        elif hasattr(val, "page") and hasattr(val.page, "_diagnostics"):
                            page_obj = val.page
                            break
                if page_obj and hasattr(page_obj, "_diagnostics"):
                    d = page_obj._diagnostics
                    diag_data = {
                        "clean": not d.has_errors(),
                        "uncaught_js_errors": len(d.page_errors),
                        "console_errors": len(d.get_console_errors()),
                        "console_warnings": len(d.get_console_warnings()),
                        "failed_requests": len(d.failed_requests),
                        "http_errors": len(d.http_errors),
                        "js_error_items": d.page_errors,
                        "console_error_items": d.get_console_errors(),
                        "failed_request_items": d.failed_requests,
                        "http_error_items": d.http_errors,
                    }
            except Exception:
                pass

            GlobalTestLogger.get_instance().record_test(
                test_id=item.nodeid,
                meaning=meaning,
                status=status,
                reason=reason,
                duration=rep.duration,
                captured_output=captured,
                error_traceback=error_tb,
                diagnostics=diag_data,
            )
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """Finalize all global text logs at the end of the pytest session."""
    try:
        from workflows.shared.utils.test_logger import GlobalTestLogger
        GlobalTestLogger.get_instance().finalize()
    except Exception:
        pass


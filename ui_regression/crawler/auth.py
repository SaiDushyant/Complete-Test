import os
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page

from crawler.crawler_config import (
    AUTH_STATE,
    BASELINE_AUTH_STATE,
    BASELINE_POST_LOGIN_URL_PATTERN,
    BASELINE_TEST_USER_EMAIL,
    BASELINE_TEST_USER_PASSWORD,
    BASELINE_URL,
    DEFAULT_VIEWPORT,
    LIVE_AUTH_STATE,
    LIVE_POST_LOGIN_URL_PATTERN,
    LIVE_TEST_USER_EMAIL,
    LIVE_TEST_USER_PASSWORD,
    LIVE_URL,
    POST_LOGIN_SELECTOR,
    POST_LOGIN_URL_PATTERN,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TIMEOUT,
    VIEWPORTS,
)


async def is_session_expired(page: Page) -> bool:
    """
    Check if the current page indicates an expired or invalid session.
    Detects redirect to /login or presence of login form fields.
    """
    current_url = page.url.lower()
    if "/login" in current_url or "/signin" in current_url:
        return True

    # Check if login input fields are visible on current page
    try:
        email_visible = await page.locator("#email, input[type='email'], input[name='email']").first.is_visible()
        password_visible = await page.locator("#password, input[type='password']").first.is_visible()
        if email_visible and password_visible:
            return True
    except Exception:
        pass

    return False


async def login(
    page: Page,
    email: str = None,
    password: str = None,
    base_url: str = None,
    post_login_url_pattern: str = None,
    post_login_selector: str = None,
):
    """
    Perform asynchronous login to authenticate the browser session.
    """
    target_base_url = base_url or BASELINE_URL
    is_live = bool(base_url and base_url.rstrip("/") == LIVE_URL.rstrip("/") and LIVE_URL.rstrip("/") != BASELINE_URL.rstrip())
    target_email = email or (LIVE_TEST_USER_EMAIL if is_live else BASELINE_TEST_USER_EMAIL)
    target_password = password or (LIVE_TEST_USER_PASSWORD if is_live else BASELINE_TEST_USER_PASSWORD)
    target_pattern = post_login_url_pattern if post_login_url_pattern is not None else (LIVE_POST_LOGIN_URL_PATTERN if is_live else BASELINE_POST_LOGIN_URL_PATTERN)
    target_selector = post_login_selector if post_login_selector is not None else POST_LOGIN_SELECTOR

    if not target_email:
        raise RuntimeError("BASELINE_TEST_USER_EMAIL (or LIVE_TEST_USER_EMAIL) is missing from .env")

    if not target_password:
        raise RuntimeError("BASELINE_TEST_USER_PASSWORD (or LIVE_TEST_USER_PASSWORD) is missing from .env")

    print(f"Navigating to {target_base_url} for authentication...")
    await page.goto(
        target_base_url,
        wait_until="domcontentloaded",
        timeout=TIMEOUT,
    )

    email_input = page.locator("#email, input[type='email'], input[name='email']").first
    password_input = page.locator("#password, input[type='password']").first
    remember_me = page.locator("#inputCheckbox, input[type='checkbox']").first
    login_button = page.locator('button.xn-btn-login[type="submit"], button[type="submit"], input[type="submit"]').first

    # Wait for login inputs
    await email_input.wait_for(state="visible", timeout=15000)
    await password_input.wait_for(state="visible", timeout=15000)

    # Fill credentials
    await email_input.fill(target_email)
    await password_input.fill(target_password)

    # Check remember-me if available
    try:
        if await remember_me.is_visible():
            if not await remember_me.is_checked():
                await remember_me.check()
    except Exception:
        pass

    # Click login button
    await login_button.click()

    # Verify authentication
    if target_pattern:
        await page.wait_for_url(target_pattern, timeout=15000)
    elif target_selector:
        await page.locator(target_selector).first.wait_for(
            state="visible", timeout=15000
        )
    else:
        await password_input.wait_for(state="hidden", timeout=15000)

    print(f"Authentication successful on {target_base_url}.")


async def create_authenticated_context(
    browser: Browser,
    viewport: dict = None,
    auth_state_path: Path = None,
    base_url: str = None,
    email: str = None,
    password: str = None,
    post_login_url_pattern: str = None,
    post_login_selector: str = None,
) -> BrowserContext:
    """
    Create a Playwright BrowserContext with authentication.
    Reuses existing auth state file if valid for target base_url;
    otherwise performs login and saves fresh state.
    Configures context with the requested viewport size.
    """
    effective_viewport = viewport or VIEWPORTS.get(DEFAULT_VIEWPORT, {"width": 1280, "height": 800})
    target_base_url = base_url or BASELINE_URL
    target_auth_state = Path(auth_state_path) if auth_state_path else (
        LIVE_AUTH_STATE if (base_url and base_url != BASELINE_URL) else AUTH_STATE
    )

    if target_auth_state.exists() and target_auth_state.stat().st_size > 0:
        print(f"Loading existing authentication state from: {target_auth_state}")
        try:
            context = await browser.new_context(
                storage_state=str(target_auth_state),
                viewport=effective_viewport,
            )
            test_page = await context.new_page()
            await test_page.goto(
                target_base_url,
                wait_until="domcontentloaded",
                timeout=TIMEOUT,
            )
            await test_page.wait_for_timeout(1000)

            if not await is_session_expired(test_page):
                print(f"Existing session on {target_base_url} is valid.")
                await test_page.close()
                return context

            print(f"Session expired or invalid for {target_base_url}. Re-authenticating...")
            await test_page.close()
            await context.close()
        except Exception as e:
            print(f"Auth state validation failed ({e}). Creating fresh session...")

    print("Initiating new authentication session...")
    context = await browser.new_context(viewport=effective_viewport)
    page = await context.new_page()

    await login(
        page=page,
        email=email,
        password=password,
        base_url=target_base_url,
        post_login_url_pattern=post_login_url_pattern,
        post_login_selector=post_login_selector,
    )

    # Save storage state for subsequent runs
    target_auth_state.parent.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(target_auth_state))
    print(f"Authentication state saved to: {target_auth_state}")

    await page.close()
    return context



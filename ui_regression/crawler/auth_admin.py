import os
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page

from crawler.crawler_config import (
    ADMIN_AUTH_STATE,
    ADMIN_BASE_URL,
    ADMIN_LOGIN_URL,
    ADMIN_POST_LOGIN_URL_PATTERN,
    ADMIN_USER_PASSWORD,
    ADMIN_USER_USERNAME,
    BASELINE_ADMIN_AUTH_STATE,
    BASELINE_ADMIN_BASE_URL,
    BASELINE_ADMIN_LOGIN_URL,
    BASELINE_ADMIN_POST_LOGIN_URL_PATTERN,
    BASELINE_ADMIN_USER_PASSWORD,
    BASELINE_ADMIN_USER_USERNAME,
    DEFAULT_VIEWPORT,
    LIVE_ADMIN_AUTH_STATE,
    LIVE_ADMIN_BASE_URL,
    LIVE_ADMIN_LOGIN_URL,
    LIVE_ADMIN_POST_LOGIN_URL_PATTERN,
    LIVE_ADMIN_USER_PASSWORD,
    LIVE_ADMIN_USER_USERNAME,
    TIMEOUT,
    VIEWPORTS,
)


async def is_admin_session_expired(page: Page) -> bool:
    """
    Check if the current admin page indicates an expired or redirected session.
    """
    current_url = page.url.lower()
    if "/login" in current_url or "/signin" in current_url:
        return True

    try:
        username_input = page.locator("#username, input[name='username']").first
        password_input = page.locator("#password, input[name='password']").first
        if await username_input.is_visible() and await password_input.is_visible():
            return True
    except Exception:
        pass

    return False


async def login_admin(
    page: Page,
    username: str = None,
    password: str = None,
    login_url: str = None,
    post_login_url_pattern: str = None,
):
    """
    Perform asynchronous admin login and verify access to Admin Console.
    """
    is_live = bool(login_url and login_url.rstrip("/") == LIVE_ADMIN_LOGIN_URL.rstrip("/") and LIVE_ADMIN_LOGIN_URL.rstrip("/") != BASELINE_ADMIN_LOGIN_URL.rstrip())
    target_username = username or (LIVE_ADMIN_USER_USERNAME if is_live else BASELINE_ADMIN_USER_USERNAME)
    target_password = password or (LIVE_ADMIN_USER_PASSWORD if is_live else BASELINE_ADMIN_USER_PASSWORD)
    target_login_url = login_url or (LIVE_ADMIN_LOGIN_URL if is_live else BASELINE_ADMIN_LOGIN_URL)
    target_pattern = post_login_url_pattern if post_login_url_pattern is not None else (LIVE_ADMIN_POST_LOGIN_URL_PATTERN if is_live else BASELINE_ADMIN_POST_LOGIN_URL_PATTERN)

    if not target_username:
        raise RuntimeError("BASELINE_ADMIN_USER_USERNAME (or LIVE_ADMIN_USER_USERNAME) is missing from .env")

    if not target_password:
        raise RuntimeError("BASELINE_ADMIN_USER_PASSWORD (or LIVE_ADMIN_USER_PASSWORD) is missing from .env")

    print(f"Navigating to Admin Login: {target_login_url}...")
    await page.goto(
        target_login_url,
        wait_until="domcontentloaded",
        timeout=TIMEOUT,
    )

    username_input = page.locator("#username, input[name='username']").first
    password_input = page.locator("#password, input[name='password']").first
    login_button = page.locator('button.btn-login-primary, button[type="submit"], input[type="submit"]').first

    # Wait for login inputs
    await username_input.wait_for(state="visible", timeout=15000)
    await password_input.wait_for(state="visible", timeout=15000)

    # Fill credentials
    await username_input.fill(target_username)
    await password_input.fill(target_password)

    # Submit login
    await login_button.click()

    # Wait for post-login redirect
    try:
        if target_pattern:
            await page.wait_for_url(target_pattern, timeout=20000)
        else:
            await page.wait_for_url("**/admin/**", timeout=20000)
    except Exception:
        # Fallback wait for admin header or navigation sidebar
        try:
            await page.wait_for_selector(".navbar, .sidebar, .vertical-menu, .page-title-box, #sidebar-menu", timeout=10000)
        except Exception:
            pass

    # Verify session is not on login
    if await is_admin_session_expired(page):
        raise RuntimeError(f"Admin authentication failed or redirected back to login: {page.url}")

    print(f"Admin authentication successful. Landed on: {page.url}")


async def create_authenticated_admin_context(
    browser: Browser,
    auth_state_path: Path = None,
    viewport: dict = None,
    admin_base_url: str = None,
    admin_login_url: str = None,
    username: str = None,
    password: str = None,
    post_login_url_pattern: str = None,
) -> BrowserContext:
    """
    Create a Playwright BrowserContext with authenticated admin session.
    Reuses existing storage state from auth_state_admin.json when valid,
    otherwise performs fresh login and saves storage state.
    Configures context with the requested viewport size.
    """
    target_base_url = admin_base_url or BASELINE_ADMIN_BASE_URL
    target_login_url = admin_login_url or BASELINE_ADMIN_LOGIN_URL
    effective_viewport = viewport or VIEWPORTS.get(DEFAULT_VIEWPORT, {"width": 1280, "height": 800})
    target_auth_state = Path(auth_state_path) if auth_state_path else (
        LIVE_ADMIN_AUTH_STATE if (admin_base_url and admin_base_url.rstrip("/") == LIVE_ADMIN_BASE_URL.rstrip("/") and LIVE_ADMIN_BASE_URL.rstrip("/") != BASELINE_ADMIN_BASE_URL.rstrip()) else BASELINE_ADMIN_AUTH_STATE
    )

    if target_auth_state.exists():
        print(f"Loading existing admin authentication state from: {target_auth_state}")
        try:
            context = await browser.new_context(
                storage_state=str(target_auth_state),
                viewport=effective_viewport,
            )
            test_page = await context.new_page()

            # Verify session validity on target admin base URL
            response = await test_page.goto(
                target_base_url,
                wait_until="domcontentloaded",
                timeout=TIMEOUT,
            )

            # Settle potential redirect
            await test_page.wait_for_timeout(1500)

            if not await is_admin_session_expired(test_page):
                print(f"Existing admin session on {target_base_url} is valid.")
                await test_page.close()
                return context

            print(f"Admin session expired or invalidated for {target_base_url}. Re-authenticating...")
            await test_page.close()
            await context.close()
        except Exception as e:
            print(f"Admin auth state validation failed ({e}). Creating fresh session...")

    # Perform fresh login
    print("Initiating fresh admin login...")
    context = await browser.new_context(viewport=effective_viewport)
    page = await context.new_page()

    await login_admin(
        page=page,
        username=username,
        password=password,
        login_url=target_login_url,
        post_login_url_pattern=post_login_url_pattern,
    )

    # Save fresh authentication state
    target_auth_state.parent.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(target_auth_state))
    print(f"Saved fresh admin authentication state to: {target_auth_state}")

    await page.close()
    return context



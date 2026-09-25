"""
Trade Terminal Login Behavioral & Authentication Persistence Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Complete validation of login form elements, placeholders, and labels from HTML.
2. Successful authentication with valid credentials and redirection from /login/ to /dashboard/.
3. Saving and persisting authentication storage state (auth/auth_state_trade.json).
4. Direct session resumption on /dashboard/ using the saved auth state.
5. Rejection of invalid credentials without redirecting to dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import Browser, expect

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_has_text,
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.login_page import TradeLoginPage


@pytest.mark.trade
@pytest.mark.smoke
def test_trade_login_form_elements_displayed(trade_login_page: TradeLoginPage):
    """
    Verify that the Trade Terminal login form renders all required inputs,
    labels, placeholders, toggles, checkboxes, links, and action buttons
    per the login form HTML specifications.
    """
    # 1. Navigate to login endpoint
    trade_login_page.navigate()

    # 2. Form container
    assert_element_is_visible(
        trade_login_page.login_form,
        element_name="Login Form (#register.xn-login-form)",
    )

    # 3. Email / Account ID field & label
    assert_element_is_visible(
        trade_login_page.email_input,
        element_name="Email / Account ID Input (#email)",
    )
    assert_element_is_visible(
        trade_login_page.email_label,
        element_name="Email Label",
    )
    assert_element_has_text(
        trade_login_page.email_label,
        expected_text="Email or Account ID",
        element_name="Email Label",
    )
    expect(trade_login_page.email_input).to_have_attribute("placeholder", "you@example.com")
    expect(trade_login_page.email_input).to_have_attribute("name", "email")

    # 4. Password field, label & toggle icon
    assert_element_is_visible(
        trade_login_page.password_input,
        element_name="Password Input (#password)",
    )
    assert_element_is_visible(
        trade_login_page.password_label,
        element_name="Password Label",
    )
    assert_element_has_text(
        trade_login_page.password_label,
        expected_text="Password",
        element_name="Password Label",
    )
    expect(trade_login_page.password_input).to_have_attribute("placeholder", "••••••••")
    expect(trade_login_page.password_input).to_have_attribute("name", "password")
    assert_element_is_visible(
        trade_login_page.password_toggle,
        element_name="Password Visibility Toggle (.toggle-password)",
    )

    # 5. Remember Me checkbox & label
    assert_element_is_visible(
        trade_login_page.remember_me_checkbox,
        element_name="Remember Me Checkbox (#inputCheckbox)",
    )
    assert_element_is_visible(
        trade_login_page.remember_me_label,
        element_name="Remember Me Label",
    )
    assert_element_has_text(
        trade_login_page.remember_me_label,
        expected_text="Remember me",
        element_name="Remember Me Label",
    )
    expect(trade_login_page.remember_me_checkbox).to_have_attribute("name", "remember")

    # 6. Forgot Password link
    assert_element_is_visible(
        trade_login_page.forgot_password_link,
        element_name="Forgot Password Link (a.xn-forgot)",
    )
    assert_element_has_text(
        trade_login_page.forgot_password_link,
        expected_text="Forgot password?",
        element_name="Forgot Password Link",
    )
    expect(trade_login_page.forgot_password_link).to_have_attribute("href", "../reset/")

    # 7. Login Submit button
    assert_element_is_visible(
        trade_login_page.login_button,
        element_name="Login Submit Button (button.xn-btn-login)",
    )
    assert_element_has_text(
        trade_login_page.login_button,
        expected_text="Login",
        element_name="Login Button Text",
    )
    expect(trade_login_page.login_button).to_have_attribute("type", "submit")

    # 8. Hidden profile data element
    expect(trade_login_page.profile_data_hidden).to_have_count(1)


@pytest.mark.trade
@pytest.mark.smoke
@pytest.mark.regression
def test_trader_can_login_and_redirect_to_dashboard(trade_login_page: TradeLoginPage):
    """
    Verify that a trader with valid credentials can log in from https://stage.xtremenext.com/login/,
    be successfully redirected to https://stage.xtremenext.com/dashboard/,
    and persist the resulting authentication session state to auth/auth_state_trade.json.
    """
    # 1. Start at Trade Terminal login URL
    trade_login_page.navigate()
    assert_url_contains(trade_login_page.page, "/login", timeout=15000)

    # 2. Execute login with configured credentials
    dashboard_url = trade_login_page.login_and_wait_for_dashboard(
        username=settings.trade_terminal.username,
        password=settings.trade_terminal.password,
        remember_me=True,
        timeout=30000,
    )

    # 3. Assert redirection to dashboard
    assert_url_contains(trade_login_page.page, "/dashboard", timeout=15000)
    assert "dashboard" in dashboard_url.lower(), (
        f"Expected final URL to contain '/dashboard', but got '{dashboard_url}'."
    )

    # 4. Save and persist authentication state
    auth_file_path = trade_login_page.save_auth_state()

    # 5. Validate saved storage state file on disk
    assert auth_file_path.exists(), (
        f"Expected auth state file at '{auth_file_path}' to exist after login."
    )
    assert auth_file_path.stat().st_size > 0, (
        f"Expected auth state file at '{auth_file_path}' to be non-empty."
    )

    with open(auth_file_path, "r", encoding="utf-8") as f:
        auth_data = json.load(f)

    assert "cookies" in auth_data, "Auth state JSON missing 'cookies' field."
    assert len(auth_data["cookies"]) > 0, "Auth state JSON contains zero cookies."


@pytest.mark.trade
@pytest.mark.regression
def test_saved_auth_allows_direct_dashboard_access(workflow_browser: Browser):
    """
    Verify that the saved auth state (auth_state_trade.json) enables resuming
    an active session and navigating directly to https://stage.xtremenext.com/dashboard/
    without repeating manual login interactions.
    """
    auth_state_file = settings.trade_terminal.auth_state_path

    # Ensure auth state exists before testing session reuse
    if not auth_state_file.exists() or auth_state_file.stat().st_size == 0:
        pytest.skip(f"Auth state file '{auth_state_file}' not found. Run test_trader_can_login first.")

    # Create new isolated context with saved storage state
    context = workflow_browser.new_context(
        storage_state=str(auth_state_file),
        viewport=settings.browser.viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()

    try:
        dashboard_target = f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
        page.goto(dashboard_target, wait_until="domcontentloaded", timeout=30000)

        # Assert user stays on dashboard and is not redirected to login
        assert_url_contains(page, "/dashboard", timeout=15000)
        assert "/login" not in page.url, (
            f"Expected session to remain on dashboard, but redirected to '{page.url}'."
        )
    finally:
        context.close()


@pytest.mark.trade
@pytest.mark.regression
def test_trader_cannot_login_with_invalid_credentials(trade_login_page: TradeLoginPage):
    """
    Verify that attempting to log in with an incorrect password prevents
    redirection to the dashboard and retains the user on the login screen.
    """
    trade_login_page.navigate()
    assert_url_contains(trade_login_page.page, "/login", timeout=15000)

    # Submit with invalid password
    trade_login_page.login(
        username=settings.trade_terminal.username,
        password="WrongPassword999!#",
        remember_me=False,
    )

    # Give brief time for network response
    trade_login_page.page.wait_for_timeout(2500)

    # Assert URL does NOT redirect to dashboard
    assert "/dashboard" not in trade_login_page.page.url, (
        f"Expected user to remain on login page after invalid credentials, but got '{trade_login_page.page.url}'."
    )
    assert "/login" in trade_login_page.page.url, (
        f"Expected URL to still be /login/, but got '{trade_login_page.page.url}'."
    )


@pytest.mark.trade
@pytest.mark.regression
def test_trade_login_runtime_network_and_console_clean(trade_login_page: TradeLoginPage):
    """
    Verify that the Trade Terminal login page operates cleanly without hidden defects:
    - Zero JavaScript runtime exceptions or unhandled page errors.
    - Zero console error logs.
    - Zero failed network requests.
    - Zero HTTP 4xx or 5xx responses.
    """
    trade_login_page.navigate()
    assert_url_contains(trade_login_page.page, "/login", timeout=15000)

    # Assert completely clean diagnostics telemetry on login page
    trade_login_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
    )

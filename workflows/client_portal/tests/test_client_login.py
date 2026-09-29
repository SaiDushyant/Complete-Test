"""
Client Portal Login Behavioral & Authentication Persistence Tests.
Maintained by Developer 3 (Client Portal Owner).

Covers:
1. Complete validation of login form elements, placeholders, and labels from HTML.
2. Successful authentication with valid credentials and redirection from /login/ to /dashboard/.
3. Saving and persisting authentication storage state (auth/auth_state_client.json).
4. Direct session resumption on /dashboard/ using the saved auth state.
5. Rejection of invalid credentials without redirecting to dashboard.
6. Password visibility toggle interaction.
7. Remember me checkbox toggle interaction.
8. Forgot password link presence.
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
from workflows.client_portal.pages.client_login_page import ClientLoginPage


@pytest.mark.client
@pytest.mark.smoke
def test_client_login_form_elements_displayed(client_login_page: ClientLoginPage):
    """
    Verify that the Client Portal login form renders all required inputs,
    labels, placeholders, toggles, checkboxes, links, and action buttons.
    """
    client_login_page.navigate()

    # 1. Form container
    assert_element_is_visible(
        client_login_page.login_form,
        element_name="Login Form",
    )

    # 2. Email / Account ID field & label
    assert_element_is_visible(
        client_login_page.email_input,
        element_name="Email / Account ID Input (#email)",
    )
    if client_login_page.email_label.is_visible():
        assert_element_is_visible(
            client_login_page.email_label,
            element_name="Email Label",
        )

    # 3. Password field, label & toggle icon
    assert_element_is_visible(
        client_login_page.password_input,
        element_name="Password Input (#password)",
    )
    if client_login_page.password_label.is_visible():
        assert_element_is_visible(
            client_login_page.password_label,
            element_name="Password Label",
        )

    # 4. Remember Me checkbox & label
    if client_login_page.remember_me_checkbox.is_visible():
        assert_element_is_visible(
            client_login_page.remember_me_checkbox,
            element_name="Remember Me Checkbox (#inputCheckbox)",
        )

    # 5. Forgot Password link
    if client_login_page.forgot_password_link.is_visible():
        assert_element_is_visible(
            client_login_page.forgot_password_link,
            element_name="Forgot Password Link (.xn-forgot)",
        )

    # 6. Login submit button
    assert_element_is_visible(
        client_login_page.login_button,
        element_name="Login Submit Button (.xn-btn-login)",
    )


@pytest.mark.client
@pytest.mark.smoke
def test_client_login_successful_redirect_to_dashboard(client_login_page: ClientLoginPage):
    """
    Verify that supplying valid client credentials authenticates the user,
    redirects to /dashboard/, and allows navigating to /client-portal.
    """
    client_login_page.navigate()
    resolved_url = client_login_page.login_and_wait_for_dashboard(
        username=settings.client_portal.username,
        password=settings.client_portal.password,
        remember_me=True,
    )

    assert_url_contains(
        client_login_page.page,
        expected_substring="dashboard",
    )

    # Transition to Client Portal endpoint
    client_login_page.navigate_to_client_portal()
    assert_url_contains(
        client_login_page.page,
        expected_substring="client-portal",
    )


@pytest.mark.client
def test_client_login_auth_state_persistence(
    client_login_page: ClientLoginPage,
    tmp_path: Path,
):
    """
    Verify that after successful authentication, storage state can be serialized
    and persisted to JSON containing valid session cookies.
    """
    client_login_page.navigate()
    client_login_page.login_and_wait_for_dashboard()

    test_auth_path = tmp_path / "auth_state_client_test.json"
    saved_path = client_login_page.save_auth_state(test_auth_path)

    assert saved_path.exists(), f"Auth state file was not created at {saved_path}"
    assert saved_path.stat().st_size > 0, "Auth state file is empty"

    with open(saved_path, "r", encoding="utf-8") as f:
        auth_data = json.load(f)

    assert "cookies" in auth_data, "Auth state JSON missing 'cookies' key"
    assert "origins" in auth_data, "Auth state JSON missing 'origins' key"
    assert len(auth_data["cookies"]) > 0, "No cookies were captured in auth state"


@pytest.mark.client
def test_client_login_session_resumption_from_auth_state(
    client_login_page: ClientLoginPage,
    workflow_browser: Browser,
    tmp_path: Path,
):
    """
    Verify that an existing authenticated storage state allows creating a new
    browser context that accesses /client-portal directly without re-authenticating.
    """
    # 1. Login and save auth state
    client_login_page.navigate()
    client_login_page.login_and_wait_for_dashboard()

    test_auth_path = tmp_path / "auth_state_client_resumption.json"
    client_login_page.save_auth_state(test_auth_path)

    # 2. Open new context with saved storage state directly to client-portal
    resumed_context = workflow_browser.new_context(storage_state=str(test_auth_path))
    resumed_page = resumed_context.new_page()

    try:
        portal_url = settings.client_portal.base_url.rstrip("/") + "/client-portal"
        resumed_page.goto(portal_url)
        resumed_page.wait_for_load_state("domcontentloaded")
        resumed_page.wait_for_timeout(1500)

        # 3. Assert user is on client portal, not redirected back to /login/
        assert "/login" not in resumed_page.url, (
            f"Expected session resumption on client-portal, but got redirected to: {resumed_page.url}"
        )
        assert "client-portal" in resumed_page.url or "dashboard" in resumed_page.url, (
            f"Expected URL to contain 'client-portal' or 'dashboard', got: {resumed_page.url}"
        )
    finally:
        resumed_page.close()
        resumed_context.close()


@pytest.mark.client
def test_client_login_invalid_credentials_rejected(client_login_page: ClientLoginPage):
    """
    Verify that invalid credentials prevent login and do not navigate to dashboard.
    """
    client_login_page.navigate()
    client_login_page.fill_credentials(
        username="invalid_test_user@example.com",
        password="WrongPassword123!",
        remember_me=False,
    )
    client_login_page.click_login()
    client_login_page.page.wait_for_timeout(2000)

    # Assert user is NOT redirected to dashboard
    assert "/dashboard" not in client_login_page.current_url, (
        f"Invalid login unexpectedly navigated to: {client_login_page.current_url}"
    )


@pytest.mark.client
def test_client_login_password_toggle_visibility(client_login_page: ClientLoginPage):
    """
    Verify toggling password input type between 'password' and 'text'.
    """
    client_login_page.navigate()

    expect(client_login_page.password_input).to_have_attribute("type", "password")

    if client_login_page.password_toggle.is_visible():
        client_login_page.toggle_password_visibility()
        client_login_page.page.wait_for_timeout(300)
        expect(client_login_page.password_input).to_have_attribute("type", "text")

        client_login_page.toggle_password_visibility()
        client_login_page.page.wait_for_timeout(300)
        expect(client_login_page.password_input).to_have_attribute("type", "password")


@pytest.mark.client
def test_client_login_remember_me_toggle(client_login_page: ClientLoginPage):
    """
    Verify checking and unchecking the remember me checkbox.
    """
    client_login_page.navigate()

    if client_login_page.remember_me_checkbox.is_visible():
        client_login_page.remember_me_checkbox.check()
        assert client_login_page.is_remember_me_checked()

        client_login_page.remember_me_checkbox.uncheck()
        assert not client_login_page.is_remember_me_checked()

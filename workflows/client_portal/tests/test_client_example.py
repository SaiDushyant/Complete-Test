"""
Client Portal Workflow Example Test.
Demonstrates fixture injection, Page Object usage, assertion conventions, and error monitoring.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import pytest

from config.settings import settings
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_login_page_renders_form_elements(
    client_login_page: ClientLoginPage,
    client_page,
):
    """
    Verify that the Client Portal login page displays the email and password fields.
    Asserts zero uncaught JS errors on public login interface.
    """
    client_login_page.navigate()

    assert client_login_page.is_login_page_displayed(), (
        f"Expected Client login page at '{settings.client_portal.login_url}' to render credentials form."
    )

    if hasattr(client_page, "error_monitor"):
        client_page.error_monitor.assert_no_errors("Login Page Render")


@pytest.mark.client
@pytest.mark.regression
def test_client_can_view_account_dashboard(
    client_dashboard_page: ClientDashboardPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that an authenticated client can access their user dashboard.
    Demonstrates authenticated fixture usage without repeating client login steps.
    Asserts zero console errors, JS page crashes, and backend failures.
    """
    client_dashboard_page.navigate()

    assert client_dashboard_page.is_dashboard_displayed(), (
        f"Expected Client Dashboard at '{settings.client_portal.base_url}' to display main workspace."
    )

    client_error_monitor.assert_no_errors("Dashboard View")

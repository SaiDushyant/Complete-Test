"""
Client Portal Workflow Example Test (Template).
Demonstrates fixture injection, Page Object usage, assertion conventions, and markers.
Maintained by Developer 3 (Client Portal Owner).

NOTE: This is an architectural template/example showing how new behavioral tests
should be structured. When implementing real workflows, replace the mock/TODO steps.
"""

import pytest

from config.settings import settings
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)


@pytest.mark.client
@pytest.mark.smoke
def test_client_login_page_renders_form_elements(client_login_page: ClientLoginPage):
    """
    Verify that the Client Portal login page displays the email and password fields.
    """
    client_login_page.navigate()

    assert client_login_page.is_login_page_displayed(), (
        f"Expected Client login page at '{settings.client_portal.login_url}' to render credentials form."
    )


@pytest.mark.client
@pytest.mark.regression
def test_client_can_view_account_dashboard(client_dashboard_page: ClientDashboardPage):
    """
    Verify that an authenticated client can access their user dashboard.
    Demonstrates authenticated fixture usage without repeating client login steps.
    """
    client_dashboard_page.navigate()

    assert client_dashboard_page.is_dashboard_displayed(), (
        f"Expected Client Dashboard at '{settings.client_portal.base_url}' to display main workspace."
    )

    # TODO (Developer 3): Add specific client workflows (e.g. KYC document upload, deposit request, profile update)

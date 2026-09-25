"""
Admin Portal Workflow Example Test (Template).
Demonstrates fixture injection, Page Object usage, assertion conventions, and markers.
Maintained by Developer 2 (Admin Portal Owner).

NOTE: This is an architectural template/example showing how new behavioral tests
should be structured. When implementing real workflows, replace the mock/TODO steps.
"""

import pytest

from config.settings import settings
from workflows.admin_portal.pages.admin_dashboard_page import AdminDashboardPage
from workflows.admin_portal.pages.admin_login_page import AdminLoginPage
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_login_page_renders_form_elements(admin_login_page: AdminLoginPage):
    """
    Verify that the Admin login page displays the admin username and password fields.
    """
    admin_login_page.navigate()

    assert admin_login_page.is_login_page_displayed(), (
        f"Expected Admin login page at '{settings.admin_portal.login_url}' to render credentials form."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_can_view_management_dashboard(admin_dashboard_page: AdminDashboardPage):
    """
    Verify that an authenticated administrator can access the Admin Console workspace.
    Demonstrates authenticated fixture usage without repeating admin login steps.
    """
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.is_dashboard_displayed(), (
        f"Expected Admin Dashboard at '{settings.admin_portal.base_url}' to render navigation or widgets."
    )

    # TODO (Developer 2): Add specific admin workflow steps (e.g. user creation, role assignment, audit logs)

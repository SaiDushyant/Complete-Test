import pytest

from workflows.admin_portal.pages.admin_dashboard_page import (
    AdminDashboardPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_profile_menu_shows_admin_details(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the profile menu shows the admin details."""
    admin_dashboard_page.navigate()
    admin_dashboard_page.open_profile_menu()

    assert admin_dashboard_page.profile_menu.is_visible()
    assert admin_dashboard_page.profile_name.inner_text() == "madmin"
    assert admin_dashboard_page.profile_role.inner_text() == (
        "Administrator"
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_profile_menu_has_logout_link(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the profile menu contains Logout."""
    admin_dashboard_page.navigate()
    admin_dashboard_page.open_profile_menu()

    assert admin_dashboard_page.logout_link.is_visible()

    logout_url = (
        admin_dashboard_page.logout_link.get_attribute("href")
        or ""
    )

    assert "/admin/Controlbase/Logout" in logout_url


@pytest.mark.admin
@pytest.mark.regression
def test_admin_theme_toggle_is_visible(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the theme toggle is visible."""
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.theme_toggle.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_notifications_are_available(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the notification controls are visible."""
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.notification_button.is_visible()
    assert admin_dashboard_page.notification_count.is_visible()

    admin_dashboard_page.notification_button.click()

    assert admin_dashboard_page.notification_menu.is_visible()
    assert admin_dashboard_page.mark_all_read.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_sidebar_menu_button_is_visible(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the sidebar menu button is visible."""
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.menu_button.is_visible()
"""
Admin Portal Shared Components Test Suite.
Consolidates topbar, theme toggle, notifications dropdown, profile menu,
and sidebar toggle tests across Admin Portal routes into clean parameterized tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent

ADMIN_REPRESENTATIVE_PAGES = [
    "/admin/Controlbase/Dashboard",
    "/admin/Controlbase/user",
    "/admin/Controlbase/deposit",
    "/admin/Controlbase/withdraw",
    "/admin/Controlbase/order/open",
    "/admin/Controlbase/cronJobs",
    "/admin/Controlbase/settings",
]


def _build_full_url(page_path: str) -> str:
    base = settings.admin_portal.base_url.split("/admin")[0]
    return f"{base}{page_path}"


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.parametrize("page_path", ADMIN_REPRESENTATIVE_PAGES)
def test_admin_shared_topbar_elements(
    authenticated_admin_page: Page,
    page_path: str,
):
    """Verify topbar branding, hamburger button, theme toggle, and notification bell."""
    url = _build_full_url(page_path)
    authenticated_admin_page.goto(url, wait_until="domcontentloaded")
    topbar = AdminTopbarComponent(authenticated_admin_page)

    expect(topbar.topbar).to_be_visible(timeout=10000)
    expect(topbar.menu_toggle_btn).to_be_visible()
    expect(topbar.theme_toggle_btn).to_be_visible()
    expect(topbar.notifications_btn).to_be_visible()
    expect(topbar.user_dropdown_btn).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("page_path", ADMIN_REPRESENTATIVE_PAGES)
def test_admin_shared_theme_toggle_switches_modes(
    authenticated_admin_page: Page,
    page_path: str,
):
    """Verify theme switcher toggles between dark and light modes cleanly."""
    url = _build_full_url(page_path)
    authenticated_admin_page.goto(url, wait_until="domcontentloaded")
    topbar = AdminTopbarComponent(authenticated_admin_page)

    initial_mode = topbar.get_layout_mode()
    new_mode = topbar.toggle_theme()
    assert new_mode != initial_mode, f"Expected theme mode to switch from {initial_mode}."

    # Toggle back to restore original mode
    reverted_mode = topbar.toggle_theme()
    assert reverted_mode == initial_mode


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("page_path", ADMIN_REPRESENTATIVE_PAGES)
def test_admin_shared_notifications_dropdown(
    authenticated_admin_page: Page,
    page_path: str,
):
    """Verify notifications bell opens dropdown with header and 'Mark all read' action."""
    url = _build_full_url(page_path)
    authenticated_admin_page.goto(url, wait_until="domcontentloaded")
    topbar = AdminTopbarComponent(authenticated_admin_page)

    topbar.open_notifications()
    expect(topbar.notifications_dropdown).to_be_visible()
    expect(topbar.mark_all_read_btn).to_be_visible()

    topbar.close_notifications()
    expect(topbar.notifications_dropdown).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("page_path", ADMIN_REPRESENTATIVE_PAGES)
def test_admin_shared_profile_dropdown_and_logout(
    authenticated_admin_page: Page,
    page_path: str,
):
    """Verify user profile dropdown expands and displays logout item."""
    url = _build_full_url(page_path)
    authenticated_admin_page.goto(url, wait_until="domcontentloaded")
    topbar = AdminTopbarComponent(authenticated_admin_page)

    topbar.open_user_menu()
    expect(topbar.logout_item).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("page_path", ADMIN_REPRESENTATIVE_PAGES)
def test_admin_shared_sidebar_toggle_action(
    authenticated_admin_page: Page,
    page_path: str,
):
    """Verify sidebar menu hamburger button toggles navigation layout width."""
    url = _build_full_url(page_path)
    authenticated_admin_page.goto(url, wait_until="domcontentloaded")
    sidebar = AdminSidebarComponent(authenticated_admin_page)

    expect(sidebar.menu_toggle_btn).to_be_visible()

    initial_size = authenticated_admin_page.evaluate("() => document.body.getAttribute('data-sidebar-size') || ''")
    sidebar.menu_toggle_btn.click()
    authenticated_admin_page.wait_for_timeout(300)

    toggled_size = authenticated_admin_page.evaluate("() => document.body.getAttribute('data-sidebar-size') || ''")
    assert toggled_size != initial_size or authenticated_admin_page.evaluate("() => document.body.classList.contains('sidebar-enable')")

    # Toggle back
    sidebar.menu_toggle_btn.click()
    authenticated_admin_page.wait_for_timeout(300)

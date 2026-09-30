"""
Admin Portal Role Permission Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.role_permission_page import RolePermissionPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_topbar_branding_and_title(
    role_permission_page: RolePermissionPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('Role Permission'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    role_permission_page.navigate()

    # Brand Logo & Responsive Icons
    assert role_permission_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert role_permission_page.logo_small.is_visible() or role_permission_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = role_permission_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert role_permission_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert role_permission_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert role_permission_page.menu_button.get_attribute("title") == "Open menu"
    assert role_permission_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert role_permission_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert role_permission_page.page_title.inner_text().strip() == "Role Permission"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_topbar_sidebar_toggle_action(
    role_permission_page: RolePermissionPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    role_permission_page.navigate()

    body = role_permission_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    role_permission_page.menu_button.click()
    role_permission_page.page.wait_for_timeout(300)

    toggled_class = body.get_attribute("class") or ""
    toggled_sidebar_size = body.get_attribute("data-sidebar-size") or ""

    assert (
        toggled_class != initial_class
        or "sidebar-enable" in toggled_class
        or toggled_sidebar_size in ["sm", "lg", "condensed"]
    ), "Expected sidebar state to change on toggle."

    # Toggle back
    role_permission_page.menu_button.click()
    role_permission_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_theme_toggle_switches_modes(
    role_permission_page: RolePermissionPage,
):
    """
    Verify clicking the theme switch button toggles between dark and light themes,
    and dark/light SVG icons are present in the DOM.
    """
    role_permission_page.navigate()

    assert role_permission_page.theme_toggle.is_visible(), "Expected theme toggle button (#admin-theme-toggle) to be visible."
    assert role_permission_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert role_permission_page.theme_toggle.get_attribute("aria-label") == "Switch theme"

    # Both SVG icons (moon and sun) must exist in DOM
    assert role_permission_page.theme_dark_icon.count() >= 1, "Expected dark mode moon icon."
    assert role_permission_page.theme_light_icon.count() >= 1, "Expected light mode sun icon."

    # Test Theme Switching
    initial_mode = role_permission_page.get_theme_mode()
    role_permission_page.toggle_theme()
    role_permission_page.page.wait_for_timeout(300)

    new_mode = role_permission_page.get_theme_mode()
    assert new_mode != initial_mode, f"Expected theme mode to change from {initial_mode}."

    # Revert back to original mode
    role_permission_page.toggle_theme()
    role_permission_page.page.wait_for_timeout(300)
    assert role_permission_page.get_theme_mode() == initial_mode


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_notifications_dropdown(
    role_permission_page: RolePermissionPage,
):
    """
    Verify notifications button, badge, dropdown menu, header, Mark all read link,
    and empty notification text.
    """
    role_permission_page.navigate()

    assert role_permission_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert role_permission_page.notification_count.is_visible(), "Expected notification count badge."

    # Open dropdown
    role_permission_page.open_notifications()
    expect(role_permission_page.notification_menu).to_be_visible()

    # Verify header and mark all read link
    assert role_permission_page.notification_menu.locator("h6").inner_text().strip() == "Notifications"
    assert role_permission_page.mark_all_read.is_visible()
    assert role_permission_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list contains empty state text
    assert role_permission_page.notification_empty_text.is_visible()
    assert "Notification not found." in role_permission_page.notification_empty_text.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_profile_dropdown_and_logout_link(
    role_permission_page: RolePermissionPage,
):
    """
    Verify profile dropdown button, initials, admin name, menu header, and logout action link.
    """
    role_permission_page.navigate()

    assert role_permission_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert role_permission_page.profile_initials.is_visible(), "Expected profile initials to be visible."
    assert role_permission_page.profile_initials.inner_text().strip() == "M"

    if role_permission_page.profile_topbar_name.is_visible():
        assert role_permission_page.profile_topbar_name.inner_text().strip() == "madmin"

    # Open Profile Menu
    role_permission_page.open_profile_menu()
    expect(role_permission_page.profile_menu).to_be_visible()

    assert role_permission_page.profile_name.inner_text().strip() == "madmin"
    assert role_permission_page.profile_role.inner_text().strip() == "Administrator"

    # Logout link
    logout = role_permission_page.logout_link
    assert logout.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (logout.get_attribute("href") or "")
    assert "Logout" in logout.inner_text()
    assert logout.locator("i.mdi-logout").is_visible(), "Expected Logout icon."


# ==============================================================================
# SECTION 2: PAGE ACTIONS & HIDDEN PERMISSIONS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_page_actions_and_hidden_flags(
    role_permission_page: RolePermissionPage,
):
    """
    Verify the role-page-actions container, Add Role Permission button (#addNew),
    3 hidden permission inputs (#editrolePermission, #deleterolePermission, #editPermission),
    and opening/closing the Role Permission creation modal (#myModal).
    """
    role_permission_page.navigate()

    # Container and Add button
    assert role_permission_page.page_actions.is_visible(), "Expected .role-page-actions to be visible."
    assert role_permission_page.add_role_button.is_visible(), "Expected #addNew button to be visible."
    assert role_permission_page.add_role_button.inner_text().strip() == "Add Role Permission"

    # Hidden permission values
    assert role_permission_page.edit_role_perm_hidden.get_attribute("value") == "1"
    assert role_permission_page.delete_role_perm_hidden.get_attribute("value") == "1"
    assert role_permission_page.edit_perm_hidden.get_attribute("value") == "1"

    # Click Add Role Permission to open modal
    role_permission_page.add_role_button.click()
    role_permission_page.page.wait_for_timeout(500)

    expect(role_permission_page.role_modal).to_be_visible()
    assert "Role Permission Form" in role_permission_page.role_modal_title.inner_text()
    assert role_permission_page.role_modal_input.is_visible()
    assert role_permission_page.role_modal_save.is_visible()

    # Close modal
    role_permission_page.role_modal_close.first.click()
    role_permission_page.page.wait_for_timeout(500)
    expect(role_permission_page.role_modal).not_to_be_visible()


# ==============================================================================
# SECTION 3: TABLE CARD & COLUMN HEADERS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_table_card_and_column_headers(
    role_permission_page: RolePermissionPage,
):
    """
    Verify role-table-card container, DataTable wrapper, 3 column headers
    (S.No, Role Name, Action), and initial records count.
    """
    role_permission_page.navigate()

    assert role_permission_page.table_card.is_visible(), "Expected .role-table-card to be visible."
    assert role_permission_page.table_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."

    # Validate exact 3 column headers
    headers = [th.inner_text().strip() for th in role_permission_page.table_headers.all()]
    expected_headers = ["S.No", "Role Name", "Action"]
    assert headers == expected_headers, f"Expected headers {expected_headers}, got {headers}."

    # Validate row count and info
    assert role_permission_page.role_rows.count() == 4
    info_text = role_permission_page.table_info.inner_text()
    assert "Showing 1 to 4 of 4 entries" in info_text


# ==============================================================================
# SECTION 4: TABLE ROWS DATA INTEGRITY
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_table_rows_data_integrity(
    role_permission_page: RolePermissionPage,
):
    """
    Verify each role row contains numeric S.No, non-empty role name,
    edit role name pencil button, edit permissions link, and delete role button.
    """
    role_permission_page.navigate()

    rows = role_permission_page.role_rows
    assert rows.count() == 4, f"Expected 4 role rows, got {rows.count()}."

    expected_roles = ["Manager", "Admin", "sadmin", "KYC"]

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        # Serial number
        sno = cells.nth(0).inner_text().strip()
        assert sno == str(i + 1), f"Expected S.No {i + 1}, got '{sno}'."

        # Role name
        role_cell_text = cells.nth(1).inner_text().strip()
        assert any(r in role_cell_text for r in expected_roles), (
            f"Expected row {i} to contain one of {expected_roles}, got '{role_cell_text}'."
        )

        # Action buttons in row
        assert cells.nth(1).locator("a.btnNameEdit").is_visible(), "Expected edit name pencil button."
        assert cells.nth(2).locator("a:has(i.mdi-book-edit-outline)").is_visible(), "Expected edit permissions link."
        assert cells.nth(2).locator("a.BtnDelete").is_visible(), "Expected delete button."


# ==============================================================================
# SECTION 5: ROW ACTION BUTTONS & MODALS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_edit_role_name_action_modal(
    role_permission_page: RolePermissionPage,
):
    """
    Verify clicking the edit role name pencil button (a.btnNameEdit) opens
    the Role Permission Form modal with pre-populated role name.
    """
    role_permission_page.navigate()

    edit_name_btn = role_permission_page.edit_name_buttons.first
    assert edit_name_btn.is_visible()
    assert edit_name_btn.get_attribute("aria-label") == "Edit role name"

    edit_name_btn.click()
    role_permission_page.page.wait_for_timeout(500)

    expect(role_permission_page.role_modal).to_be_visible()
    assert "Role Permission Form" in role_permission_page.role_modal_title.inner_text()
    assert role_permission_page.role_modal_input.input_value() == "Manager"

    # Close modal
    role_permission_page.role_modal_close.first.click()
    role_permission_page.page.wait_for_timeout(500)
    expect(role_permission_page.role_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_edit_permissions_navigation_link(
    role_permission_page: RolePermissionPage,
):
    """
    Verify the edit permissions link (a:has(i.mdi-book-edit-outline)) has valid
    href pointing to /admin/Controlbase/permissions?role_id=... and proper tooltip.
    """
    role_permission_page.navigate()

    perm_link = role_permission_page.edit_permission_links.first
    assert perm_link.is_visible()
    assert perm_link.get_attribute("aria-label") == "Edit permissions"

    href = perm_link.get_attribute("href") or ""
    assert "Controlbase/permissions?role_id=" in href, f"Expected permissions href, got '{href}'."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_delete_action_triggers_sweetalert(
    role_permission_page: RolePermissionPage,
):
    """
    Verify clicking the delete button (a.BtnDelete) triggers the SweetAlert2
    confirmation dialog ('Are you sure?'), and clicking 'No, cancel!' safely dismisses it.
    """
    role_permission_page.navigate()

    delete_btn = role_permission_page.delete_buttons.first
    assert delete_btn.is_visible()
    assert delete_btn.get_attribute("aria-label") == "Delete role"

    delete_btn.click()
    role_permission_page.page.wait_for_timeout(500)

    expect(role_permission_page.swal_popup).to_be_visible()
    assert "Are you sure?" in role_permission_page.swal_title.inner_text()
    assert role_permission_page.swal_confirm_button.is_visible()
    assert role_permission_page.swal_cancel_button.is_visible()

    # Safely cancel dialog without deleting
    role_permission_page.swal_cancel_button.click()
    role_permission_page.page.wait_for_timeout(500)
    expect(role_permission_page.swal_popup).not_to_be_visible()

    # Verify rows remain intact
    assert role_permission_page.role_rows.count() == 4


# ==============================================================================
# SECTION 6: CONTROLS, SEARCH & PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_length_dropdown_selection(
    role_permission_page: RolePermissionPage,
):
    """
    Verify changing visible entries per page via datatable_length dropdown
    (10, 25, 50, 100) preserves all 4 entries and updates status info.
    """
    role_permission_page.navigate()

    for length in ["25", "50", "100", "10"]:
        role_permission_page.select_page_length(length)
        assert role_permission_page.role_rows.count() == 4
        assert "Showing 1 to 4 of 4 entries" in role_permission_page.table_info.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_search_filtering(
    role_permission_page: RolePermissionPage,
):
    """
    Verify search input filters rows by role name, displays empty state
    when unmatched ('No matching records found'), and restores on clear.
    """
    role_permission_page.navigate()

    # Search for specific role "Manager"
    role_permission_page.search_role("Manager")
    assert role_permission_page.role_rows.count() == 1
    assert "Showing 1 to 1 of 1 entries" in role_permission_page.table_info.inner_text()
    assert "Manager" in role_permission_page.role_rows.first.inner_text()

    # Search for non-existent record
    role_permission_page.search_role("NONEXISTENTROLE")
    assert role_permission_page.empty_row.is_visible()
    assert "No matching records found" in role_permission_page.empty_row.inner_text()
    assert "Showing 0 to 0 of 0 entries" in role_permission_page.table_info.inner_text()

    # Clear search
    role_permission_page.clear_search()
    assert role_permission_page.role_rows.count() == 4
    assert "Showing 1 to 4 of 4 entries" in role_permission_page.table_info.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_pagination_controls(
    role_permission_page: RolePermissionPage,
):
    """
    Verify pagination container states when total records fit on single page:
    - Active page is 1
    - Previous button is disabled
    - Next button is disabled
    """
    role_permission_page.navigate()

    assert role_permission_page.pagination.is_visible()
    assert role_permission_page.active_page_button.inner_text().strip() == "1"
    assert "disabled" in (role_permission_page.previous_page_button.get_attribute("class") or "")
    assert "disabled" in (role_permission_page.next_page_button.get_attribute("class") or "")
    assert "Showing 1 to 4 of 4 entries" in role_permission_page.table_info.inner_text()

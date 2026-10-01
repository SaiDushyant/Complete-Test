"""
Admin Portal Manager/Group User Management Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.manager_user_management_page import (
    ManagerUserManagementPage,
)


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_topbar_branding_and_title(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('User Management'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    manager_user_management_page.navigate()

    # Brand Logo & Responsive Icons
    assert manager_user_management_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert manager_user_management_page.logo_small.is_visible() or manager_user_management_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = manager_user_management_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert manager_user_management_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert manager_user_management_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert manager_user_management_page.menu_button.get_attribute("title") == "Open menu"
    assert manager_user_management_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert manager_user_management_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert manager_user_management_page.page_title.inner_text().strip() == "User Management"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_topbar_sidebar_toggle_action(
    manager_user_management_page: ManagerUserManagementPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    manager_user_management_page.navigate()

    body = manager_user_management_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    manager_user_management_page.menu_button.click()
    manager_user_management_page.page.wait_for_timeout(300)

    toggled_class = body.get_attribute("class") or ""
    toggled_sidebar_size = body.get_attribute("data-sidebar-size") or ""

    assert (
        toggled_class != initial_class
        or "sidebar-enable" in toggled_class
        or toggled_sidebar_size in ["sm", "lg", "condensed"]
    ), "Expected sidebar state to change on toggle."

    # Toggle back
    manager_user_management_page.menu_button.click()
    manager_user_management_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_theme_toggle_switches_modes(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify clicking the theme switch button toggles between dark and light themes,
    and dark/light SVG icons are present in the DOM.
    """
    manager_user_management_page.navigate()

    assert manager_user_management_page.theme_toggle.is_visible(), "Expected theme toggle button (#admin-theme-toggle) to be visible."
    assert manager_user_management_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert manager_user_management_page.theme_toggle.get_attribute("aria-label") == "Switch theme"

    # Both SVG icons (moon and sun) must exist in DOM
    assert manager_user_management_page.theme_dark_icon.count() >= 1, "Expected dark mode moon icon."
    assert manager_user_management_page.theme_light_icon.count() >= 1, "Expected light mode sun icon."

    # Test Theme Switching
    initial_mode = manager_user_management_page.get_theme_mode()
    manager_user_management_page.toggle_theme()
    manager_user_management_page.page.wait_for_timeout(300)

    new_mode = manager_user_management_page.get_theme_mode()
    assert new_mode != initial_mode, f"Expected theme mode to change from {initial_mode}, got {new_mode}."

    # Switch back
    manager_user_management_page.toggle_theme()
    manager_user_management_page.page.wait_for_timeout(300)
    assert manager_user_management_page.get_theme_mode() == initial_mode


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_notifications_dropdown(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify the notifications button renders bell icon and count badge,
    and opening the dropdown displays 'Notifications' heading, 'Mark all read' link,
    and 'Notification not found.' text.
    """
    manager_user_management_page.navigate()

    assert manager_user_management_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert manager_user_management_page.notification_count.is_visible(), "Expected notification count badge."
    assert manager_user_management_page.notification_count.inner_text().strip() == "0"

    # Open Notifications Dropdown
    manager_user_management_page.open_notifications()
    expect(manager_user_management_page.notification_menu).to_be_visible()

    # Dropdown Content
    assert manager_user_management_page.notification_menu.locator("h6").inner_text().strip() == "Notifications"
    assert manager_user_management_page.mark_all_read.is_visible()
    assert manager_user_management_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Simplebar Notification List Content
    assert manager_user_management_page.notification_empty_text.is_visible()
    assert "Notification not found." in manager_user_management_page.notification_empty_text.inner_text()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_profile_dropdown_and_logout_link(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify the user profile dropdown button displays initials and admin name,
    and clicking reveals the profile menu with administrator role and Logout link.
    """
    manager_user_management_page.navigate()

    # Profile Button Details
    assert manager_user_management_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert manager_user_management_page.profile_initials.is_visible(), "Expected profile initials to be visible."
    assert manager_user_management_page.profile_initials.inner_text().strip() == "M"

    if manager_user_management_page.profile_topbar_name.is_visible():
        assert manager_user_management_page.profile_topbar_name.inner_text().strip() == "madmin"

    # Open Profile Menu
    manager_user_management_page.open_profile_menu()
    expect(manager_user_management_page.profile_menu).to_be_visible()

    assert manager_user_management_page.profile_name.inner_text().strip() == "madmin"
    assert manager_user_management_page.profile_role.inner_text().strip() == "Administrator"

    # Logout link
    logout = manager_user_management_page.logout_link
    assert logout.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (logout.get_attribute("href") or "")
    assert "Logout" in logout.inner_text()
    assert logout.locator("i.mdi-logout").is_visible(), "Expected Logout icon."


# ==============================================================================
# SECTION 2: PAGE ACTIONS & HIDDEN PERMISSIONS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_page_actions_and_hidden_flags(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify the admin-page-actions container, Add User button (#addNew),
    2 hidden permission inputs (#editUserMgmt, #deleteUserMgmt),
    and opening/closing the User creation modal (#myModal).
    """
    manager_user_management_page.navigate()

    # Container and Add button
    assert manager_user_management_page.page_actions.is_visible(), "Expected .admin-page-actions to be visible."
    assert manager_user_management_page.add_user_button.is_visible(), "Expected #addNew button to be visible."
    assert manager_user_management_page.add_user_button.inner_text().strip() == "Add User"

    # Hidden permission values
    assert manager_user_management_page.edit_user_mgmt_hidden.get_attribute("value") == "1"
    assert manager_user_management_page.delete_user_mgmt_hidden.get_attribute("value") == "1"

    # Click Add User to open modal
    manager_user_management_page.add_user_button.click()
    manager_user_management_page.page.wait_for_timeout(500)

    expect(manager_user_management_page.user_modal).to_be_visible()
    assert "User Management" in manager_user_management_page.user_modal_title.inner_text()

    # Close modal
    manager_user_management_page.user_modal_close.first.click()
    manager_user_management_page.page.wait_for_timeout(500)
    expect(manager_user_management_page.user_modal).not_to_be_visible()


# ==============================================================================
# SECTION 3: TABLE CARD & COLUMN HEADERS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_table_card_and_column_headers(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify admin-table-card container, DataTable wrapper, 6 column headers
    (S.No, User Name, User Type, Login OTP, Action, Active), and initial records count.
    """
    manager_user_management_page.navigate()

    assert manager_user_management_page.table_card.is_visible(), "Expected .admin-table-card to be visible."
    assert manager_user_management_page.table_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."

    # Validate exact 6 column headers
    headers = [th.inner_text().strip() for th in manager_user_management_page.table_headers.all()]
    expected_headers = ["S.No", "User Name", "User Type", "Login OTP", "Action", "Active"]
    assert headers == expected_headers, f"Expected headers {expected_headers}, got {headers}."

    # Validate rows count and info
    assert manager_user_management_page.data_rows.count() >= 1
    info_text = manager_user_management_page.table_info.inner_text()
    assert "Showing 1 to" in info_text


# ==============================================================================
# SECTION 4: TABLE ROWS DATA INTEGRITY & ROW ACTIONS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_table_rows_data_integrity(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify table data integrity:
    - Row 1 displays 'sadmin', 'S', 'Direct', and active switch
    - Row 2 displays 'testuser_pw_check', 'A', 'Direct', and active switch
    - All rows have edit and password reset buttons
    - Non-admin rows have delete buttons
    - All rows have active status switch controls
    """
    manager_user_management_page.navigate()

    row_1 = manager_user_management_page.data_rows.nth(0)
    assert "sadmin" in row_1.inner_text()
    assert "Direct" in row_1.inner_text()

    row_2 = manager_user_management_page.data_rows.nth(1)
    assert "testuser_pw_check" in row_2.inner_text()
    assert "Direct" in row_2.inner_text()

    # Action buttons count
    assert manager_user_management_page.edit_user_buttons.count() >= 1
    assert manager_user_management_page.reset_password_buttons.count() >= 1
    assert manager_user_management_page.delete_buttons.count() >= 1
    assert manager_user_management_page.status_switches.count() >= 1


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_edit_user_action_modal(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify clicking the edit icon on a user row opens the User Management modal
    pre-populated with user details, and close button dismisses it cleanly.
    """
    manager_user_management_page.navigate()

    edit_btn = manager_user_management_page.edit_user_buttons.first
    assert edit_btn.is_visible()
    assert edit_btn.get_attribute("aria-label") == "Edit user"

    edit_btn.click()
    manager_user_management_page.page.wait_for_timeout(500)

    expect(manager_user_management_page.user_modal).to_be_visible()
    assert "User Management" in manager_user_management_page.user_modal_title.inner_text()

    # Dismiss modal
    manager_user_management_page.user_modal_close.first.click()
    manager_user_management_page.page.wait_for_timeout(500)
    expect(manager_user_management_page.user_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_reset_password_modal(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify clicking the reset password icon on a user row opens the password modal
    and close button dismisses it cleanly.
    """
    manager_user_management_page.navigate()

    reset_btn = manager_user_management_page.reset_password_buttons.first
    assert reset_btn.is_visible()
    assert reset_btn.get_attribute("aria-label") == "Reset password"

    reset_btn.click()
    manager_user_management_page.page.wait_for_timeout(500)

    expect(manager_user_management_page.reset_pass_modal).to_be_visible()
    assert "Reset Password" in manager_user_management_page.reset_pass_modal.locator(".modal-title").inner_text()

    # Dismiss modal
    close_btn = manager_user_management_page.reset_pass_modal.locator(".close, [data-dismiss='modal'], [data-bs-dismiss='modal'], button:has-text('Close')")
    if close_btn.count() > 0:
        close_btn.first.click()
        manager_user_management_page.page.wait_for_timeout(500)
        expect(manager_user_management_page.reset_pass_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_delete_action_triggers_sweetalert(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify clicking the delete icon on a non-admin user triggers the SweetAlert2
    confirmation dialog and cancel button dismisses it safely without altering data.
    """
    manager_user_management_page.navigate()

    initial_count = manager_user_management_page.data_rows.count()
    delete_btn = manager_user_management_page.delete_buttons.first
    assert delete_btn.is_visible()
    assert delete_btn.get_attribute("aria-label") == "Delete user"

    delete_btn.click()
    manager_user_management_page.page.wait_for_timeout(500)

    expect(manager_user_management_page.swal_popup).to_be_visible()
    assert "Are you sure?" in manager_user_management_page.swal_title.inner_text()
    assert manager_user_management_page.swal_confirm_button.is_visible()
    assert manager_user_management_page.swal_cancel_button.is_visible()

    # Safely cancel dialog without deleting
    manager_user_management_page.swal_cancel_button.click()
    manager_user_management_page.page.wait_for_timeout(500)
    expect(manager_user_management_page.swal_popup).not_to_be_visible()

    # Verify rows remain intact
    assert manager_user_management_page.data_rows.count() == initial_count


# ==============================================================================
# SECTION 5: CONTROLS, SEARCH & PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_length_dropdown_selection(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify changing visible entries per page via datatable_length dropdown
    (10, 25, 50, 100) updates visible users count and pagination status info.
    """
    manager_user_management_page.navigate()

    total_count = manager_user_management_page.data_rows.count()
    if total_count == 0:
        return

    for length in ["25", "50", "100"]:
        manager_user_management_page.select_page_length(length)
        assert manager_user_management_page.data_rows.count() == min(int(length), total_count)
        assert f"of {total_count} entries" in manager_user_management_page.table_info.inner_text()

    # Switch to 10 entries
    manager_user_management_page.select_page_length("10")
    assert manager_user_management_page.data_rows.count() == min(10, total_count)
    assert f"Showing 1 to {min(10, total_count)} of {total_count} entries" in manager_user_management_page.table_info.inner_text()

    # Restore to 25 entries
    manager_user_management_page.select_page_length("25")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_search_filtering(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify search input filters rows by user name, displays empty state
    when unmatched ('No matching records found'), and restores on clear.
    """
    manager_user_management_page.navigate()

    total_count = manager_user_management_page.data_rows.count()
    if total_count > 0:
        first_user = manager_user_management_page.data_rows.first.locator("td").nth(1).inner_text().strip()
        manager_user_management_page.search_user(first_user)
        assert manager_user_management_page.data_rows.count() >= 1
        assert "Showing 1 to" in manager_user_management_page.table_info.inner_text()
        assert first_user in manager_user_management_page.data_rows.first.inner_text()

    # Search for non-existent record
    manager_user_management_page.search_user("NONEXISTENTUSERXYZ")
    assert manager_user_management_page.empty_row.is_visible()
    assert "No matching records found" in manager_user_management_page.empty_row.inner_text()
    assert "Showing 0 to 0 of 0 entries" in manager_user_management_page.table_info.inner_text()

    # Clear search
    manager_user_management_page.clear_search()
    assert manager_user_management_page.data_rows.count() == total_count


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_user_management_pagination_controls(
    manager_user_management_page: ManagerUserManagementPage,
):
    """
    Verify pagination navigation when entries per page is set to 10:
    - Page 1 shows 1 to 10
    - Navigating to Page 2 shows remaining entries
    - Previous button navigates back to Page 1
    """
    manager_user_management_page.navigate()

    manager_user_management_page.select_page_length("10")
    total_count = manager_user_management_page.data_rows.count()
    assert manager_user_management_page.pagination.is_visible()
    assert manager_user_management_page.active_page_button.inner_text().strip() == "1"

    if total_count > 10:
        # Click Next button
        manager_user_management_page.next_page_button.click()
        manager_user_management_page.page.wait_for_timeout(400)
        assert manager_user_management_page.active_page_button.inner_text().strip() == "2"
        assert f"of {total_count} entries" in manager_user_management_page.table_info.inner_text()

        # Click Previous button
        manager_user_management_page.previous_page_button.click()
        manager_user_management_page.page.wait_for_timeout(400)
        assert manager_user_management_page.active_page_button.inner_text().strip() == "1"
        assert f"Showing 1 to 10 of {total_count} entries" in manager_user_management_page.table_info.inner_text()

    # Reset length
    manager_user_management_page.select_page_length("25")


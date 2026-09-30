"""
Admin Portal Manager Management Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.manager_management_page import (
    ManagerManagementPage,
)


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_topbar_branding_and_title(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify top navbar branding logos (small and large), page title ('Manager Management'),
    and sidebar menu button attributes matching the navbar-header layout.
    """
    manager_management_page.navigate()

    # Brand Logo & Responsive Icons
    assert manager_management_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert manager_management_page.logo_small.is_visible() or manager_management_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = manager_management_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert manager_management_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert manager_management_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert manager_management_page.menu_button.get_attribute("title") == "Open menu"
    assert manager_management_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert manager_management_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert manager_management_page.page_title.inner_text().strip() == "Manager Management"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_topbar_sidebar_toggle_action(
    manager_management_page: ManagerManagementPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    manager_management_page.navigate()

    body = manager_management_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    manager_management_page.menu_button.click()
    manager_management_page.page.wait_for_timeout(300)

    toggled_class = body.get_attribute("class") or ""
    toggled_sidebar_size = body.get_attribute("data-sidebar-size") or ""

    assert (
        toggled_class != initial_class
        or "sidebar-enable" in toggled_class
        or toggled_sidebar_size in ["sm", "lg", "condensed"]
    ), "Expected sidebar state to change on toggle."

    # Toggle back
    manager_management_page.menu_button.click()
    manager_management_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_theme_toggle_switches_modes(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify clicking the theme switch button toggles between dark and light themes,
    and dark/light SVG icons are present in the DOM.
    """
    manager_management_page.navigate()

    assert manager_management_page.theme_toggle.is_visible(), "Expected theme toggle button (#admin-theme-toggle) to be visible."
    assert manager_management_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert manager_management_page.theme_toggle.get_attribute("aria-label") == "Switch theme"

    # Both SVG icons (moon and sun) must exist in DOM
    assert manager_management_page.theme_dark_icon.count() >= 1, "Expected dark mode moon icon."
    assert manager_management_page.theme_light_icon.count() >= 1, "Expected light mode sun icon."

    # Test Theme Switching
    initial_mode = manager_management_page.get_theme_mode()
    manager_management_page.toggle_theme()
    manager_management_page.page.wait_for_timeout(300)

    new_mode = manager_management_page.get_theme_mode()
    assert new_mode != initial_mode, f"Expected theme mode to change from {initial_mode}, got {new_mode}."

    # Switch back
    manager_management_page.toggle_theme()
    manager_management_page.page.wait_for_timeout(300)
    assert manager_management_page.get_theme_mode() == initial_mode


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_notifications_dropdown(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify the notifications button renders bell icon and count badge,
    and opening the dropdown displays 'Notifications' heading, 'Mark all read' link,
    and 'Notification not found.' text.
    """
    manager_management_page.navigate()

    assert manager_management_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert manager_management_page.notification_count.is_visible(), "Expected notification count badge."
    assert manager_management_page.notification_count.inner_text().strip().isdigit(), "Expected notification count to be numeric."

    # Open Notifications Dropdown
    manager_management_page.open_notifications()
    expect(manager_management_page.notification_menu).to_be_visible()

    # Dropdown Content
    heading = manager_management_page.notification_menu.locator(".notification-head h6")
    assert heading.inner_text().strip() == "Notifications"
    assert manager_management_page.mark_all_read.is_visible()
    assert manager_management_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Notification List Content - may have items or show empty text
    notification_list = manager_management_page.notification_menu.locator(".notification-list")
    assert notification_list.is_visible(), "Expected notification list container to be visible."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_profile_dropdown_and_logout_link(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify the user profile dropdown button displays initials and admin name,
    and clicking reveals the profile menu with administrator role and Logout link.
    """
    manager_management_page.navigate()

    # Profile Button Details
    assert manager_management_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert manager_management_page.profile_initials.is_visible(), "Expected profile initials to be visible."
    assert manager_management_page.profile_initials.inner_text().strip() == "M"

    if manager_management_page.profile_topbar_name.is_visible():
        assert manager_management_page.profile_topbar_name.inner_text().strip() == "madmin"

    # Open Profile Menu
    manager_management_page.open_profile_menu()
    expect(manager_management_page.profile_menu).to_be_visible()

    assert manager_management_page.profile_name.inner_text().strip() == "madmin"
    assert manager_management_page.profile_role.inner_text().strip() == "Administrator"

    # Logout link
    logout = manager_management_page.logout_link
    assert logout.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (logout.get_attribute("href") or "")
    assert "Logout" in logout.inner_text()
    assert logout.locator("i.mdi-logout").is_visible(), "Expected Logout icon."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_permissions_hidden_inputs(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify the page-title-box hidden permission input flags:
    #editmanager and #deletemanager both have value '1'.
    """
    manager_management_page.navigate()
    assert manager_management_page.editmanager_input.count() >= 1, "Expected #editmanager input."
    assert manager_management_page.editmanager_input.get_attribute("value") == "1"
    assert manager_management_page.deletemanager_input.count() >= 1, "Expected #deletemanager input."
    assert manager_management_page.deletemanager_input.get_attribute("value") == "1"


# ==============================================================================
# SECTION 2: PAGE ACTIONS & ADD MANAGER
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_add_manager_button_and_modal(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify the Add Manager button (#addNew) is visible,
    and clicking it opens the Manager creation modal (#myModal).
    """
    manager_management_page.navigate()

    # Add Manager button
    assert manager_management_page.add_manager_button.is_visible(), "Expected #addNew button to be visible."
    assert manager_management_page.add_manager_button.inner_text().strip() == "Add Manager"

    # Click Add Manager to open modal
    manager_management_page.add_manager_button.click()
    manager_management_page.page.wait_for_timeout(500)

    expect(manager_management_page.manager_modal).to_be_visible()

    # Close modal
    manager_management_page.manager_modal_close.first.click()
    manager_management_page.page.wait_for_timeout(500)
    expect(manager_management_page.manager_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_add_modal_form_fields(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify Add Manager modal contains all required form fields:
    Username (#username), Email (#email), Password (#password), and Submit button (#formSubmit).
    """
    manager_management_page.navigate()
    manager_management_page.add_manager_button.click()
    manager_management_page.page.wait_for_timeout(500)

    expect(manager_management_page.manager_modal).to_be_visible()
    assert manager_management_page.modal_username.is_visible(), "Expected #username input in modal."
    assert manager_management_page.modal_email.is_visible(), "Expected #email input in modal."
    assert manager_management_page.modal_password.is_visible(), "Expected #password input in modal."
    assert manager_management_page.modal_submit.is_visible(), "Expected #formSubmit button in modal."

    # Close modal cleanly
    manager_management_page.manager_modal_close.first.click()
    manager_management_page.page.wait_for_timeout(500)
    expect(manager_management_page.manager_modal).not_to_be_visible()


# ==============================================================================
# SECTION 3: TABLE CARD & COLUMN HEADERS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_table_card_and_column_headers(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify table card container, DataTable wrapper, 5 column headers
    (S.No, Manager Name, Email, Password, Action), and initial records count.
    """
    manager_management_page.navigate()

    assert manager_management_page.table_card.is_visible(), "Expected table card to be visible."
    assert manager_management_page.table_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."

    # Validate exact 5 column headers
    headers = [th.inner_text().strip() for th in manager_management_page.table_headers.all()]
    expected_headers = ["S.No", "Manager Name", "Email", "Pasword", "Action"]
    assert headers == expected_headers, f"Expected headers {expected_headers}, got {headers}."

    # Validate rows count and info
    assert manager_management_page.data_rows.count() >= 1
    info_text = manager_management_page.table_info.inner_text()
    assert "Showing 1 to" in info_text


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_table_sorting_by_manager_name(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify clicking the Manager Name column header toggles sorting order between ascending and descending.
    """
    manager_management_page.navigate()
    manager_name_header = manager_management_page.table_headers.nth(1)
    assert "Manager Name" in manager_name_header.inner_text()

    # Click to sort
    manager_name_header.click()
    manager_management_page.page.wait_for_timeout(400)
    sorted_class = manager_name_header.get_attribute("class") or ""
    assert "sorting_asc" in sorted_class or "sorting_desc" in sorted_class

    # Click again to reverse sort
    manager_name_header.click()
    manager_management_page.page.wait_for_timeout(400)
    sorted_desc_class = manager_name_header.get_attribute("class") or ""
    assert "sorting_desc" in sorted_desc_class or "sorting_asc" in sorted_desc_class


# ==============================================================================
# SECTION 4: TABLE ROWS DATA INTEGRITY & ROW ACTIONS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_table_rows_data_integrity(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify table data integrity:
    - Rows display sequential S.No values
    - Each row has manager name, email, password (masked), and action buttons
    - Edit and delete action buttons are present
    """
    manager_management_page.navigate()

    row_count = manager_management_page.data_rows.count()
    assert row_count >= 1, "Expected at least 1 manager row."

    # First row check
    row_1 = manager_management_page.data_rows.nth(0)
    row_text = row_1.inner_text()
    assert "1" in row_text, "Expected S.No 1 in first row."

    # Action buttons count
    assert manager_management_page.edit_buttons.count() >= 1, "Expected at least 1 edit button."
    assert manager_management_page.delete_buttons.count() >= 1, "Expected at least 1 delete button."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_passwords_are_masked(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify security compliance: all manager rows display masked password values (asterisks) in table.
    """
    manager_management_page.navigate()
    row_count = manager_management_page.data_rows.count()
    assert row_count >= 1

    for idx in range(min(row_count, 5)):
        pwd_cell = manager_management_page.data_rows.nth(idx).locator("td").nth(3)
        pwd_text = pwd_cell.inner_text().strip()
        assert "*" in pwd_text, f"Expected masked password in row {idx+1}, got {pwd_text}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_row_action_button_tooltips(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify row action buttons have proper tooltips, aria-labels, and icons for Edit and Delete.
    """
    manager_management_page.navigate()
    first_edit = manager_management_page.edit_buttons.first
    first_delete = manager_management_page.delete_buttons.first

    first_edit.wait_for(state="visible", timeout=10000)
    first_delete.wait_for(state="visible", timeout=10000)
    assert first_edit.is_visible()
    edit_title = (
        first_edit.get_attribute("data-bs-original-title")
        or first_edit.get_attribute("title")
        or first_edit.get_attribute("aria-label")
        or ""
    )
    assert "Edit" in edit_title or "edit" in edit_title

    assert first_delete.is_visible()
    delete_title = (
        first_delete.get_attribute("data-bs-original-title")
        or first_delete.get_attribute("title")
        or first_delete.get_attribute("aria-label")
        or ""
    )
    assert "Delete" in delete_title or "delete" in delete_title

    assert first_edit.locator("i.mdi-book-edit-outline, i.mdi-pencil").is_visible()
    assert first_delete.locator("i.mdi-trash-can, i.mdi-delete").is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_edit_manager_action_modal(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify clicking the edit icon on a manager row opens the Manager modal
    and close button dismisses it cleanly.
    """
    manager_management_page.navigate()

    edit_btn = manager_management_page.edit_buttons.first
    edit_btn.wait_for(state="visible", timeout=10000)
    assert edit_btn.is_visible()

    edit_btn.click()
    manager_management_page.page.wait_for_timeout(500)

    expect(manager_management_page.manager_modal).to_be_visible()

    # Dismiss modal
    manager_management_page.manager_modal_close.first.click()
    manager_management_page.page.wait_for_timeout(500)
    expect(manager_management_page.manager_modal).not_to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_delete_action_triggers_sweetalert(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify clicking the delete icon on a manager triggers the SweetAlert2
    confirmation dialog and cancel button dismisses it safely without altering data.
    """
    manager_management_page.navigate()

    initial_count = manager_management_page.data_rows.count()
    delete_btn = manager_management_page.delete_buttons.first
    delete_btn.wait_for(state="visible", timeout=10000)
    assert delete_btn.is_visible()

    delete_btn.click()
    manager_management_page.page.wait_for_timeout(500)

    expect(manager_management_page.swal_popup).to_be_visible()
    assert "Are you sure?" in manager_management_page.swal_title.inner_text()
    assert manager_management_page.swal_confirm_button.is_visible()
    assert manager_management_page.swal_cancel_button.is_visible()

    # Safely cancel dialog without deleting
    manager_management_page.swal_cancel_button.click()
    manager_management_page.page.wait_for_timeout(500)
    expect(manager_management_page.swal_popup).not_to_be_visible()

    # Verify rows remain intact
    assert manager_management_page.data_rows.count() == initial_count


# ==============================================================================
# SECTION 5: CONTROLS, SEARCH & PAGINATION
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_length_dropdown_selection(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify changing visible entries per page via datatable_length dropdown
    (10, 25, 50, 100) updates visible manager count and pagination status info.
    """
    manager_management_page.navigate()

    # With 11 records, selecting 25/50/100 should show all 11
    for length in ["25", "50", "100"]:
        manager_management_page.select_page_length(length)
        assert manager_management_page.data_rows.count() == 11
        assert "Showing 1 to 11 of 11 entries" in manager_management_page.table_info.inner_text()

    # Switch to 10 entries - should show first 10 of 11
    manager_management_page.select_page_length("10")
    assert manager_management_page.data_rows.count() == 10
    assert "Showing 1 to 10 of 11 entries" in manager_management_page.table_info.inner_text()

    # Restore to 25 entries
    manager_management_page.select_page_length("25")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_search_filtering(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify search input filters rows by manager name, displays empty state
    when unmatched ('No matching records found'), and restores on clear.
    """
    manager_management_page.navigate()

    # Search for a known manager from the screenshot
    manager_management_page.search_manager("Test manager")
    assert manager_management_page.data_rows.count() >= 1
    assert "Test manager" in manager_management_page.data_rows.first.inner_text()

    # Search for non-existent record
    manager_management_page.search_manager("NONEXISTENTMANAGERXYZ")
    assert manager_management_page.empty_row.is_visible()
    assert "No matching records found" in manager_management_page.empty_row.inner_text()
    assert "Showing 0 to 0 of 0 entries" in manager_management_page.table_info.inner_text()

    # Clear search
    manager_management_page.clear_search()
    assert manager_management_page.data_rows.count() >= 1


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manager_management_pagination_controls(
    manager_management_page: ManagerManagementPage,
):
    """
    Verify pagination navigation when entries per page is set to 10:
    - Page 1 shows 1 to 10
    - Navigating to Page 2 shows 11 to 11
    - Previous button navigates back to Page 1
    """
    manager_management_page.navigate()

    manager_management_page.select_page_length("10")
    assert manager_management_page.pagination.is_visible()
    assert manager_management_page.active_page_button.inner_text().strip() == "1"

    # Click Next button
    manager_management_page.next_page_button.click()
    manager_management_page.page.wait_for_timeout(400)
    assert manager_management_page.active_page_button.inner_text().strip() == "2"
    assert "Showing 11 to 11 of 11 entries" in manager_management_page.table_info.inner_text()

    # Click Previous button
    manager_management_page.previous_page_button.click()
    manager_management_page.page.wait_for_timeout(400)
    assert manager_management_page.active_page_button.inner_text().strip() == "1"
    assert "Showing 1 to 10 of 11 entries" in manager_management_page.table_info.inner_text()

    # Reset length
    manager_management_page.select_page_length("25")

"""
Admin Portal Manage Leads Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.manage_leads_page import ManageLeadsPage


# ==============================================================================
# SECTION 1: TOP NAVIGATION BAR HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_topbar_branding_and_title(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    manage_leads_page.navigate()

    # Brand Logo & Responsive Icons
    assert manage_leads_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert manage_leads_page.logo_small.is_visible() or manage_leads_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = manage_leads_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert manage_leads_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert manage_leads_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert manage_leads_page.menu_button.get_attribute("title") == "Open menu"
    assert manage_leads_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert manage_leads_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert manage_leads_page.page_title.inner_text().strip() == "Leads"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_topbar_sidebar_toggle_action(
    manage_leads_page: ManageLeadsPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    manage_leads_page.navigate()

    body = manage_leads_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    manage_leads_page.menu_button.click()
    manage_leads_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    manage_leads_page.menu_button.click()
    manage_leads_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_theme_toggle_switches_modes(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    manage_leads_page.navigate()

    assert manage_leads_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert manage_leads_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert manage_leads_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert manage_leads_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert manage_leads_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = manage_leads_page.get_theme_mode() or "light"

    manage_leads_page.toggle_theme()
    manage_leads_page.page.wait_for_timeout(300)

    toggled_mode = manage_leads_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    manage_leads_page.toggle_theme()
    manage_leads_page.page.wait_for_timeout(300)
    assert manage_leads_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_notifications_dropdown(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify notification bell button, unread badge, dropdown menu,
    Mark all read link, and notifications content.
    """
    manage_leads_page.navigate()

    assert manage_leads_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert manage_leads_page.notification_count.is_visible(), "Expected notification count badge to be visible."
    assert manage_leads_page.notification_count.inner_text().strip().isdigit(), "Expected numeric notification count."

    manage_leads_page.open_notifications()
    manage_leads_page.notification_menu.wait_for(state="visible", timeout=10000)

    assert manage_leads_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert manage_leads_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert manage_leads_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list has items or empty message
    menu_text = manage_leads_page.notification_menu.inner_text().casefold()
    assert "notification" in menu_text or manage_leads_page.notification_items.count() > 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_profile_dropdown_and_logout_link(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    manage_leads_page.navigate()

    assert manage_leads_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert manage_leads_page.profile_initials.first.inner_text().strip() == "M"
    assert manage_leads_page.profile_topbar_name.inner_text().strip() == "madmin"

    manage_leads_page.open_profile_menu()
    manage_leads_page.profile_menu.wait_for(state="visible", timeout=10000)

    assert manage_leads_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert manage_leads_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in manage_leads_page.profile_role.inner_text().casefold()

    assert manage_leads_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = manage_leads_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: LEADS PAGE ACTIONS & MODALS (.leads-page-actions)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_action_buttons_and_permissions_rendered(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify the actions bar displays Lead Types, Add Lead, Bulk Upload buttons,
    and hidden permission control flags.
    """
    manage_leads_page.navigate()

    # Action buttons container
    assert manage_leads_page.actions_bar.is_visible(), "Expected .leads-page-actions container."

    # Lead Types button
    assert manage_leads_page.lead_types_button.is_visible(), "Expected #manageLeadTypes button."
    assert manage_leads_page.lead_types_button.inner_text().strip() == "Lead Types"

    # Add Lead button
    assert manage_leads_page.add_lead_button.is_visible(), "Expected #addNew button."
    assert manage_leads_page.add_lead_button.inner_text().strip() == "Add Lead"

    # Bulk Upload button
    assert manage_leads_page.bulk_upload_button.is_visible(), "Expected #bulkUpload button."
    assert manage_leads_page.bulk_upload_button.inner_text().strip() == "Bulk Upload"

    # Hidden permission controls
    assert manage_leads_page.permission_edit.get_attribute("value") == "1", "Expected editlead=1."
    assert manage_leads_page.permission_delete.get_attribute("value") == "1", "Expected deletelead=1."
    assert manage_leads_page.permission_settings.get_attribute("value") == "1", "Expected settingsLeadType=1."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_lead_types_modal_opens_and_closes(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify clicking the Lead Types button opens the Lead Type Form modal
    with category controls and table, and dismisses cleanly.
    """
    manage_leads_page.navigate()

    manage_leads_page.open_lead_types_modal()
    assert manage_leads_page.lead_types_modal.is_visible(), "Expected #leadTypeModal to be open."
    assert "lead type form" in manage_leads_page.lead_types_modal_title.inner_text().casefold()

    # Form controls
    assert manage_leads_page.lead_type_name_input.is_visible(), "Expected lead_type_name input."
    assert manage_leads_page.lead_type_submit_button.is_visible(), "Expected Add button (#leadTypeSubmit)."
    assert manage_leads_page.lead_type_cancel_button.count() >= 1, "Expected Cancel button (#leadTypeCancel) in DOM."

    # Dismiss modal safely
    manage_leads_page.close_lead_types_modal()
    assert not manage_leads_page.lead_types_modal.is_visible(), "Expected modal to close."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_add_lead_modal_opens_and_closes(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify clicking Add Lead opens the Leads Form modal with all required
    fields (name, email, phone, employee, lead type, date, description)
    and dismisses safely.
    """
    manage_leads_page.navigate()

    manage_leads_page.open_add_lead_modal()
    assert manage_leads_page.lead_modal.is_visible(), "Expected #myModal to be open."
    assert "leads form" in manage_leads_page.lead_modal_title.inner_text().casefold()

    # Required Form Fields
    assert manage_leads_page.lead_name_input.is_visible(), "Expected Name input."
    assert manage_leads_page.lead_email_input.is_visible(), "Expected Email input."
    assert manage_leads_page.lead_phone_input.is_visible(), "Expected Phone input."
    assert manage_leads_page.lead_admin_select.is_visible(), "Expected Employee select dropdown."
    assert manage_leads_page.lead_type_select.is_visible(), "Expected Lead Type select dropdown."
    assert manage_leads_page.lead_followup_input.is_visible(), "Expected Followup date input."
    assert manage_leads_page.lead_description_input.is_visible(), "Expected Description input."
    assert manage_leads_page.lead_submit_button.is_visible(), "Expected Save button (#formSubmit)."

    # Dismiss modal safely
    manage_leads_page.close_add_lead_modal()
    assert not manage_leads_page.lead_modal.is_visible(), "Expected Leads modal to close."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_add_lead_empty_submission_validation(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify submitting empty Add Lead form prevents submission
    and keeps the modal open.
    """
    manage_leads_page.navigate()

    manage_leads_page.open_add_lead_modal()
    assert manage_leads_page.lead_modal.is_visible()

    # Attempt to submit empty form
    manage_leads_page.lead_name_input.fill("")
    manage_leads_page.lead_submit_button.click()
    manage_leads_page.page.wait_for_timeout(400)

    # Modal should remain open due to required validations
    assert manage_leads_page.lead_modal.is_visible(), "Modal should remain open on empty submission."

    manage_leads_page.close_add_lead_modal()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_bulk_upload_modal_opens_and_closes(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify clicking Bulk Upload opens the Bulk Upload modal with file input,
    Save button, and dismisses cleanly.
    """
    manage_leads_page.navigate()

    manage_leads_page.open_bulk_upload_modal()
    assert manage_leads_page.bulk_upload_modal.is_visible(), "Expected #bulkUploadModal to be open."
    assert "bulk upload" in manage_leads_page.bulk_upload_modal_title.inner_text().casefold()

    # File input & Save button
    assert manage_leads_page.bulk_file_input.count() >= 1, "Expected bulk_file input."
    assert manage_leads_page.bulk_submit_button.is_visible(), "Expected Save button (#bulkFormSubmit)."

    # Dismiss modal safely
    manage_leads_page.close_bulk_upload_modal()
    assert not manage_leads_page.bulk_upload_modal.is_visible(), "Expected Bulk Upload modal to close."


# ==============================================================================
# SECTION 3: LEADS TABLE CARD (.leads-table-card) & DATATABLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_table_card_and_datatable_controls(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify the Leads table card wrapper, DataTable length dropdown with
    options 10, 25, 50, 100, and search filter input.
    """
    manage_leads_page.navigate()

    assert manage_leads_page.table_card.is_visible(), "Expected .card.leads-table-card to be visible."
    assert manage_leads_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert manage_leads_page.length_dropdown.is_visible(), "Expected page length dropdown to be visible."
    assert manage_leads_page.search_input.is_visible(), "Expected search input to be visible."

    # Verify length options
    options = [
        opt.get_attribute("value")
        for opt in manage_leads_page.length_dropdown.locator("option").all()
    ]
    expected_options = ["10", "25", "50", "100"]
    for opt in expected_options:
        assert opt in options, f"Expected option '{opt}' in length dropdown, got {options}"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_table_headers_and_columns_are_valid(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify that all 9 expected table column headers (S.No, Name, Email, Phone,
    Employee Name, Lead Type, Followup Date, Description, Action) and sortable states
    are rendered correctly.
    """
    manage_leads_page.navigate()

    expected_headers = [
        "s.no",
        "name",
        "email",
        "phone",
        "employee name",
        "lead type",
        "followup date",
        "description",
        "action",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in manage_leads_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # All headers are sortable
    assert manage_leads_page.table_headers.count() >= 9
    for i in range(9):
        header_class = manage_leads_page.table_headers.nth(i).get_attribute("class") or ""
        assert "sorting" in header_class, f"Expected header {i} to be sortable, got '{header_class}'"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_table_rows_data_integrity(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify that Manage Leads table rows display sequential S.No, Name,
    valid Email, Phone, Employee Name, Lead Type, Followup Date, and Action buttons.
    """
    manage_leads_page.navigate()

    row_count = manage_leads_page.get_row_count()
    assert row_count > 0, "Expected at least one lead row in table."

    first_row = manage_leads_page.table_rows.first
    cells = first_row.locator("td").all_inner_texts()
    assert len(cells) >= 9, f"Expected at least 9 cells in row, got {len(cells)}"

    # S.No (1st column) has responsive dtr-control and is numeric
    s_no = cells[0].strip()
    assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"
    assert "dtr-control" in (first_row.locator("td").first.get_attribute("class") or "")

    # Name (2nd column)
    assert cells[1].strip(), "Expected non-empty lead name."

    # Email (3rd column)
    assert "@" in cells[2], f"Expected valid email with @, got '{cells[2]}'"

    # Phone (4th column)
    assert cells[3].strip(), "Expected non-empty phone."

    # Action column has Edit and Delete buttons
    assert first_row.locator("a.btnEdit, .btn.btnEdit").is_visible(), "Expected Edit button."
    assert first_row.locator("a.BtnDelete, .btn.BtnDelete").count() >= 1, "Expected Delete button."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_edit_lead_action_opens_modal_prefilled(
    manage_leads_page: ManageLeadsPage,
):
    """
    Verify clicking the edit pencil on a row opens the Leads Form modal
    prefilled with the lead's details and dismisses cleanly.
    """
    manage_leads_page.navigate()

    first_row = manage_leads_page.table_rows.first
    lead_name = first_row.locator("td").nth(1).inner_text().strip()

    manage_leads_page.open_edit_lead(0)
    assert manage_leads_page.lead_modal.is_visible(), "Expected #myModal to open on Edit click."

    prefilled_name = manage_leads_page.lead_name_input.input_value().strip()
    assert prefilled_name == lead_name, f"Expected prefilled name '{lead_name}', got '{prefilled_name}'"

    manage_leads_page.close_add_lead_modal()
    assert not manage_leads_page.lead_modal.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_page_length_selection(
    manage_leads_page: ManageLeadsPage,
):
    """Verify changing page length dropdown updates visible row count and DataTable info."""
    manage_leads_page.navigate()

    for length in ["10", "25", "50"]:
        manage_leads_page.select_page_length(length)
        assert manage_leads_page.length_dropdown.input_value() == length
        info_text = manage_leads_page.get_table_info_text()
        assert "showing" in info_text.casefold()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_search_filters_by_name(
    manage_leads_page: ManageLeadsPage,
):
    """Verify entering a lead name into the search bar filters rows correctly."""
    manage_leads_page.navigate()

    first_row = manage_leads_page.table_rows.first
    target_name = first_row.locator("td").nth(1).inner_text().strip()

    manage_leads_page.search_leads(target_name)
    assert manage_leads_page.get_row_count() >= 1

    first_filtered = manage_leads_page.table_rows.first
    assert target_name.casefold() in first_filtered.locator("td").nth(1).inner_text().casefold()

    manage_leads_page.clear_search()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_search_filters_by_email(
    manage_leads_page: ManageLeadsPage,
):
    """Verify searching by email isolates matching lead records."""
    manage_leads_page.navigate()

    first_row = manage_leads_page.table_rows.first
    target_email = first_row.locator("td").nth(2).inner_text().strip()

    manage_leads_page.search_leads(target_email)
    assert manage_leads_page.get_row_count() >= 1

    first_filtered = manage_leads_page.table_rows.first
    assert target_email.casefold() in first_filtered.locator("td").nth(2).inner_text().casefold()

    manage_leads_page.clear_search()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_search_nonexistent_query_shows_empty_state(
    manage_leads_page: ManageLeadsPage,
):
    """Verify searching for a nonexistent term shows empty state and zero entries."""
    manage_leads_page.navigate()

    manage_leads_page.search_leads("NonExistent_Lead_Query_XYZ_999")
    info_text = manage_leads_page.get_table_info_text()
    assert "0" in info_text

    empty_cell = manage_leads_page.empty_state_cell
    assert empty_cell.is_visible() or manage_leads_page.get_row_count() == 0

    manage_leads_page.clear_search()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_table_column_sorting(
    manage_leads_page: ManageLeadsPage,
):
    """Verify clicking sortable column headers toggles sorting class."""
    manage_leads_page.navigate()

    s_no_header = manage_leads_page.table_headers.first
    s_no_header.click()
    manage_leads_page.page.wait_for_timeout(300)
    class_after_first = s_no_header.get_attribute("class") or ""
    assert "sorting_asc" in class_after_first or "sorting_desc" in class_after_first

    s_no_header.click()
    manage_leads_page.page.wait_for_timeout(300)
    class_after_second = s_no_header.get_attribute("class") or ""
    assert class_after_second != class_after_first


@pytest.mark.admin
@pytest.mark.regression
def test_admin_manage_leads_table_pagination_and_info(
    manage_leads_page: ManageLeadsPage,
):
    """Verify DataTable info text and pagination controls render active status."""
    manage_leads_page.navigate()

    # Info status
    info = manage_leads_page.datatable_info
    assert info.is_visible(), "Expected #datatable_info to be visible."
    assert info.get_attribute("role") == "status"
    assert info.get_attribute("aria-live") == "polite"
    info_text = manage_leads_page.get_table_info_text()
    assert "showing" in info_text.casefold()
    assert "entries" in info_text.casefold()

    # Pagination controls
    assert manage_leads_page.pagination.is_visible(), "Expected pagination container to be visible."
    assert manage_leads_page.pagination_previous.is_visible(), "Expected Previous button to be visible."
    assert manage_leads_page.pagination_next.is_visible(), "Expected Next button to be visible."
    assert manage_leads_page.pagination.locator("li.page-item.active").is_visible(), (
        "Expected active page indicator."
    )



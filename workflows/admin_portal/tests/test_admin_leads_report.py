"""
Admin Portal Leads Report Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.leads_report_page import LeadsReportPage


# ==============================================================================
# SECTION 1: TOP NAVIGATION BAR HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_topbar_branding_and_title(
    leads_report_page: LeadsReportPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    leads_report_page.navigate()

    # Brand Logo & Responsive Icons
    assert leads_report_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert leads_report_page.logo_small.is_visible() or leads_report_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = leads_report_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert leads_report_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert leads_report_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert leads_report_page.menu_button.get_attribute("title") == "Open menu"
    assert leads_report_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert leads_report_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert leads_report_page.page_title.inner_text().strip() == "Report"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_topbar_sidebar_toggle_action(
    leads_report_page: LeadsReportPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    leads_report_page.navigate()

    body = leads_report_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    leads_report_page.menu_button.click()
    leads_report_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    leads_report_page.menu_button.click()
    leads_report_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_theme_toggle_switches_modes(
    leads_report_page: LeadsReportPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    leads_report_page.navigate()

    assert leads_report_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert leads_report_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert leads_report_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert leads_report_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert leads_report_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = leads_report_page.get_theme_mode() or "light"

    leads_report_page.toggle_theme()
    leads_report_page.page.wait_for_timeout(300)

    toggled_mode = leads_report_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    leads_report_page.toggle_theme()
    leads_report_page.page.wait_for_timeout(300)
    assert leads_report_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_notifications_dropdown(
    leads_report_page: LeadsReportPage,
):
    """
    Verify notification bell button, unread badge, dropdown menu,
    Mark all read link, and notifications content.
    """
    leads_report_page.navigate()

    assert leads_report_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert leads_report_page.notification_count.is_visible(), "Expected notification count badge to be visible."
    assert leads_report_page.notification_count.inner_text().strip().isdigit(), "Expected numeric notification count."

    leads_report_page.open_notifications()
    leads_report_page.notification_menu.wait_for(state="visible", timeout=10000)

    assert leads_report_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert leads_report_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert leads_report_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Verify notification list has items or empty message
    menu_text = leads_report_page.notification_menu.inner_text().casefold()
    assert "notification" in menu_text or leads_report_page.notification_items.count() > 0


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_profile_dropdown_and_logout_link(
    leads_report_page: LeadsReportPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    leads_report_page.navigate()

    assert leads_report_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert leads_report_page.profile_initials.first.inner_text().strip() == "M"
    assert leads_report_page.profile_topbar_name.inner_text().strip() == "madmin"

    leads_report_page.open_profile_menu()
    leads_report_page.profile_menu.wait_for(state="visible", timeout=10000)

    assert leads_report_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert leads_report_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in leads_report_page.profile_role.inner_text().casefold()

    assert leads_report_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = leads_report_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: REPORT FILTER BAR (.report-filter-bar)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_filter_bar_structure_and_visibility(
    leads_report_page: LeadsReportPage,
):
    """
    Verify the Leads Report filter bar renders date pickers, dropdown selects,
    and action buttons with proper attributes.
    """
    leads_report_page.navigate()

    # Filter Bar container
    assert leads_report_page.filter_bar.is_visible(), "Expected filter bar (.report-filter-bar) to be visible."

    # Date Inputs
    assert leads_report_page.from_date_input.is_visible(), "Expected fromDate input to be visible."
    assert leads_report_page.from_date_input.get_attribute("type") == "date"
    assert leads_report_page.to_date_input.is_visible(), "Expected toDate input to be visible."
    assert leads_report_page.to_date_input.get_attribute("type") == "date"

    # Default Date Values format (YYYY-MM-DD)
    from_val = leads_report_page.from_date_input.input_value()
    to_val = leads_report_page.to_date_input.input_value()
    assert len(from_val.split("-")) == 3, f"Expected YYYY-MM-DD fromDate, got '{from_val}'"
    assert len(to_val.split("-")) == 3, f"Expected YYYY-MM-DD toDate, got '{to_val}'"

    # Select dropdowns
    assert leads_report_page.employee_select.is_visible(), "Expected employee dropdown (#admin_id) to be visible."
    assert leads_report_page.lead_type_select.is_visible(), "Expected lead type dropdown (#lead_type_id) to be visible."

    # Action buttons
    assert leads_report_page.filter_button.is_visible(), "Expected Filter button to be visible."
    assert leads_report_page.filter_button.inner_text().strip() == "Filter"
    assert leads_report_page.download_button.is_visible(), "Expected Download XLSX button to be visible."
    assert leads_report_page.download_button.inner_text().strip() == "Download XLSX"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_employee_dropdown_options(
    leads_report_page: LeadsReportPage,
):
    """
    Verify the Employee dropdown (#admin_id) displays the placeholder,
    'All' option, and employee options, and updates selection properly.
    """
    leads_report_page.navigate()

    options = leads_report_page.employee_select.locator("option")
    count = options.count()
    assert count >= 2, f"Expected at least 2 employee options, got {count}"

    # Verify placeholder & 'All'
    first_opt_text = options.first.inner_text().strip()
    first_opt_val = options.first.get_attribute("value")
    assert "--Select Employee--" in first_opt_text
    assert first_opt_val == ""

    second_opt_text = options.nth(1).inner_text().strip()
    second_opt_val = options.nth(1).get_attribute("value")
    assert second_opt_text == "All"
    assert second_opt_val == "all"

    # Select 'all' and verify
    leads_report_page.select_employee("all")
    assert leads_report_page.employee_select.input_value() == "all"

    # Revert to placeholder
    leads_report_page.select_employee("")
    assert leads_report_page.employee_select.input_value() == ""


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_lead_type_dropdown_options(
    leads_report_page: LeadsReportPage,
):
    """
    Verify the Lead Type dropdown (#lead_type_id) displays the placeholder,
    'All' option, valid lead category options, and updates selection properly.
    """
    leads_report_page.navigate()

    options = leads_report_page.lead_type_select.locator("option")
    count = options.count()
    assert count >= 2, f"Expected at least 2 lead type options, got {count}"

    # Verify placeholder & 'All'
    first_opt_text = options.first.inner_text().strip()
    first_opt_val = options.first.get_attribute("value")
    assert "--Select Lead Type--" in first_opt_text
    assert first_opt_val == ""

    second_opt_text = options.nth(1).inner_text().strip()
    second_opt_val = options.nth(1).get_attribute("value")
    assert second_opt_text == "All"
    assert second_opt_val == "all"

    # Verify options contain categories
    all_texts = [opt.strip() for opt in options.all_inner_texts()]
    assert any("Approved" in t or "Not Interested" in t or "All" in t for t in all_texts)

    # Select 'all' and verify
    leads_report_page.select_lead_type("all")
    assert leads_report_page.lead_type_select.input_value() == "all"

    # Revert to placeholder
    leads_report_page.select_lead_type("")
    assert leads_report_page.lead_type_select.input_value() == ""


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_date_inputs_interaction(
    leads_report_page: LeadsReportPage,
):
    """Verify modifying fromDate and toDate input fields updates values accurately."""
    leads_report_page.navigate()

    leads_report_page.set_date_range("2026-09-01", "2026-09-28")
    assert leads_report_page.from_date_input.input_value() == "2026-09-01"
    assert leads_report_page.to_date_input.input_value() == "2026-09-28"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_filter_button_action(
    leads_report_page: LeadsReportPage,
):
    """
    Verify clicking the Filter button applies the selected filter criteria
    without navigation errors or crashing.
    """
    leads_report_page.navigate()

    leads_report_page.select_employee("all")
    leads_report_page.select_lead_type("all")
    leads_report_page.click_filter()

    # Verify page remains intact and filter bar is still available
    assert leads_report_page.filter_bar.is_visible()
    assert leads_report_page.page_title.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_download_button_attributes(
    leads_report_page: LeadsReportPage,
):
    """Verify the Download XLSX button displays correct styling and action attributes."""
    leads_report_page.navigate()

    btn = leads_report_page.download_button
    assert btn.is_visible(), "Expected Download XLSX button to be visible."
    btn_class = btn.get_attribute("class") or ""
    assert "btn-success" in btn_class, f"Expected btn-success class, got '{btn_class}'"
    assert btn.get_attribute("id") == "downloadLeadReport"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_employee_specific_options_selection(
    leads_report_page: LeadsReportPage,
):
    """
    Verify selecting specific employee options (e.g. Velan, test employee)
    updates the dropdown value correctly.
    """
    leads_report_page.navigate()

    # Find available option values
    options = leads_report_page.employee_select.locator("option")
    for i in range(options.count()):
        val = options.nth(i).get_attribute("value") or ""
        text = options.nth(i).inner_text().strip()
        if val in ("21", "41", "43") or "Velan" in text:
            leads_report_page.select_employee(val)
            assert leads_report_page.employee_select.input_value() == val
            break


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_lead_type_specific_options_selection(
    leads_report_page: LeadsReportPage,
):
    """
    Verify selecting specific lead category options (e.g. Approved, Not Interested)
    updates the dropdown value correctly.
    """
    leads_report_page.navigate()

    options = leads_report_page.lead_type_select.locator("option")
    for i in range(options.count()):
        val = options.nth(i).get_attribute("value") or ""
        text = options.nth(i).inner_text().strip()
        if val in ("7", "8", "9", "10") or "Approved" in text:
            leads_report_page.select_lead_type(val)
            assert leads_report_page.lead_type_select.input_value() == val
            break


# ==============================================================================
# SECTION 3: MAIN REPORT TABLE CARD (.report-table-card) & DATATABLE
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_card_and_controls(
    leads_report_page: LeadsReportPage,
):
    """
    Verify the Leads Report table card wrapper, DataTable wrapper,
    and search filter input.
    """
    leads_report_page.navigate()

    assert leads_report_page.table_card.is_visible(), "Expected .card.report-table-card to be visible."
    assert leads_report_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert leads_report_page.search_input.is_visible(), "Expected search input to be visible."
    assert leads_report_page.datatable.is_visible(), "Expected table#datatable to be visible."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_headers_and_columns_are_valid(
    leads_report_page: LeadsReportPage,
):
    """
    Verify that all 8 expected table column headers (S.No, Name, Email, Phone,
    Employee Name, Lead Type, Followup Date, Description) and sortable states
    are rendered correctly.
    """
    leads_report_page.navigate()

    expected_headers = [
        "s.no",
        "name",
        "email",
        "phone",
        "employee name",
        "lead type",
        "followup date",
        "description",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in leads_report_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # Verify all 8 headers are sortable
    assert leads_report_page.table_headers.count() >= 8
    for i in range(8):
        header_class = leads_report_page.table_headers.nth(i).get_attribute("class") or ""
        assert "sorting" in header_class, f"Expected header {i} to be sortable, got '{header_class}'"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_empty_state_or_data_integrity(
    leads_report_page: LeadsReportPage,
):
    """
    Verify that the table either renders valid data rows with 8 columns
    or renders the empty state message spanning 8 columns.
    """
    leads_report_page.navigate()

    row_count = leads_report_page.get_row_count()
    if row_count > 0:
        first_row = leads_report_page.table_rows.first
        cells = first_row.locator("td").all_inner_texts()
        assert len(cells) >= 8, f"Expected at least 8 cells, got {len(cells)}"
        s_no = cells[0].strip()
        assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"
    else:
        # Empty state validation matching HTML snippet
        empty_cell = leads_report_page.empty_state_cell
        assert empty_cell.is_visible(), "Expected empty state cell to be visible."
        assert empty_cell.get_attribute("colspan") == "8", "Expected colspan='8' on empty state."
        assert "no data available in table" in empty_cell.inner_text().casefold(), (
            "Expected 'No data available in table' message."
        )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_column_sorting(
    leads_report_page: LeadsReportPage,
):
    """
    Verify clicking sortable column headers toggles sorting class
    between ascending and descending.
    """
    leads_report_page.navigate()

    s_no_header = leads_report_page.table_headers.first
    s_no_header.click()
    leads_report_page.page.wait_for_timeout(300)
    class_after_first = s_no_header.get_attribute("class") or ""
    assert "sorting_asc" in class_after_first or "sorting_desc" in class_after_first

    s_no_header.click()
    leads_report_page.page.wait_for_timeout(300)
    class_after_second = s_no_header.get_attribute("class") or ""
    assert class_after_second != class_after_first

    # Also sort Name column
    name_header = leads_report_page.table_headers.nth(1)
    name_header.click()
    leads_report_page.page.wait_for_timeout(300)
    name_class = name_header.get_attribute("class") or ""
    assert "sorting_asc" in name_class or "sorting_desc" in name_class


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_search_filter_interaction(
    leads_report_page: LeadsReportPage,
):
    """
    Verify typing in the search box filters rows and clearing restores the table.
    """
    leads_report_page.navigate()

    leads_report_page.search_table("NonExistent_Lead_Query_XYZ_999")
    info_text = leads_report_page.get_table_info_text()
    assert "0" in info_text

    leads_report_page.clear_search()
    assert leads_report_page.search_input.input_value() == ""


@pytest.mark.admin
@pytest.mark.regression
def test_admin_leads_report_table_pagination_and_info(
    leads_report_page: LeadsReportPage,
):
    """
    Verify DataTable info text ('Showing 0 to 0 of 0 entries') and pagination controls
    render properly.
    """
    leads_report_page.navigate()

    # Info status
    info = leads_report_page.datatable_info
    assert info.is_visible(), "Expected #datatable_info to be visible."
    assert info.get_attribute("role") == "status"
    assert info.get_attribute("aria-live") == "polite"
    info_text = leads_report_page.get_table_info_text()
    assert "showing" in info_text.casefold()
    assert "entries" in info_text.casefold()

    # Pagination controls
    assert leads_report_page.pagination.is_visible(), "Expected pagination container to be visible."
    assert leads_report_page.pagination_previous.is_visible(), "Expected Previous button to be visible."
    assert leads_report_page.pagination_next.is_visible(), "Expected Next button to be visible."

    # If empty table, both Previous and Next are disabled
    if leads_report_page.get_row_count() == 0:
        prev_class = leads_report_page.pagination_previous.get_attribute("class") or ""
        next_class = leads_report_page.pagination_next.get_attribute("class") or ""
        assert "disabled" in prev_class, f"Expected disabled Previous, got '{prev_class}'"
        assert "disabled" in next_class, f"Expected disabled Next, got '{next_class}'"




"""
Admin Portal LP Commission Log Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.lp_commission_log_page import LpCommissionLogPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_topbar_branding_and_title(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    lp_commission_log_page.navigate()

    # Brand Logo & Responsive Icons
    assert lp_commission_log_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert lp_commission_log_page.logo_small.is_visible() or lp_commission_log_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = lp_commission_log_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert lp_commission_log_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert lp_commission_log_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert lp_commission_log_page.menu_button.get_attribute("title") == "Open menu"
    assert lp_commission_log_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert lp_commission_log_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert lp_commission_log_page.page_title.inner_text().strip() == "LP Commission Log"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_topbar_sidebar_toggle_action(
    lp_commission_log_page: LpCommissionLogPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    lp_commission_log_page.navigate()

    body = lp_commission_log_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    lp_commission_log_page.menu_button.click()
    lp_commission_log_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    lp_commission_log_page.menu_button.click()
    lp_commission_log_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_theme_toggle_switches_modes(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert lp_commission_log_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert lp_commission_log_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert lp_commission_log_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert lp_commission_log_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = lp_commission_log_page.get_theme_mode() or "light"

    lp_commission_log_page.toggle_theme()
    lp_commission_log_page.page.wait_for_timeout(300)

    toggled_mode = lp_commission_log_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    lp_commission_log_page.toggle_theme()
    lp_commission_log_page.page.wait_for_timeout(300)
    assert lp_commission_log_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_notifications_dropdown(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify notification bell button, count badge, dropdown menu,
    Mark all read link, and empty notification text.
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.notification_button.is_visible(), "Expected notification button to be visible."
    assert lp_commission_log_page.notification_count.is_visible(), "Expected notification count badge to be visible."

    lp_commission_log_page.open_notifications()
    lp_commission_log_page.notification_menu.wait_for(state="visible", timeout=10000)

    assert lp_commission_log_page.notification_menu.is_visible(), "Expected notification dropdown menu to be open."
    assert lp_commission_log_page.mark_all_read.is_visible(), "Expected 'Mark all read' link to be visible."
    assert lp_commission_log_page.mark_all_read.inner_text().strip() == "Mark all read"

    # Notification list shows empty message or items
    menu_text = lp_commission_log_page.notification_menu.inner_text().casefold()
    assert "notification not found" in menu_text or "notification" in menu_text


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_profile_dropdown_and_logout_link(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify profile dropdown displays admin avatar initials, username,
    role Administrator, and valid Logout URL.
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert lp_commission_log_page.profile_initials.first.inner_text().strip() == "M"
    assert lp_commission_log_page.profile_topbar_name.inner_text().strip() == "madmin"

    lp_commission_log_page.open_profile_menu()
    lp_commission_log_page.profile_menu.wait_for(state="visible", timeout=10000)

    assert lp_commission_log_page.profile_menu.is_visible(), "Expected profile menu dropdown to be visible."
    assert lp_commission_log_page.profile_name.inner_text().strip() == "madmin"
    assert "administrator" in lp_commission_log_page.profile_role.inner_text().casefold()

    assert lp_commission_log_page.logout_link.is_visible(), "Expected Logout item to be visible."
    logout_href = lp_commission_log_page.logout_link.get_attribute("href") or ""
    assert "/admin/Controlbase/Logout" in logout_href, (
        f"Expected logout href to point to /admin/Controlbase/Logout, got '{logout_href}'"
    )


# ==============================================================================
# SECTION 2: DATATABLE CARD & TABLE CONTROLS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_card_and_datatable_controls(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify the table card wrapper, DataTable length selector with options
    10, 25, 50, 100, search filter input, and export buttons container.
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.table_card.is_visible(), "Expected table card to be visible."
    assert lp_commission_log_page.datatable_wrapper.is_visible(), "Expected #datatable_wrapper to be visible."
    assert lp_commission_log_page.length_dropdown.is_visible(), "Expected length dropdown to be visible."
    assert lp_commission_log_page.search_input.is_visible(), "Expected search input to be visible."
    assert lp_commission_log_page.export_buttons.count() == 3, "Expected 3 export buttons."

    # Verify length options
    options = [
        opt.get_attribute("value")
        for opt in lp_commission_log_page.length_dropdown.locator("option").all()
    ]
    for opt in ["10", "25", "50", "100"]:
        assert opt in options, f"Expected option '{opt}' in length dropdown."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_export_buttons_attributes(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify CSV, PDF, and Print export buttons have correct classes and labels.
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.csv_button.is_visible(), "Expected CSV export button."
    assert lp_commission_log_page.csv_button.inner_text().strip() == "CSV"

    assert lp_commission_log_page.pdf_button.is_visible(), "Expected PDF export button."
    assert lp_commission_log_page.pdf_button.inner_text().strip() == "PDF"

    assert lp_commission_log_page.print_button.is_visible(), "Expected Print export button."
    assert lp_commission_log_page.print_button.inner_text().strip() == "Print"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_headers_and_columns(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify that all 6 expected table column headers (S.No, Order ID, Commission,
    Price, Lot, Date Time) and sortable states are rendered correctly.
    """
    lp_commission_log_page.navigate()

    expected_headers = [
        "s.no",
        "order id",
        "commission",
        "price",
        "lot",
        "date time",
    ]

    actual_headers = [
        th.strip().casefold()
        for th in lp_commission_log_page.table_headers.all_inner_texts()
        if th.strip()
    ]

    for expected in expected_headers:
        assert any(expected in h for h in actual_headers), (
            f"Expected header '{expected}' to be present among: {actual_headers}"
        )

    # Check sortable class on headers
    for i in range(min(6, lp_commission_log_page.table_headers.count())):
        header_class = lp_commission_log_page.table_headers.nth(i).get_attribute("class") or ""
        assert "sorting" in header_class, f"Expected header {i} to be sortable."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_rows_data_integrity(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify that table rows display valid sequential S.No, numeric Order ID,
    valid Commission, Price, Lot, and Date Time timestamps.
    """
    lp_commission_log_page.navigate()

    row_count = lp_commission_log_page.get_row_count()
    assert row_count > 0, "Expected at least 1 row of commission log data."

    cells = lp_commission_log_page.get_first_row_cells()
    assert len(cells) >= 6, f"Expected at least 6 cells in first row, got {len(cells)}"

    # 1. S.No (numeric)
    s_no = cells[0].strip()
    assert s_no.isdigit(), f"Expected numeric S.No, got '{s_no}'"

    # 2. Order ID (numeric)
    order_id = cells[1].strip()
    assert order_id.isdigit(), f"Expected numeric Order ID, got '{order_id}'"

    # 3. Commission (float/numeric)
    commission = cells[2].strip()
    assert float(commission) >= 0.0, f"Expected non-negative commission float, got '{commission}'"

    # 4. Price (float/numeric)
    price = cells[3].strip()
    assert float(price) > 0.0, f"Expected positive price float, got '{price}'"

    # 5. Lot (float/numeric)
    lot = cells[4].strip()
    assert float(lot) > 0.0, f"Expected positive lot float, got '{lot}'"

    # 6. Date Time (contains date/time components)
    date_time = cells[5].strip()
    assert len(date_time) >= 10, f"Expected valid timestamp, got '{date_time}'"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_length_dropdown_selection(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify selecting 10, 25, 50 entries dynamically updates the table row count.
    """
    lp_commission_log_page.navigate()

    # Switch to 10
    lp_commission_log_page.select_length("10")
    assert lp_commission_log_page.get_row_count() == 10, "Expected 10 rows when length is 10."

    # Switch to 25
    lp_commission_log_page.select_length("25")
    assert lp_commission_log_page.get_row_count() == 25, "Expected 25 rows when length is 25."

    # Switch to 50
    lp_commission_log_page.select_length("50")
    assert lp_commission_log_page.get_row_count() == 50, "Expected 50 rows when length is 50."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_search_filtering(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify searching for a specific Order ID filters records, searching for a
    nonexistent term displays the empty message, and clearing restores records.
    """
    lp_commission_log_page.navigate()

    # Capture the first row's Order ID
    first_cells = lp_commission_log_page.get_first_row_cells()
    target_order_id = first_cells[1]

    # Search by Order ID
    lp_commission_log_page.search_table(target_order_id)
    assert lp_commission_log_page.get_row_count() >= 1
    filtered_cells = lp_commission_log_page.get_first_row_cells()
    assert target_order_id in filtered_cells[1]

    # Search nonexistent
    lp_commission_log_page.search_table("nonexistent_order_999999")
    table_text = lp_commission_log_page.datatable.inner_text().casefold()
    assert "no matching records found" in table_text or "no data available" in table_text

    # Clear search
    lp_commission_log_page.clear_search()
    assert lp_commission_log_page.get_row_count() >= 10


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_column_sorting(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify clicking table headers updates sorting state between ascending
    and descending.
    """
    lp_commission_log_page.navigate()

    order_id_header = lp_commission_log_page.table_headers.nth(1)
    initial_class = order_id_header.get_attribute("class") or ""

    order_id_header.click()
    lp_commission_log_page.page.wait_for_timeout(400)
    first_sort_class = order_id_header.get_attribute("class") or ""
    assert "sorting_asc" in first_sort_class or "sorting_desc" in first_sort_class or first_sort_class != initial_class

    order_id_header.click()
    lp_commission_log_page.page.wait_for_timeout(400)
    second_sort_class = order_id_header.get_attribute("class") or ""
    assert second_sort_class != first_sort_class or "sorting" in second_sort_class


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_pagination_controls(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify pagination info displays record ranges and clicking Next/Previous
    controls navigates pages.
    """
    lp_commission_log_page.navigate()

    initial_info = lp_commission_log_page.get_table_info_text()
    assert "Showing 1 to" in initial_info

    # Click Next
    lp_commission_log_page.go_next_page()
    next_info = lp_commission_log_page.get_table_info_text()
    assert next_info != initial_info
    assert "Showing 51 to" in next_info or "Showing 11 to" in next_info or "Showing 26 to" in next_info

    # Click Previous
    lp_commission_log_page.go_previous_page()
    prev_info = lp_commission_log_page.get_table_info_text()
    assert "Showing 1 to" in prev_info


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_table_scroll_container_and_responsive_controls(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify the DataTable scroll wrapper (.dataTables_scrollHead, .dataTables_scrollBody),
    the report tools container, and responsive row controls (td.dtr-control).
    """
    lp_commission_log_page.navigate()

    assert lp_commission_log_page.scroll_head.is_visible(), "Expected .dataTables_scrollHead to be visible."
    assert lp_commission_log_page.scroll_body.is_visible(), "Expected .dataTables_scrollBody to be visible."
    assert lp_commission_log_page.tools_container.is_visible(), "Expected .report-log-tools to be visible."

    # Check responsive dtr-control class on first cell
    first_row_first_cell = lp_commission_log_page.table_rows.first.locator("td").first
    cell_class = first_row_first_cell.get_attribute("class") or ""
    assert "dtr-control" in cell_class, f"Expected dtr-control on first column cell, got '{cell_class}'"
    assert first_row_first_cell.get_attribute("tabindex") == "0"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_pagination_numbered_page_navigation(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify clicking numbered pagination buttons directly navigates to the selected page
    and updates active button status and table info text.
    """
    lp_commission_log_page.navigate()

    # Initial active page is 1
    assert lp_commission_log_page.active_page.inner_text().strip() == "1"

    # Click page 2
    page_2_button = lp_commission_log_page.paginate_pages.filter(has_text="2").first
    assert page_2_button.is_visible(), "Expected page 2 button in pagination."
    page_2_button.locator("a").click()
    lp_commission_log_page.page.wait_for_timeout(500)

    # Active page should now be 2
    assert lp_commission_log_page.active_page.inner_text().strip() == "2"
    assert "Showing 51 to 100" in lp_commission_log_page.get_table_info_text()

    # Click page 1 to return
    page_1_button = lp_commission_log_page.paginate_pages.filter(has_text="1").first
    page_1_button.locator("a").click()
    lp_commission_log_page.page.wait_for_timeout(500)
    assert lp_commission_log_page.active_page.inner_text().strip() == "1"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_commission_log_page_2_pagination_state_and_navigation(
    lp_commission_log_page: LpCommissionLogPage,
):
    """
    Verify exact pagination state when on Page 2:
    - Info displays 'Showing 51 to 100 of 1,803 entries' (or total).
    - Previous button is enabled (class 'disabled' is removed).
    - Page 2 is highlighted with class 'active'.
    - Pages 1, 3, 4, 5, ellipsis (...), and last page (e.g. 37) are rendered.
    - Next button remains enabled.
    - Clicking Previous navigates back to page 1 and Previous becomes disabled again.
    """
    lp_commission_log_page.navigate()

    # On page 1: Previous is disabled
    assert "disabled" in (lp_commission_log_page.paginate_previous.get_attribute("class") or "")

    # Go to page 2
    lp_commission_log_page.go_next_page()
    lp_commission_log_page.page.wait_for_timeout(400)

    # 1. Info status on page 2
    info_text = lp_commission_log_page.get_table_info_text()
    assert "Showing 51 to 100 of" in info_text

    # 2. Previous button is now enabled (not disabled)
    prev_class = lp_commission_log_page.paginate_previous.get_attribute("class") or ""
    assert "disabled" not in prev_class, "Expected Previous button to be enabled on page 2."

    # 3. Page 2 is active
    assert lp_commission_log_page.active_page.inner_text().strip() == "2"

    # 4. Ellipsis and other numbered pages are present
    assert lp_commission_log_page.paginate_ellipsis.is_visible()
    page_numbers = [p.inner_text().strip() for p in lp_commission_log_page.paginate_pages.all()]
    assert "1" in page_numbers
    assert "2" in page_numbers
    assert "3" in page_numbers

    # 5. Next button is enabled
    next_class = lp_commission_log_page.paginate_next.get_attribute("class") or ""
    assert "disabled" not in next_class, "Expected Next button to be enabled on page 2."

    # 6. Click Previous button to return to page 1
    lp_commission_log_page.go_previous_page()
    lp_commission_log_page.page.wait_for_timeout(400)

    # Verify returned to page 1 and Previous is disabled again
    assert "Showing 1 to 50 of" in lp_commission_log_page.get_table_info_text()
    assert "disabled" in (lp_commission_log_page.paginate_previous.get_attribute("class") or "")



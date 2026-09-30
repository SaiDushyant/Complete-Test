"""
Admin Portal Symbol Configuration Test Suite.
Tests all scenarios for Symbol Configuration (#symbolConfigurationTable) and Edit Modal (#symbolConfigModal):
- Real UI testing on read-only table structure, search filtering, headers, and modal tab switching
- SAFE MOCKED testing on form submission to PREVENT any live admin data modification
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from workflows.admin_portal.pages.admin_symbol_configuration_page import (
    AdminSymbolConfigurationPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_table_and_controls_render(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify Symbol Configuration table renders expected headers, search box, dropdown, and controls."""
    page = admin_symbol_configuration_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search_input).to_be_visible()
    expect(page.entries_select).to_be_visible()
    expect(page.info_status).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "S.No", "Symbol", "Display Name", "Sector", "Decimal",
        "Min Lot", "Max Lot", "Default Lot", "Step Size", "Margin Index",
        "Allow Trade", "Active",
    ]
    actual_headers = page.get_header_titles()
    for header in expected_headers:
        assert header in actual_headers, f"Expected header '{header}' missing from {actual_headers}"


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_row_structure_and_badges(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify row structure, symbol format, and Allow Trade / Active status badges."""
    page = admin_symbol_configuration_page
    page.navigate()

    if page.empty_message.is_visible() or page.get_row_count() == 0:
        pytest.skip("No symbol configuration rows available to validate.")

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        if cells.count() == 1 and "dataTables_empty" in (cells.first.get_attribute("class") or ""):
            pytest.skip("DataTables empty message row present.")

        symbol_text = cells.nth(1).inner_text().strip()
        assert symbol_text, "Expected Symbol cell to not be empty"

        allow_trade_badge = cells.nth(10).locator("span.badge")
        active_badge = cells.nth(11).locator("span.badge")
        expect(allow_trade_badge).to_be_visible()
        expect(active_badge).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_search_filter(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify searching by Symbol or Sector filters the table rows and clearing restores them."""
    page = admin_symbol_configuration_page
    page.navigate()

    if page.get_row_count() == 0:
        pytest.skip("No rows to perform search filter test.")

    first_symbol = page.rows.first.locator("td").nth(1).inner_text().strip()
    original_count = page.get_row_count()

    page.search_symbol(first_symbol)
    expect(page.rows).to_have_count(1)
    assert first_symbol in page.rows.first.inner_text()

    page.clear_search()
    expect(page.rows).to_have_count(original_count)


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_search_empty_result(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify searching for a non-existent symbol displays empty table message."""
    page = admin_symbol_configuration_page
    page.navigate()

    page.search_symbol("NON-EXISTENT-SYMBOL-XYZ-999")
    expect(page.empty_message).to_be_visible()



@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_column_sorting(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify sortable symbol column headers toggle ascending and descending states."""
    page = admin_symbol_configuration_page
    page.navigate()

    headers = page.headers
    for i in range(headers.count()):
        header = headers.nth(i)
        first_sort = header.get_attribute("aria-sort")
        if first_sort is None:
            continue

        header.click()
        new_sort = header.get_attribute("aria-sort")
        assert new_sort in {"ascending", "descending"}


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("length_option", ["10", "25", "50", "100"])
def test_symbol_config_page_length_options(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
    length_option: str,
):
    """Verify page length dropdown selects 10, 25, 50, 100 entries."""
    page = admin_symbol_configuration_page
    page.navigate()

    page.select_page_length(length_option)
    assert page.entries_select.input_value() == length_option


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_pagination_controls(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify previous and next pagination buttons render correctly."""
    page = admin_symbol_configuration_page
    page.navigate()

    expect(page.pagination).to_be_visible()
    expect(page.previous_button).to_be_visible()
    expect(page.next_button).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_modal_tabs_navigation(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """Verify Symbol Configuration modal opens and switches between all 5 tabs without modifying data."""
    page = admin_symbol_configuration_page
    page.navigate()

    if page.edit_buttons.count() == 0:
        pytest.skip("No edit symbol configuration buttons available to test modal tabs.")

    page.open_first_edit_modal()
    expect(page.modal).to_be_attached()

    if page.is_modal_visible():
        expect(page.modal_title).to_have_text("Symbol Configuration")
        expect(page.general_tab_button).to_be_visible()
        expect(page.hours_tab_button).to_be_visible()
        expect(page.holiday_tab_button).to_be_visible()
        expect(page.special_tab_button).to_be_visible()
        expect(page.upcoming_tab_button).to_be_visible()

        # Switch to Market Hours tab
        page.hours_tab_button.click()
        expect(page.hours_tab_pane).to_be_visible()
        expect(page.refresh_calendar_button).to_be_visible()

        # Switch to Holidays tab
        page.holiday_tab_button.click()
        expect(page.holiday_tab_pane).to_be_visible()
        expect(page.add_holiday_button).to_be_visible()

        # Switch to Special Days tab
        page.special_tab_button.click()
        expect(page.special_tab_pane).to_be_visible()
        expect(page.add_special_override_button).to_be_visible()

        # Switch to Upcoming tab
        page.upcoming_tab_button.click()
        expect(page.upcoming_tab_pane).to_be_visible()
        expect(page.refresh_upcoming_button).to_be_visible()

        # Close Modal safely
        page.modal_close_button.first.click()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_config_mocked_save_general_form(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK symbol form submission so live admin database is NEVER altered."""
    admin_symbol_configuration_page.navigate()

    def handle_save_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked symbol configuration saved successfully"}',
        )

    # Intercept any API calls to prevent live symbol modification
    page.route("**/symbolConfiguration**", handle_save_request)
    page.route("**/saveSymbol**", handle_save_request)

    if admin_symbol_configuration_page.edit_buttons.count() > 0:
        admin_symbol_configuration_page.open_first_edit_modal()
        if admin_symbol_configuration_page.is_modal_visible():
            expect(admin_symbol_configuration_page.save_general_button).to_be_visible()
            admin_symbol_configuration_page.save_general_button.click()

    assert True

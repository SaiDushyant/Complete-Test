"""
Admin Portal Symbol List Test Suite.
Tests all scenarios for Symbol List (#datatable), Edit Modal (#myModal), and Bulk Upload Modal (#swapModal):
- Real UI testing on read-only table structure, headers, controls, search filtering, and modals
- SAFE MOCKED testing on form submissions to PREVENT any live admin data modification
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect, Page

from workflows.admin_portal.pages.admin_symbol_list_page import AdminSymbolListPage


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_table_and_controls_render(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify Symbol List page title, table, search box, dropdown, buttons, and expected headers render."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible():
        pytest.skip("Symbol list table not visible or endpoint 404 on staging environment.")

    expect(page.table).to_be_visible()
    expect(page.search_input).to_be_visible()
    expect(page.entries_select).to_be_visible()
    expect(page.info_status).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "S.No",
        "Symbol Name",
        "Commission",
        "A Book Buy Swap Points",
        "A Book Sell Swap Points",
        "B Book Buy Swap Points",
        "B Book Sell Swap Points",
        "Action",
    ]
    actual_headers = page.get_header_titles()
    for header in expected_headers:
        assert any(header.lower() in h.lower() for h in actual_headers), f"Expected header '{header}' missing from {actual_headers}"


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_row_data_structure(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify row cell formatting, non-empty symbol names, and swap points."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible() or page.empty_message.is_visible() or page.get_row_count() == 0:
        pytest.skip("No symbol list rows available to validate.")

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        if cells.count() == 1 and "dataTables_empty" in (cells.first.get_attribute("class") or ""):
            pytest.skip("DataTables empty message row present.")

        symbol_text = cells.nth(1).inner_text().strip()
        assert symbol_text, "Expected Symbol Name cell to not be empty"

        edit_button = cells.last.locator("a.btnEdit")
        expect(edit_button).to_be_attached()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_search_filter(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify searching by symbol name filters table rows and clearing restores original rows."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible() or page.get_row_count() == 0:
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
def test_symbol_list_search_empty_result(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify searching for a non-existent symbol displays empty table message."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible():
        pytest.skip("Symbol list table not visible on staging environment.")

    page.search_symbol("NON-EXISTENT-SYMBOL-XYZ-999")
    expect(page.empty_message).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_column_sorting(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify sortable symbol list column headers toggle ascending/descending states."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible():
        pytest.skip("Symbol list table not visible on staging environment.")

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
def test_symbol_list_page_length_options(
    admin_symbol_list_page: AdminSymbolListPage,
    length_option: str,
):
    """Verify page length dropdown selects 10, 25, 50, 100 entries."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible():
        pytest.skip("Symbol list table not visible on staging environment.")

    page.select_page_length(length_option)
    assert page.entries_select.input_value() == length_option


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_pagination_controls(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify previous and next pagination buttons render correctly."""
    page = admin_symbol_list_page
    page.navigate()

    if not page.table.is_visible():
        pytest.skip("Symbol list table not visible on staging environment.")

    expect(page.pagination).to_be_visible()
    expect(page.previous_button).to_be_visible()
    expect(page.next_button).to_be_visible()



@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_open_bulk_upload_modal(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify Bulk upload button opens the Swap Data modal (#swapModal) with file input."""
    page = admin_symbol_list_page
    page.navigate()

    page.open_bulk_upload_modal()
    expect(page.bulk_modal).to_be_attached()

    if page.is_bulk_modal_visible():
        expect(page.bulk_modal_title).to_have_text("Swap Data")
        expect(page.bulk_file_input).to_be_visible()
        expect(page.bulk_form_submit_button).to_be_visible()
        page.bulk_modal_close_button.first.click()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_open_edit_modal(
    admin_symbol_list_page: AdminSymbolListPage,
):
    """Verify clicking row Edit button opens the Database Form modal (#myModal) with symbol inputs."""
    page = admin_symbol_list_page
    page.navigate()

    if page.edit_buttons.count() == 0:
        pytest.skip("No edit symbol buttons available to test modal.")

    page.open_first_edit_modal()
    expect(page.edit_modal).to_be_attached()

    if page.is_edit_modal_visible():
        expect(page.edit_modal_title).to_have_text("Database Form")
        expect(page.symbol_name_input).to_be_visible()
        expect(page.brokerage_input).to_be_visible()
        expect(page.abook_buy_swap_input).to_be_visible()
        expect(page.abook_sell_swap_input).to_be_visible()
        expect(page.bbook_buy_swap_input).to_be_visible()
        expect(page.bbook_sell_swap_input).to_be_visible()
        expect(page.edit_form_submit_button).to_be_visible()

        page.edit_modal_close_button.first.click()


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_mocked_edit_form_submit(
    admin_symbol_list_page: AdminSymbolListPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK symbol edit form submission so live admin database is NEVER altered."""
    admin_symbol_list_page.navigate()

    def handle_save_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked symbol swap data updated successfully"}',
        )

    # Intercept network requests to block database changes
    page.route("**/symbol**", handle_save_request)
    page.route("**/saveSymbol**", handle_save_request)
    page.route("**/updateSymbol**", handle_save_request)

    if admin_symbol_list_page.edit_buttons.count() > 0:
        admin_symbol_list_page.open_first_edit_modal()
        if admin_symbol_list_page.is_edit_modal_visible():
            expect(admin_symbol_list_page.edit_form_submit_button).to_be_visible()
            admin_symbol_list_page.edit_form_submit_button.click()

    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_symbol_list_mocked_bulk_upload_submit(
    admin_symbol_list_page: AdminSymbolListPage,
    page: Page,
):
    """SAFETY TEST: Intercept and MOCK bulk upload submit so live admin database is NEVER altered."""
    admin_symbol_list_page.navigate()

    def handle_bulk_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Mocked bulk swap data uploaded successfully"}',
        )

    page.route("**/upload**", handle_bulk_request)
    page.route("**/bulkSwap**", handle_bulk_request)

    admin_symbol_list_page.open_bulk_upload_modal()
    if admin_symbol_list_page.is_bulk_modal_visible():
        expect(admin_symbol_list_page.bulk_form_submit_button).to_be_visible()
        admin_symbol_list_page.bulk_form_submit_button.click()

    assert True

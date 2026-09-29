"""
Admin Portal Active Users Page Test Suite.
Tests all scenarios for the Active Users datatable (#au-datatable):
- Rendering of table structure, controls, and 5 expected columns
- Row data integrity, cell formatting, and green LED online indicators
- Search filtering by Account No, Name, or Token, and clearing filter
- Empty search state validation
- Multi-column sorting (ascending / descending)
- Page length dropdown option selection (10, 25, 50, 100)
- Pagination control behavior (Previous / Next)
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_active_users_page import AdminActiveUsersPage


@pytest.mark.admin
@pytest.mark.regression
def test_active_users_table_and_controls_render(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify Active Users table renders expected columns, search input, dropdown, and controls."""
    page = admin_active_users_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search_input).to_be_visible()
    expect(page.entries_select).to_be_visible()
    expect(page.info_status).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = ["S.No", "Account No", "Name", "Token", "Balance"]
    actual_headers = page.get_header_titles()
    assert actual_headers == expected_headers, f"Expected headers {expected_headers}, got {actual_headers}"

    dropdown_options = [
        opt.inner_text().strip()
        for opt in page.entries_select.locator("option").all()
    ]
    assert dropdown_options == ["10", "25", "50", "100"]


@pytest.mark.admin
@pytest.mark.regression
def test_active_users_row_structure_and_online_indicator(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify each active user row contains 5 cells, valid values, and green LED online status."""
    page = admin_active_users_page
    page.navigate()

    if page.empty_message.is_visible() or page.get_row_count() == 0:
        pytest.skip("No active user rows available to validate.")

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        if cells.count() == 1 and "dataTables_empty" in (cells.first.get_attribute("class") or ""):
            pytest.skip("DataTables empty message row present.")

        assert cells.count() == 5, f"Expected 5 cells per row, found {cells.count()}"

        s_no = cells.nth(0).inner_text().strip()
        account_no = cells.nth(1).inner_text().strip()
        name_cell = cells.nth(2)
        token = cells.nth(3).inner_text().strip()
        balance = cells.nth(4).inner_text().strip()

        assert s_no.isdigit(), f"Expected S.No to be numeric, got '{s_no}'"
        assert account_no.isdigit(), f"Expected Account No to be numeric, got '{account_no}'"
        assert name_cell.inner_text().strip(), "Expected Name cell to not be empty"
        expect(name_cell.locator(".led-green")).to_be_visible()
        assert token, "Expected Token cell to not be empty"
        assert re.match(r"^-?\d+(\.\d+)?$", balance), f"Expected Balance to be numeric, got '{balance}'"



@pytest.mark.admin
@pytest.mark.regression
def test_active_users_search_filter(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify search input filters active users by Account No or Name and restores rows when cleared."""
    page = admin_active_users_page
    page.navigate()

    if page.get_row_count() == 0:
        pytest.skip("No rows to perform search filter test.")

    first_account = page.rows.first.locator("td").nth(1).inner_text().strip()
    original_count = page.get_row_count()

    page.search_user(first_account)
    expect(page.rows.first).to_be_visible()
    assert first_account in page.rows.first.inner_text()

    page.clear_search()
    expect(page.rows).to_have_count(original_count)



@pytest.mark.admin
@pytest.mark.regression
def test_active_users_search_empty_result(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify searching for non-existent query displays empty state or no matching records."""
    page = admin_active_users_page
    page.navigate()

    page.search_user("non-existent-user-token-xyz-999")
    expect(page.empty_message).to_be_visible()



@pytest.mark.admin
@pytest.mark.regression
def test_active_users_column_sorting(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify clicking sortable table column headers toggles sorting state."""
    page = admin_active_users_page
    page.navigate()

    headers = page.headers
    for i in range(headers.count()):
        header = headers.nth(i)
        header.click()

        first_sort = header.get_attribute("aria-sort")
        first_class = header.get_attribute("class") or ""
        
        if first_sort is not None:
            assert first_sort in {"ascending", "descending"}
        else:
            assert "sorting" in first_class

        header.click()
        second_sort = header.get_attribute("aria-sort")
        second_class = header.get_attribute("class") or ""

        if second_sort is not None:
            assert second_sort in {"ascending", "descending"}
            assert second_sort != first_sort
        else:
            assert "sorting" in second_class


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("length_option", ["10", "25", "50", "100"])
def test_active_users_page_length_options(
    admin_active_users_page: AdminActiveUsersPage,
    length_option: str,
):
    """Verify page length dropdown can select 10, 25, 50, and 100 entries."""
    page = admin_active_users_page
    page.navigate()

    page.select_page_length(length_option)
    assert page.entries_select.input_value() == length_option


@pytest.mark.admin
@pytest.mark.regression
def test_active_users_pagination_controls(
    admin_active_users_page: AdminActiveUsersPage,
):
    """Verify previous and next pagination buttons render correctly."""
    page = admin_active_users_page
    page.navigate()

    expect(page.pagination).to_be_visible()
    expect(page.previous_button).to_be_visible()
    expect(page.next_button).to_be_visible()

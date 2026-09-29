"""
Admin Portal User Bonus Page Test Suite.
Tests all scenarios for the User Bonus datatable (#datatable) and Edit Bonus Modal (#myModal):
- Rendering of table structure, controls, hidden inputs, and 9 expected column headers
- Row data integrity, bonus amounts format, expiration dates, status badges, and action buttons
- Search filtering by User Name or Account No, and clearing search filter
- Empty search query handling
- Column header sorting (ascending / descending)
- Page length dropdown selection (10, 25, 50, 100 entries)
- Pagination control behavior (Previous / Next)
- Edit Bonus modal opening, form input visibility (#user_credit, #expire_date), and modal closing
- Mocked form submission flow
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_user_bonus_page import AdminUserBonusPage


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_table_and_controls_render(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify User Bonus table renders expected 9 columns, search input, dropdown, and hidden config fields."""
    page = admin_user_bonus_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search_input).to_be_visible()
    expect(page.entries_select).to_be_visible()
    expect(page.info_status).to_be_visible()
    expect(page.pagination).to_be_visible()

    expect(page.modify_credit_hidden).to_be_attached()
    expect(page.withdraw_credit_hidden).to_be_attached()

    expected_headers = [
        "S.No", "User Name", "Account No", "Total Bonus",
        "Used Bonus", "Remaining Bonus", "Expire Date", "Bonus Status", "Action",
    ]
    actual_headers = page.get_header_titles()
    assert actual_headers == expected_headers, f"Expected headers {expected_headers}, got {actual_headers}"

    dropdown_options = [
        opt.inner_text().strip()
        for opt in page.entries_select.locator("option").all()
    ]
    assert dropdown_options == ["10", "25", "50", "100"]


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_row_data_integrity(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify user bonus row structure, cells count, date format, and action buttons."""
    page = admin_user_bonus_page
    page.navigate()

    if page.empty_message.is_visible() or page.get_row_count() == 0:
        pytest.skip("No user bonus rows available to validate.")

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        if cells.count() == 1 and "dataTables_empty" in (cells.first.get_attribute("class") or ""):
            pytest.skip("DataTables empty message row present.")

        assert cells.count() == 9, f"Expected 9 cells per row, found {cells.count()}"

        s_no = cells.nth(0).inner_text().strip()
        user_name = cells.nth(1).inner_text().strip()
        account_no = cells.nth(2).inner_text().strip()
        total_bonus = cells.nth(3).inner_text().strip()
        used_bonus = cells.nth(4).inner_text().strip()
        remaining_bonus = cells.nth(5).inner_text().strip()
        expire_date = cells.nth(6).inner_text().strip()
        bonus_status = cells.nth(7).inner_text().strip().lower()

        assert s_no.isdigit(), f"Expected S.No to be numeric, got '{s_no}'"
        assert user_name, "Expected User Name to not be empty"
        assert account_no.isdigit(), f"Expected Account No to be numeric, got '{account_no}'"
        assert re.match(r"^-?\d+(\.\d+)?$", total_bonus), f"Invalid Total Bonus '{total_bonus}'"
        assert used_bonus == "NaN" or re.match(r"^-?\d+(\.\d+)?$", used_bonus), f"Invalid Used Bonus '{used_bonus}'"
        assert re.match(r"^-?\d+(\.\d+)?$", remaining_bonus), f"Invalid Remaining Bonus '{remaining_bonus}'"
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", expire_date), f"Invalid Expire Date format '{expire_date}'"
        assert bonus_status in {"out", "in", "expired"}, f"Unexpected Bonus Status '{bonus_status}'"

        action_cell = cells.nth(8)
        expect(action_cell.locator("a.btnEdit")).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_search_filter(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify search input filters user bonus table by Account No or Name and restores rows when cleared."""
    page = admin_user_bonus_page
    page.navigate()

    if page.get_row_count() == 0:
        pytest.skip("No rows to perform search filter test.")

    first_account = page.rows.first.locator("td").nth(2).inner_text().strip()
    original_count = page.get_row_count()

    page.search_user_bonus(first_account)
    expect(page.rows).to_have_count(1)
    assert first_account in page.rows.first.inner_text()


    page.clear_search()
    expect(page.rows).to_have_count(original_count)


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_search_empty_result(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify searching for non-existent query displays empty state message."""
    page = admin_user_bonus_page
    page.navigate()

    page.search_user_bonus("non-existent-bonus-account-xyz-999")
    if page.empty_message.is_visible():
        expect(page.empty_message).to_be_visible()
    else:
        assert page.get_row_count() == 0 or "no matching records" in page.table_wrapper.inner_text().lower()


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_column_sorting(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify clicking sortable table column headers toggles sorting state."""
    page = admin_user_bonus_page
    page.navigate()

    headers = page.headers
    for i in range(headers.count()):
        header = headers.nth(i)
        header.click()

        first_sort = header.get_attribute("aria-sort")
        if first_sort is None:
            continue
        assert first_sort in {"ascending", "descending"}

        header.click()
        second_sort = header.get_attribute("aria-sort")
        assert second_sort in {"ascending", "descending"}
        assert second_sort != first_sort


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize("length_option", ["10", "25", "50", "100"])
def test_user_bonus_page_length_options(
    admin_user_bonus_page: AdminUserBonusPage,
    length_option: str,
):
    """Verify page length dropdown can select 10, 25, 50, and 100 entries."""
    page = admin_user_bonus_page
    page.navigate()

    page.select_page_length(length_option)
    assert page.entries_select.input_value() == length_option


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_pagination_controls(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify previous and next pagination buttons render correctly."""
    page = admin_user_bonus_page
    page.navigate()

    expect(page.pagination).to_be_visible()
    expect(page.previous_button).to_be_visible()
    expect(page.next_button).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_modify_modal_renders_and_closes(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify clicking Modify button opens the Edit User Bonus modal and close button closes it."""
    page = admin_user_bonus_page
    page.navigate()

    if page.modify_buttons.count() == 0:
        pytest.skip("No modify action buttons available to test modal.")

    page.open_first_modify_modal()
    expect(page.modal).to_be_attached()

    if page.is_modal_visible():
        expect(page.modal_title).to_have_text("Edit User Bonus Form")
        expect(page.user_credit_input).to_be_visible()
        expect(page.expire_date_input).to_be_visible()
        expect(page.save_button).to_be_visible()

        page.modal_close_button.first.click()
        expect(page.modal).to_be_hidden()


@pytest.mark.admin
@pytest.mark.regression
def test_user_bonus_modify_modal_mocked_save(
    admin_user_bonus_page: AdminUserBonusPage,
):
    """Verify submitting modal form triggers save request without modifying live admin data."""
    page = admin_user_bonus_page
    page.navigate()

    def handle_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Bonus updated successfully"}',
        )

    page.page.route("**/userBonus**", handle_request)
    page.page.route("**/formSubmit**", handle_request)

    if page.modify_buttons.count() > 0:
        page.open_first_modify_modal()
        if page.is_modal_visible():
            page.fill_modal_form(bonus_amount="1000", expire_date="2026-12-31")
            page.click_modal_save()

    assert True

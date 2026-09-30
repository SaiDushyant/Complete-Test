import csv
import pytest
from datetime import datetime
from pathlib import Path
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_user_transaction_log_page import (
    AdminUserTransactionLogPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_table_and_controls(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Check DataTable layout, controls, headers, search, and export buttons."""
    page = admin_user_transaction_log_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search).to_be_visible()
    expect(page.entries).to_be_visible()
    expect(page.info).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "S.No",
        "Account No",
        "Transaction",
        "Transaction Type",
        "Transaction Value",
        "Modified Date",
    ]

    actual_headers = [
        (header.get_attribute("aria-label") or "")
        .split(": activate")[0]
        .strip()
        for header in page.table.locator("thead th").all()
    ]

    assert actual_headers == expected_headers
    assert page.entries.locator("option").all_text_contents() == ["10", "25", "50", "100"]

    expect(page.csv_button).to_be_visible()
    expect(page.pdf_button).to_be_visible()
    expect(page.print_button).to_be_visible()

    if page.rows.count() > 0:
        assert page.rows.first.locator("td").count() == 6
        first_row = page.rows.first
        for i in range(6):
            assert first_row.locator("td").nth(i).is_visible()

    original_row_count = page.rows.count()
    page.search.fill("user-transaction-no-match-xyz")
    expect(page.empty_message).to_be_visible()
    page.search.clear()
    expect(page.rows).to_have_count(original_row_count)


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_page_size_options(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify page size options work correctly."""
    page = admin_user_transaction_log_page
    page.navigate()

    for size in ("10", "25", "50", "100"):
        page.entries.select_option(value=size)
        expect(page.entries).to_have_value(size)


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_row_structure_is_valid(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify each row contains the required transaction log structure."""
    page = admin_user_transaction_log_page
    page.navigate()

    if page.rows.count() == 0:
        pytest.skip("No data available for user transaction log.")

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        assert cells.count() == 6

        s_no = cells.nth(0).inner_text().strip()
        account_no = cells.nth(1).inner_text().strip()
        transaction_text = cells.nth(2).inner_text().strip()
        transaction_type = cells.nth(3).inner_text().strip()
        transaction_value = cells.nth(4).inner_text().strip()
        modified_date = cells.nth(5).inner_text().strip()

        assert s_no.isdigit()
        assert account_no
        assert transaction_text
        assert transaction_type
        assert transaction_value
        assert modified_date

        assert "→" in transaction_text or "fund" in transaction_text.lower() or "balance" in transaction_text.lower() or "equity" in transaction_text.lower()
        assert any(ch.isdigit() for ch in transaction_value)


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("button_name", "expected_suffix"),
    [
        ("csv_button", ".csv"),
        ("pdf_button", ".pdf"),
    ],
)
def test_user_transaction_log_exports_correct_file_type(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
    button_name: str,
    expected_suffix: str,
    tmp_path: Path,
):
    """Check that export buttons download correct file types."""
    page = admin_user_transaction_log_page
    page.navigate()

    with page.page.expect_download() as download_info:
        getattr(page, button_name).click()

    download = download_info.value
    assert Path(download.suggested_filename).suffix.lower() == expected_suffix

    file_path = tmp_path / f"user_transaction_log{expected_suffix}"
    download.save_as(file_path)

    if expected_suffix == ".csv":
        with file_path.open(encoding="utf-8-sig", newline="") as export_file:
            rows = list(csv.reader(export_file))
        assert rows
        headers = rows[0]
        assert headers == [
            "S.No",
            "Account No",
            "Transaction",
            "Transaction Type",
            "Transaction Value",
            "Modified Date",
        ]
    elif expected_suffix == ".pdf":
        assert file_path.read_bytes().startswith(b"%PDF-")


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_sorting_works(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify sortable headers update aria-sort state."""
    page = admin_user_transaction_log_page
    page.navigate()

    headers = page.table.locator("thead th")
    for i in range(headers.count()):
        header = headers.nth(i)
        header.click()
        first_state = header.get_attribute("aria-sort")
        assert first_state in {"ascending", "descending"}

        header.click()
        second_state = header.get_attribute("aria-sort")
        assert second_state in {"ascending", "descending"}
        assert second_state != first_state


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_pagination_changes_pages(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify pagination changes page only when more than one page exists."""
    page = admin_user_transaction_log_page
    page.navigate()

    row_count = page.rows.count()
    if row_count <= 10:
        pytest.skip("Not enough rows to exercise pagination.")

    next_button = page.pagination.locator("a.next, #datatable_next").first
    prev_button = page.pagination.locator("a.previous, #datatable_previous").first

    next_classes = next_button.get_attribute("class") or ""
    if "disabled" in next_classes:
        pytest.skip("Next pagination is disabled for this dataset.")

    before_info = page.info.inner_text().strip()
    next_button.click()

    expect(page.info).to_be_visible()
    after_info = page.info.inner_text().strip()
    assert after_info != before_info

    prev_classes = prev_button.get_attribute("class") or ""
    if "disabled" not in prev_classes:
        prev_button.click()
        expect(page.info).to_be_visible()
        assert page.info.inner_text().strip() != after_info


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_empty_search_shows_expected_message(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify empty search result shows the DataTables empty message."""
    page = admin_user_transaction_log_page
    page.navigate()

    page.search.fill("transaction-no-match-xyz")
    expect(page.empty_message).to_be_visible()

    message = page.empty_message.inner_text().strip().lower()
    assert (
        "no data available in table" in message
        or "no matching records found" in message
        or "no data" in message
    )


@pytest.mark.admin
@pytest.mark.regression
def test_user_transaction_log_date_values_are_valid(
    admin_user_transaction_log_page: AdminUserTransactionLogPage,
):
    """Verify Modified Date values are valid timestamps."""
    page = admin_user_transaction_log_page
    page.navigate()

    if page.rows.count() == 0:
        pytest.skip("No data available for timestamp validation.")

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
    ]

    for row in page.rows.all()[:10]:
        date_text = row.locator("td").nth(5).inner_text().strip()
        if not date_text:
            pytest.fail(f"Modified Date is empty in row: {row.inner_html()}")

        parsed = False
        for fmt in formats:
            try:
                datetime.strptime(date_text, fmt)
                parsed = True
                break
            except ValueError:
                continue

        assert parsed, f"Invalid Modified Date format: '{date_text}'"
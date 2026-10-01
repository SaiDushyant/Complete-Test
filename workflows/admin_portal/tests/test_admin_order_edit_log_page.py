import csv
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_order_edit_log_page import AdminOrderEditLogPage


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_table_and_controls(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Check the DataTable layout, headers, search, and export controls."""
    page = admin_order_edit_log_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search).to_be_visible()
    expect(page.entries).to_be_visible()
    expect(page.info).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "S.No",
        "Account No",
        "Order ID",
        "Time",
        "Changes",
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
        assert page.rows.first.locator("td").count() == 5
        first_row = page.rows.first
        assert first_row.locator("td").nth(0).is_visible()
        assert first_row.locator("td").nth(1).is_visible()
        assert first_row.locator("td").nth(2).is_visible()
        assert first_row.locator("td").nth(3).is_visible()
        assert first_row.locator("td").nth(4).is_visible()

    original_row_count = page.rows.count()

    page.search.fill("order-edit-no-match-xyz")
    expect(page.empty_message).to_be_visible()
    page.search.clear()
    expect(page.rows).to_have_count(original_row_count)


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_page_size_options(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify page size selector options work correctly."""
    page = admin_order_edit_log_page
    page.navigate()

    for size in ("10", "25", "50", "100"):
        page.entries.select_option(value=size)
        expect(page.entries).to_have_value(size)


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_row_structure_is_valid(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify each row contains the expected cell structure for account/order change log."""
    page = admin_order_edit_log_page
    page.navigate()

    expect(page.rows.first).to_be_visible()
    assert page.rows.count() > 0, "Expected order edit log rows to be present."

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        assert cells.count() == 5

        s_no = cells.nth(0).inner_text().strip()
        account_no = cells.nth(1).inner_text().strip()
        order_id = cells.nth(2).inner_text().strip()
        time_text = cells.nth(3).inner_text().strip()
        changes_text = cells.nth(4).inner_text().strip()

        assert s_no.isdigit()
        assert account_no.isdigit()
        assert order_id.isdigit()
        assert time_text
        assert changes_text
        assert "oldvalue" in row.inner_html() or "newvalue" in row.inner_html()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("button_name", "expected_suffix"),
    [
        ("csv_button", ".csv"),
        ("pdf_button", ".pdf"),
    ],
)
def test_order_edit_log_exports_correct_file_type(
    admin_order_edit_log_page: AdminOrderEditLogPage,
    button_name: str,
    expected_suffix: str,
    tmp_path: Path,
):
    """Check that export buttons produce valid files."""
    page = admin_order_edit_log_page
    page.navigate()

    with page.page.expect_download() as download_info:
        getattr(page, button_name).click()

    download = download_info.value
    assert Path(download.suggested_filename).suffix.lower() == expected_suffix

    file_path = tmp_path / f"order_edit_log{expected_suffix}"
    download.save_as(file_path)

    if expected_suffix == ".csv":
        with file_path.open(encoding="utf-8-sig", newline="") as export_file:
            rows = list(csv.reader(export_file))
        assert rows
        headers = rows[0]
        assert headers == ["S.No", "Account No", "Order ID", "Time", "Changes"]
    elif expected_suffix == ".pdf":
        assert file_path.read_bytes().startswith(b"%PDF-")


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_sorting_works(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Check that the sortable columns update aria-sort state."""
    page = admin_order_edit_log_page
    page.navigate()

    headers = page.table.locator("thead th")

    for i in range(headers.count()):
        header = headers.nth(i)
        cls = header.get_attribute("class") or ""
        if "sorting" not in cls:
            continue
        header.click()
        page.page.wait_for_timeout(300)
        first_cls = header.get_attribute("class") or ""
        first_state = header.get_attribute("aria-sort") or ""
        assert "sorting_asc" in first_cls or "sorting_desc" in first_cls or first_state in {"ascending", "descending"}

        header.click()
        page.page.wait_for_timeout(300)
        second_cls = header.get_attribute("class") or ""
        second_state = header.get_attribute("aria-sort") or ""
        assert "sorting_asc" in second_cls or "sorting_desc" in second_cls or second_state in {"ascending", "descending"}


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_pagination_changes_pages(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify Next/Previous pagination changes the visible page only when pagination is enabled."""
    page = admin_order_edit_log_page
    page.navigate()

    expect(page.pagination).to_be_visible()
    next_button = page.pagination.locator("a.next, #datatable_next, .next a").first
    prev_button = page.pagination.locator("a.previous, #datatable_previous, .previous a").first

    prev_parent = prev_button.locator("..")
    prev_classes = (prev_button.get_attribute("class") or "") + " " + (prev_parent.get_attribute("class") or "")
    assert "disabled" in prev_classes or not prev_button.is_enabled()

    next_parent = next_button.locator("..")
    next_classes = (next_button.get_attribute("class") or "") + " " + (next_parent.get_attribute("class") or "")

    if "disabled" not in next_classes and next_button.is_enabled():
        before_info = page.info.inner_text().strip()
        next_button.click()
        expect(page.info).to_be_visible()
        after_info = page.info.inner_text().strip()
        assert after_info != before_info

        prev_classes_now = (prev_button.get_attribute("class") or "") + " " + (prev_button.locator("..").get_attribute("class") or "")
        if "disabled" not in prev_classes_now:
            prev_button.click()
            expect(page.info).to_be_visible()
            assert page.info.inner_text().strip() != after_info
    else:
        assert "disabled" in next_classes or not next_button.is_enabled()


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_empty_search_shows_expected_message(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify searching with no matching result shows the expected empty-state message."""
    page = admin_order_edit_log_page
    page.navigate()

    page.search.fill("order-edit-no-match-xyz")
    expect(page.empty_message).to_be_visible()

    message = page.empty_message.inner_text().strip().lower()
    assert (
        "no data available in table" in message
        or "no matching records found" in message
        or "no data" in message
    )


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_time_column_has_valid_format(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify all visible time values can be parsed as valid timestamps."""
    page = admin_order_edit_log_page
    page.navigate()

    expect(page.rows.first).to_be_visible()
    assert page.rows.count() > 0, "Expected order edit log rows to be present."

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
        time_text = row.locator("td").nth(3).inner_text().strip()
        if not time_text:
            pytest.fail(f"Empty time value found in row: {row.inner_html()}")

        parsed = False
        for fmt in formats:
            try:
                datetime.strptime(time_text, fmt)
                parsed = True
                break
            except ValueError:
                continue

        assert parsed, f"Invalid time format: '{time_text}'"


@pytest.mark.admin
@pytest.mark.regression
def test_order_edit_log_changes_column_has_old_and_new_value_pattern(
    admin_order_edit_log_page: AdminOrderEditLogPage,
):
    """Verify the Changes column contains actual before/after update information."""
    page = admin_order_edit_log_page
    page.navigate()

    expect(page.rows.first).to_be_visible()
    assert page.rows.count() > 0, "Expected order edit log rows to be present."

    for row in page.rows.all()[:10]:
        cells = row.locator("td")
        assert cells.count() == 5

        changes_text = cells.nth(4).inner_text().strip()
        row_html = row.inner_html().lower()

        if not changes_text:
            pytest.fail(f"Changes column is empty in row: {row.inner_html()}")

        has_old = "old" in changes_text.lower() or "oldvalue" in row_html
        has_new = "new" in changes_text.lower() or "newvalue" in row_html

        assert has_old or has_new, f"Changes value does not look like an old/new update: '{changes_text}'"
        assert "oldvalue" in row_html or "newvalue" in row_html or (
            "old" in changes_text.lower() and "new" in changes_text.lower()
        )
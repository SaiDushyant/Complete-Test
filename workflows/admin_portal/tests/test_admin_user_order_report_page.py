import pytest
import csv
import zipfile
from pathlib import Path
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_user_order_report_page import (
    AdminUserOrderReportPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_user_order_report_table_and_controls(
    admin_user_order_report_page: AdminUserOrderReportPage,
):
    """Check the report table, controls, and filtering without exposing customer data."""
    page = admin_user_order_report_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search).to_be_visible()
    expect(page.entries).to_be_visible()
    expect(page.info).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "User UID", "Customer Name", "Account ID",
        "Commission", "LP Commission", "Spread Commission",
    ]
    actual_headers = [
        (header.get_attribute("aria-label") or "")
        .split(": activate")[0]
        .strip()
        for header in page.table.locator("thead th").all()
    ]
    assert actual_headers == expected_headers

    assert page.entries.locator("option").all_text_contents() == [
        "10", "25", "50", "100"
    ]

    expect(page.csv_button).to_be_visible()
    expect(page.pdf_button).to_be_visible()
    expect(page.excel_button).to_be_visible()

    original_row_count = page.rows.count()

    page.search.fill("automation-no-match")
    expect(page.empty_message).to_be_visible()

    page.search.clear()
    expect(page.rows).to_have_count(original_row_count)

@pytest.mark.admin
@pytest.mark.regression
def test_user_order_report_page_size_options(
    admin_user_order_report_page: AdminUserOrderReportPage,
):
    page = admin_user_order_report_page
    page.navigate()

    for size in ("10", "25", "50", "100"):
        page.entries.select_option(value=size)
        expect(page.entries).to_have_value(size)

@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("button_name", "expected_suffix"),
    [
        ("csv_button", ".csv"),
        ("pdf_button", ".pdf"),
        ("excel_button", ".xlsx"),
    ],
)
def test_user_order_report_exports_correct_file_type(
    admin_user_order_report_page: AdminUserOrderReportPage,
    button_name: str,
    expected_suffix: str,
    tmp_path: Path,
):
    """Check export formats using test-only customer data."""
    page = admin_user_order_report_page
    page.navigate()

    with page.page.expect_download() as download_info:
        getattr(page, button_name).click()

    download = download_info.value
    assert Path(download.suggested_filename).suffix.lower() == expected_suffix

    # Save only to pytest's temporary folder, not the reports folder.
    file_path = tmp_path / f"report{expected_suffix}"
    download.save_as(file_path)

    if expected_suffix == ".csv":
        with file_path.open(encoding="utf-8-sig", newline="") as export_file:
            headers = next(csv.reader(export_file))
        assert headers == [
            "User ID",
            "Name",
            "Account ID",
            "Commission",
            "LP Commission",
            "Spread Commission",
        ]
    elif expected_suffix == ".pdf":
        assert file_path.read_bytes().startswith(b"%PDF-")
    else:
        assert zipfile.is_zipfile(file_path)
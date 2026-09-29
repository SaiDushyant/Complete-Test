import json
import pytest
import re 
from urllib.parse import urlsplit
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_refer_report_page import (
    AdminReferReportPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_refer_report_table_and_controls(
    admin_refer_report_page: AdminReferReportPage,
):
    """Check table structure and controls without exposing referral data."""
    page = admin_refer_report_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search).to_be_visible()
    expect(page.entries).to_be_visible()
    expect(page.info).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "Account Id", "Name", "Token", "Ref ID",
        "Refer by", "Brokerage", "View Report",
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
    expect(page.print_button).to_be_visible()

    expect(page.report_modal).to_be_attached()
    expect(page.modal_title).to_have_text("IB Report")
    assert page.view_report_buttons.count() == page.rows.count()

    original_row_count = page.rows.count()
    page.search.fill("refer-report-no-match")
    expect(page.table.locator("td.dataTables_empty")).to_be_visible()
    page.search.clear()
    expect(page.rows).to_have_count(original_row_count)

@pytest.mark.admin
@pytest.mark.regression
def test_view_report_opens_with_mocked_empty_data(
    admin_refer_report_page: AdminReferReportPage,
):
    """Check the IB Report modal using mocked data, not live referral details."""
    page = admin_refer_report_page
    page.navigate()

    endpoint_path = "/dashboard/api/referbyData.php"
    mock_body = json.dumps([])
    mocked_paths = []

    def mock_refer_data(route):
        mocked_paths.append(urlsplit(route.request.url).path)
        route.fulfill(
            status=200,
            content_type="application/json",
            body=mock_body,
        )

    page.page.route("**/dashboard/api/referbyData.php**", mock_refer_data)

    with page.page.expect_response(
        lambda response: (
            response.request.method == "GET"
            and urlsplit(response.url).path == endpoint_path
        )
    ) as response_info:
        page.view_report_buttons.first.click()

    assert response_info.value.status == 200
    assert mocked_paths == [endpoint_path]
    expect(page.report_modal).to_be_attached()
    expect(page.report_modal).to_be_hidden()
    expect(page.page.locator("text=No Referal Users Found")).to_be_visible()

    expected_modal_headers = [
        "Order ID", "Level", "Commission", "Multi Level", "Time",
    ]
    actual_modal_headers = [
        header.inner_text().strip()
        for header in page.modal_table.locator("thead th").all()
    ]
    assert actual_modal_headers == expected_modal_headers

@pytest.mark.admin
@pytest.mark.regression
def test_refer_report_columns_sort_both_directions(
    admin_refer_report_page: AdminReferReportPage,
):
    """Check each sortable table heading sorts ascending and descending."""
    page = admin_refer_report_page
    page.navigate()

    headers = page.table.locator("thead th")

    for index in range(headers.count()):
        header = headers.nth(index)
        first_sort = header.get_attribute("aria-sort")
        if first_sort is None:
            continue

        header.click()
        new_sort = header.get_attribute("aria-sort")
        if new_sort is not None:
            assert new_sort in {"ascending", "descending"}




@pytest.mark.admin
@pytest.mark.regression
def test_refer_report_next_previous_pagination(
    admin_refer_report_page: AdminReferReportPage,
):
    """Check Next and Previous paging without reading row contents."""
    page = admin_refer_report_page
    page.navigate()
    page.entries.select_option("10")

    next_button = page.pagination.get_by_role("link", name="Next")
    previous_button = page.pagination.get_by_role("link", name="Previous")
    active_page = page.pagination.locator("li.active a")

    next_button.click()
    expect(active_page).to_have_text("2")

    previous_button.click()
    expect(active_page).to_have_text("1")


@pytest.mark.admin
@pytest.mark.regression
def test_refer_report_mocked_modal_can_be_closed(
    admin_refer_report_page: AdminReferReportPage,
):
    """Check the IB Report modal opens from a mocked response and closes."""
    page = admin_refer_report_page
    page.navigate()

    def mock_refer_data(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body="[]",
        )

    page.page.route("**/dashboard/api/referbyData.php**", mock_refer_data)

    with page.page.expect_response(
        lambda response: (
            response.request.method == "GET"
            and urlsplit(response.url).path == "/dashboard/api/referbyData.php"
        )
    ):
        page.view_report_buttons.first.click()

    expect(page.report_modal).to_be_attached()
    expect(page.report_modal).to_be_hidden()
    expect(page.page.locator("text=No Referal Users Found")).to_be_visible()
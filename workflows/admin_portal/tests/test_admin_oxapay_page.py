import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_oxapay_page import AdminOxapayPage


@pytest.mark.admin
@pytest.mark.regression
def test_oxapay_table_controls_columns_and_empty_state(
    admin_oxapay_page: AdminOxapayPage,
):
    page = admin_oxapay_page
    page.navigate()

    expect(page.table).to_be_visible()
    expect(page.search).to_be_visible()
    expect(page.entries).to_be_visible()
    expect(page.info).to_be_visible()
    expect(page.pagination).to_be_visible()

    expected_headers = [
        "S.No", "Account No", "Token", "TrackId", "Status",
        "Address", "Transaction ID", "Amount", "Currency", "Created",
    ]
    actual_headers = [
        (header.get_attribute("aria-label") or "").split(": activate")[0]
        for header in page.table.locator("thead th").all()
    ]
    assert actual_headers == expected_headers

    if page.empty_message.is_visible():
        expect(page.empty_message).to_have_text("No data available in table")
        expect(page.info).to_contain_text("0 entries")
    else:
        assert page.rows.count() > 0
        for row in page.rows.all():
            assert row.locator("td").count() == 10

    page.search.fill("automation-no-match")
    expect(page.empty_message).to_be_visible()
    page.search.clear()
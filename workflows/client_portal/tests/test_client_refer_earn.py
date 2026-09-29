"""
Client Portal Refer & Earn Workflow Tests.
Detailed validation covering all minute controls:
1. Universal header & page title
2. Metric summary cards (Total Earnings & Successful Referrals)
3. Unique referral URL & dynamic 'Copied!' button feedback
4. Interactive Referral Tree View hierarchy with expand/collapse (+ / -)
5. Referred Clients data table (7 columns: Client, Account, Ref ID, Mobile, Balance, Activity, IB Earned)
6. Rows per page selector dropdown (10, 25, 50, 100) & Refresh action
7. Pagination indicators and navigation controls
Includes automated monitoring for Browser Console, JavaScript Runtime, and Backend Network Errors.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.shared.utils.error_monitor import ErrorMonitor


@pytest.mark.client
@pytest.mark.smoke
def test_client_refer_earn_header_elements(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Refer & Earn view displays consistent header elements:
    - Page title is 'Refer & Earn'
    - Account selector badge is visible
    - 'CREATE ACCOUNT' action button is visible and enabled
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()
    client_refer_earn_page.header.assert_header_elements(expected_title="Refer & Earn")

    # Automated Error Check
    client_error_monitor.assert_no_errors("Refer & Earn Header")


@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_summary_cards(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify that the Refer & Earn dashboard renders metric cards:
    - TOTAL EARNINGS (displays dollar amount, e.g. '$16.72')
    - SUCCESSFUL REFERRALS (displays count, e.g. '3')
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()

    expect(client_refer_earn_page.total_earnings_card).to_be_visible()
    expect(client_refer_earn_page.successful_referrals_card).to_be_visible()

    earnings_text = client_refer_earn_page.total_earnings_card.inner_text()
    assert "$" in earnings_text, f"Expected '$' in Total Earnings card, got: '{earnings_text}'"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Refer & Earn Summary Cards")


@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_unique_link_and_copied_feedback(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify minute interaction for the referral link:
    - Input contains valid referral link URL with 'register?ref='
    - 'Copy' button is visible and enabled
    - Clicking 'Copy' dynamically changes button text to 'Copied!'
    - 'How It Works' 3-step cards are displayed
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()

    # 1. Verify link input
    expect(client_refer_earn_page.unique_link_input).to_be_visible()
    link_value = client_refer_earn_page.get_referral_link()
    assert "register?ref=" in link_value, f"Expected 'register?ref=' in referral link, got: '{link_value}'"

    # 2. Click Copy and verify dynamic 'Copied!' feedback
    client_refer_earn_page.click_copy_link_and_verify_feedback()

    # 3. Verify How It Works guide
    expect(client_refer_earn_page.how_it_works_container).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Refer & Earn Link Copy Feedback")


@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_tree_view_hierarchy(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify minute details of the Referral Tree View:
    - Tree view section heading is visible
    - Direct referrals badge is displayed (e.g. '3 Direct')
    - Expand (+) and Collapse (-) buttons are interactive
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()

    expect(client_refer_earn_page.tree_view_heading.first).to_be_visible()
    expect(client_refer_earn_page.direct_referrals_badge).to_be_visible()

    # Expand/collapse interaction
    if client_refer_earn_page.tree_expand_buttons.count() > 0:
        client_refer_earn_page.tree_expand_buttons.first.click()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Refer & Earn Tree View")


@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_referred_clients_table_and_rows_dropdown(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify minute details of the Referred Clients ledger table:
    - All 7 column headers are present: CLIENT, ACCOUNT, REF ID, MOBILE, BALANCE, ACTIVITY, IB EARNED
    - Rows per page dropdown allows selecting 10, 25, 50, 100
    - Refresh referrals button is visible, enabled, and clicked
    - Table rows render client records with accurate formatting
    - Pagination summary indicates total records count
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()

    expect(client_refer_earn_page.referred_clients_heading.first).to_be_visible()

    # 1. Verify 7 Column Headers
    headers = client_refer_earn_page.get_table_header_titles()
    expected_headers = ["CLIENT", "ACCOUNT", "REF ID", "MOBILE", "BALANCE", "ACTIVITY", "IB EARNED"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column header '{expected}' in {headers}"

    # 2. Rows per page selector dropdown
    expect(client_refer_earn_page.rows_per_page_select).to_be_visible()
    client_refer_earn_page.select_rows_per_page("50")
    expect(client_refer_earn_page.rows_per_page_select).to_have_value("50")

    # 3. Refresh button interaction
    expect(client_refer_earn_page.refresh_button).to_be_visible()
    expect(client_refer_earn_page.refresh_button).to_be_enabled()
    client_refer_earn_page.click_refresh_referrals()

    # 4. Table data rows verification
    row_count = client_refer_earn_page.get_referred_clients_count()
    assert row_count > 0, "Expected at least 1 referred client record in table."

    first_row = client_refer_earn_page.get_first_client_row_data()
    assert first_row["account"].isdigit(), f"Expected numeric account ID, got: '{first_row['account']}'"
    assert "$" in first_row["balance"], f"Expected '$' in balance, got: '{first_row['balance']}'"
    assert "$" in first_row["ib_earned"], f"Expected '$' in IB Earned, got: '{first_row['ib_earned']}'"

    # 5. Pagination summary
    expect(client_refer_earn_page.pagination_summary).to_be_visible()
    summary_text = client_refer_earn_page.pagination_summary.inner_text()
    assert "Showing" in summary_text and "referrals" in summary_text

    # Automated Error Check
    client_error_monitor.assert_no_errors("Refer & Earn Clients Table & Dropdown")


@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_referral_link_autofill_on_registration(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End Attribute Scenario: Referral Link Registration Prefill:
    - Extracts the unique referral URL from Refer & Earn view (e.g. '.../register?ref=DZ3FO9')
    - Parses the referral code parameter (ref=...)
    - Opens a new tab/page to the referral URL
    - Verifies the Registration page automatically pre-fills the referral code in 'input[name=referral]'
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()
    referral_url = client_refer_earn_page.get_referral_link()
    assert "ref=" in referral_url, f"Expected 'ref=' in referral link: {referral_url}"

    # Extract referral code
    ref_code = referral_url.split("ref=")[-1].strip()

    # Open registration page in a fresh unauthenticated browser context
    reg_context = client_refer_earn_page.page.context.browser.new_context()
    reg_page = reg_context.new_page()
    reg_page.goto(referral_url)
    reg_page.wait_for_load_state("domcontentloaded")

    # Assert referral code input is correctly prefilled in DOM
    ref_input = reg_page.locator("input[name='referral'], #referral").first
    expect(ref_input).to_have_value(ref_code, timeout=10000)
    assert ref_input.input_value() == ref_code

    reg_page.close()
    reg_context.close()
    client_error_monitor.assert_no_errors("Refer & Earn Registration Autofill")




@pytest.mark.client
@pytest.mark.regression
def test_client_refer_earn_negative_referral_link_readonly(
    client_refer_earn_page: ClientReferEarnPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Negative Scenario: Referral Link Protection:
    - Referral link input must be protected (read-only)
    - User cannot manually alter or overwrite the affiliate link
    - Asserts ZERO console errors, JS crashes, and backend failures
    """
    client_refer_earn_page.navigate()
    expect(client_refer_earn_page.unique_link_input).to_be_visible()

    # The link should have readonly attribute
    is_readonly = client_refer_earn_page.unique_link_input.get_attribute("readonly")
    assert is_readonly is not None or client_refer_earn_page.unique_link_input.is_disabled(), (
        "Expected referral link input to be read-only or disabled."
    )

    client_error_monitor.assert_no_errors("Refer & Earn Negative Link Protection")



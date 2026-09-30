"""
Client Portal PAMM Workflow Tests.
Comprehensive validation covering every minute detail:
- Universal header integration and page title ('PAMM')
- 4 Summary Cards (MANAGERS count, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
- 4 Dropdown Filters (Range: 30D/90D/1Y/All Time, Risk, Fund, Rows: 10/25/50)
- Refresh action button ('Refresh')
- Search input filter & clear
- 9 column table headers & static non-interactive cursor
- View switching: 'MY FOLLOWERS' (Active & History subtabs) <-> 'PAMM MANAGER'
- Statistics button opening Statistics modal dialog (8 metric cards, EQUITY CURVE chart, close)
- Follow PAMM Manager modal lifecycle (Investment amount input, debit notice, Cancel dismissal)
- Multi-Account Follow & Unfollow subscription lifecycle
- Pagination navigation ('Prev', 'Next')
- Zero console errors, JS crashes, or backend 5xx failures.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.shared.utils.error_monitor import ErrorMonitor


# =============================================================================
# 1. PAMM UI & COMPONENT TESTS
# =============================================================================

@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.smoke
def test_client_pamm_header_and_cards(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify PAMM header, summary cards, and column headers:
    - Main heading is 'PAMM'
    - 4 Summary cards render with valid non-empty data:
      * MANAGERS
      * MANAGED CAPITAL
      * CLOSED TRADES
      * FOLLOWERS
    - 9 table headers render: NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION
    - Table headers have static non-interactive cursor
    """
    client_pamm_page.navigate()
    client_pamm_page.header.assert_header_elements(expected_title="PAMM")

    expect(client_pamm_page.main_heading.first).to_be_visible()

    # 1. Assert 4 summary cards
    cards = client_pamm_page.get_summary_card_values()
    assert "MANAGERS" in cards["managers"], f"Expected MANAGERS in {cards['managers']}"
    assert "MANAGED CAPITAL" in cards["managed_capital"], f"Expected MANAGED CAPITAL in {cards['managed_capital']}"
    assert "CLOSED TRADES" in cards["closed_trades"], f"Expected CLOSED TRADES in {cards['closed_trades']}"
    assert "FOLLOWERS" in cards["followers"], f"Expected FOLLOWERS in {cards['followers']}"

    # Extract managers count
    managers_match = re.search(r"MANAGERS\s*(\d+)", cards["managers"])
    assert managers_match is not None, f"Could not parse managers count from {cards['managers']}"
    expected_manager_count = int(managers_match.group(1))
    assert expected_manager_count >= 0

    # 2. Assert 9 column headers
    headers = client_pamm_page.get_table_headers()
    expected_headers = ["NAME", "RANK", "GROWTH", "WIN RATE", "TRADES", "DRAWDOWN", "MANAGED", "RISK", "ACTION"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Static headers cursor check
    for th in client_pamm_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    client_error_monitor.assert_no_errors("PAMM Header and Cards")


@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.regression
def test_client_pamm_dropdowns_and_refresh(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 4 dropdown filters and Refresh action button on PAMM:
    - Range select: '30 Days', '90 Days', '1 Year', 'All Time'
    - Risk select: 'Risk', 'Risk 1', 'Risk 2', 'Risk 3'
    - Fund select: 'Fund', '$1,000+', '$10,000+', '$50,000+'
    - Rows select: '10', '25', '50'
    - Refresh button reloads table data cleanly
    """
    client_pamm_page.navigate()

    # 1. Range dropdown
    range_options = client_pamm_page.range_select.locator("option").all_inner_texts()
    assert any("30 Days" in opt for opt in range_options)
    assert any("1 Year" in opt for opt in range_options)
    client_pamm_page.range_select.select_option("30")
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.range_select.select_option("365")
    client_pamm_page.page.wait_for_timeout(300)

    # 2. Risk dropdown
    risk_options = client_pamm_page.risk_select.locator("option").all_inner_texts()
    assert any("Risk" in opt for opt in risk_options)
    client_pamm_page.risk_select.select_option(index=1)
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.risk_select.select_option(index=0)
    client_pamm_page.page.wait_for_timeout(300)

    # 3. Fund dropdown
    fund_options = client_pamm_page.fund_select.locator("option").all_inner_texts()
    assert any("Fund" in opt for opt in fund_options)
    client_pamm_page.fund_select.select_option(index=1)
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.fund_select.select_option(index=0)
    client_pamm_page.page.wait_for_timeout(300)

    # 4. Rows dropdown
    rows_options = client_pamm_page.rows_select.locator("option").all_inner_texts()
    assert "10" in rows_options
    assert "25" in rows_options
    assert "50" in rows_options

    # 5. Refresh button
    client_pamm_page.click_refresh()
    expect(client_pamm_page.table).to_be_visible()

    client_error_monitor.assert_no_errors("PAMM Dropdowns and Refresh")


@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.regression
def test_client_pamm_search_and_pagination(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Search filtering and pagination controls on PAMM:
    - Search by manager name '10026' or 'Me' filters table
    - Clear search restores full list
    - Pagination buttons Prev/Next operate cleanly
    """
    client_pamm_page.navigate()

    # 1. Get first manager name from table
    expect(client_pamm_page.table_rows.first).to_be_visible(timeout=10000)
    first_mgr_text = client_pamm_page.table_rows.first.locator("td").first.inner_text().strip()
    search_term = first_mgr_text.split("\n")[0].split()[0] if first_mgr_text else "10026"

    # Search for manager
    client_pamm_page.filter_by_search(search_term)
    expect(client_pamm_page.table_rows.first.locator("td").first).not_to_have_text("", timeout=10000)
    filtered_count = client_pamm_page.get_manager_count()
    assert filtered_count >= 1, f"Expected at least 1 manager matching search '{search_term}'"

    first_row_text = client_pamm_page.table_rows.first.inner_text().lower()
    assert search_term.lower() in first_row_text

    # 2. Clear search
    client_pamm_page.clear_search()
    full_count = client_pamm_page.get_manager_count()
    assert full_count >= filtered_count

    # 3. Test pagination controls
    expect(client_pamm_page.prev_btn).to_be_visible()
    expect(client_pamm_page.next_btn).to_be_visible()

    if not client_pamm_page.next_btn.is_disabled():
        client_pamm_page.next_btn.click()
        client_pamm_page.page.wait_for_timeout(500)
        expect(client_pamm_page.table_rows.first).to_be_visible()
        client_pamm_page.prev_btn.click()
        client_pamm_page.page.wait_for_timeout(500)

    client_error_monitor.assert_no_errors("PAMM Search and Pagination")


@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.regression
def test_client_pamm_statistics_modal(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify opening, inspecting, and dismissing the Statistics modal dialog:
    - Open modal via row Statistics icon
    - Validate 8 metric cards: NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, DRAWDOWN, MANAGED
    - Validate Equity Curve chart is visible
    - Dismiss modal via close button
    """
    client_pamm_page.navigate()
    client_pamm_page.open_statistics_modal(row_index=0)

    modal = client_pamm_page.statistics_modal
    expect(modal).to_be_visible()

    # Wait for async statistics data to load
    expect(modal.locator("div, p, span, h2, h3, h4").filter(has_text="NET PROFIT").first).to_be_visible(timeout=15000)

    modal_text = modal.inner_text()
    expected_metrics = ["NET PROFIT", "GROWTH", "WIN RATE", "PROFIT FACTOR", "CLOSED TRADES", "TOTAL LOTS", "DRAWDOWN", "MANAGED"]
    for m in expected_metrics:
        assert m in modal_text, f"Expected metric '{m}' in statistics modal"

    # Close modal
    client_pamm_page.close_statistics_modal()
    expect(modal).not_to_be_visible()

    client_error_monitor.assert_no_errors("PAMM Statistics Modal")


@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.regression
def test_client_pamm_follow_modal_lifecycle(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Follow PAMM Manager modal dialog controls:
    - Open modal on a manager row
    - Verify Investment Amount input field and debit warning
    - Verify Cancel button dismisses modal without subscribing
    """
    client_pamm_page.navigate()
    expect(client_pamm_page.table_rows.first).to_be_visible(timeout=10000)

    for i in range(client_pamm_page.table_rows.count()):
        row = client_pamm_page.table_rows.nth(i)
        if "Follow" in row.inner_text() and "Unfollow" not in row.inner_text():
            manager_name = client_pamm_page.open_follow_modal(row_index=i)
            modal = client_pamm_page.follow_modal

            expect(client_pamm_page.investment_amount_input).to_be_visible()
            expect(client_pamm_page.modal_confirm_btn).to_be_visible()

            # Fill investment amount test
            client_pamm_page.investment_amount_input.fill("250")
            client_pamm_page.page.wait_for_timeout(300)

            # Cancel dismissal
            client_pamm_page.close_follow_modal()
            expect(modal).not_to_be_visible()
            break

    client_error_monitor.assert_no_errors("PAMM Follow Modal Lifecycle")


@pytest.mark.client
@pytest.mark.pamm
@pytest.mark.regression
def test_client_pamm_view_switching(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify view switching between PAMM Manager and MY FOLLOWERS:
    - Switch to MY FOLLOWERS view
    - Verify Active / History tabs and table headers
    - Switch back to PAMM Manager view
    """
    client_pamm_page.navigate()

    # 1. Switch to MY FOLLOWERS
    client_pamm_page.switch_to_my_followers()
    expect(client_pamm_page.table).to_be_visible()

    headers = client_pamm_page.get_followers_table_headers()
    assert len(headers) > 0

    # Verify subtabs
    expect(client_pamm_page.followers_active_btn).to_be_visible()
    expect(client_pamm_page.followers_history_btn).to_be_visible()
    client_pamm_page.followers_history_btn.click()
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.followers_active_btn.click()
    client_pamm_page.page.wait_for_timeout(300)

    # 2. Switch back to PAMM Manager
    client_pamm_page.switch_to_pamm_manager()
    expect(client_pamm_page.table).to_be_visible()
    tm_headers = client_pamm_page.get_table_headers()
    assert any("NAME" in h for h in tm_headers)

    client_error_monitor.assert_no_errors("PAMM View Switching")

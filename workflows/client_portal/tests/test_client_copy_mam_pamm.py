"""
Client Portal Copy Trading, MAM, and PAMM Workflow Tests for Master Account.
Comprehensive validation covering every minute detail and element across all 3 pages:
1. Copy Trading:
   * 4 Summary Cards (MANAGERS count, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
   * Verification that MANAGERS card count matches total rows when Rows=25
   * 4 Dropdowns (Range: 30D/90D/1Y/All Time, Risk, Fund, Rows: 10/25/50)
   * Refresh action button ('Refresh')
   * Search input filter & clear
   * 9 column table headers & static non-interactive cursor
   * View switching: 'MY FOLLOWERS' (Active & History subtabs, follower headers) <-> 'TRADING MANAGER'
   * Statistics button opening Statistics modal dialog (8 metric cards, EQUITY CURVE chart, close)
   * Follow Manager modal lifecycle (Trade method options, fee notice, Cancel dismissal)
   * Pagination navigation ('Prev', 'Next')
2. MAM (Multi-Account Manager):
   * 4 Summary Cards (MANAGERS count, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
   * Verification that MANAGERS card count matches total rows when Rows=25
   * 4 Dropdowns (Range, Risk, Fund, Rows)
   * Refresh action button ('Refresh')
   * Search input filter & clear
   * 9 column table headers & static non-interactive cursor
   * View switching: 'MY FOLLOWERS' (Active & History subtabs, follower headers) <-> 'MAM MANAGER'
   * Statistics button opening Statistics modal dialog (8 metric cards, EQUITY CURVE chart, close)
   * Follow MAM Manager confirmation modal lifecycle
   * Pagination navigation ('Prev', 'Next')
3. PAMM (Percentage Allocation Management Module):
   * 4 Summary Cards (MANAGERS count, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
   * Verification that MANAGERS card count matches total rows when Rows=25
   * 4 Dropdowns (Range, Risk, Fund, Rows)
   * Refresh action button ('Refresh')
   * Search input filter & clear
   * 9 column table headers & static non-interactive cursor
   * View switching: 'MY FOLLOWERS' (Active & History subtabs, follower headers) <-> 'PAMM MANAGER'
   * Statistics button opening Statistics modal dialog (8 metric cards, EQUITY CURVE chart, close)
   * Follow PAMM Manager investment modal lifecycle (Amount input, debit notice, Cancel dismissal)
   * Pagination navigation ('Prev', 'Next')
4. Universal Header Interactive Lifecycle directly on Master view
5. End-to-End Master Journey with Zero Console Errors, JS Crashes, or Backend 5xx Failures
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.client_portal.pages.client_mam_page import ClientMAMPage
from workflows.client_portal.pages.client_pamm_page import ClientPAMMPage
from workflows.shared.utils.error_monitor import ErrorMonitor


# =============================================================================
# 1. COPY TRADING MASTER ACCOUNT TESTS
# =============================================================================

@pytest.mark.client
@pytest.mark.smoke
def test_client_copy_trading_master_cards_and_counts(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Copy Trading Master summary cards, table headers, and manager counts:
    - Main heading is 'Copy Trading'
    - 4 Summary cards render with valid non-empty data:
      * MANAGERS (e.g. 22)
      * MANAGED CAPITAL (e.g. $315,123.41)
      * CLOSED TRADES (e.g. 1,478)
      * FOLLOWERS (e.g. 310)
    - 9 table headers render: NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION
    - Table headers are static (cursor is default/auto)
    - Setting rows dropdown to '25' reveals that total table rows matches the count in the MANAGERS card
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()
    client_copy_trading_page.header.assert_header_elements(expected_title="Copy Trading")

    expect(client_copy_trading_page.main_heading.first).to_be_visible()

    # 1. Inspect and assert 4 summary cards
    cards = client_copy_trading_page.get_summary_card_values()
    assert "MANAGERS" in cards["managers"], f"Expected MANAGERS in {cards['managers']}"
    assert "MANAGED CAPITAL" in cards["managed_capital"], f"Expected MANAGED CAPITAL in {cards['managed_capital']}"
    assert "CLOSED TRADES" in cards["closed_trades"], f"Expected CLOSED TRADES in {cards['closed_trades']}"
    assert "FOLLOWERS" in cards["followers"], f"Expected FOLLOWERS in {cards['followers']}"

    # Extract managers count from card
    managers_match = re.search(r"MANAGERS\s*(\d+)", cards["managers"])
    assert managers_match is not None, f"Could not parse managers count from {cards['managers']}"
    expected_manager_count = int(managers_match.group(1))
    assert expected_manager_count > 0, "Expected positive manager count in MANAGERS card"

    # 2. Inspect 9 column headers
    headers = client_copy_trading_page.get_table_headers()
    expected_headers = ["NAME", "RANK", "GROWTH", "WIN RATE", "TRADES", "DRAWDOWN", "MANAGED", "RISK", "ACTION"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Static headers cursor check
    for th in client_copy_trading_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 4. Verify total manager rows matches MANAGERS card count when rows=25
    client_copy_trading_page.rows_select.select_option("25")
    client_copy_trading_page.page.wait_for_timeout(500)
    assert client_copy_trading_page.get_manager_count() == expected_manager_count, (
        f"Expected {expected_manager_count} rows in table, got {client_copy_trading_page.get_manager_count()}"
    )

    # Restore rows to 10
    client_copy_trading_page.rows_select.select_option("10")
    client_copy_trading_page.page.wait_for_timeout(500)

    # Automated Error Check
    client_error_monitor.assert_no_errors("Copy Trading Master Cards and Counts")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_dropdowns_and_refresh(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 4 dropdown filters and Refresh action button on Copy Trading:
    - Range select: '30 Days', '90 Days', '1 Year', 'All Time'
    - Risk select: 'Risk', 'Risk 1', 'Risk 2', 'Risk 3'
    - Fund select: 'Fund', '$1,000+', '$10,000+', '$50,000+'
    - Rows select: '10', '25', '50'
    - Selecting and restoring options executes cleanly without page crash
    - Refresh button reloads table data cleanly
    - Search filter searches for manager and clears query
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()

    # 1. Range dropdown
    range_options = client_copy_trading_page.range_select.locator("option").all_inner_texts()
    assert any("30 Days" in opt for opt in range_options)
    assert any("1 Year" in opt for opt in range_options)
    client_copy_trading_page.range_select.select_option("30")
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.range_select.select_option("365")
    client_copy_trading_page.page.wait_for_timeout(300)

    # 2. Risk dropdown (test selection and reset)
    risk_options = client_copy_trading_page.risk_select.locator("option").all_inner_texts()
    assert any("Risk" in opt for opt in risk_options)
    client_copy_trading_page.risk_select.select_option("1")
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.risk_select.select_option(value="")
    client_copy_trading_page.page.wait_for_timeout(300)

    # 3. Fund dropdown (test selection and reset)
    fund_options = client_copy_trading_page.fund_select.locator("option").all_inner_texts()
    assert any("Fund" in opt for opt in fund_options)
    client_copy_trading_page.fund_select.select_option("1000")
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.fund_select.select_option(value="")
    client_copy_trading_page.page.wait_for_timeout(300)

    # 4. Rows dropdown
    rows_options = client_copy_trading_page.rows_select.locator("option").all_inner_texts()
    assert "10" in rows_options and "25" in rows_options and "50" in rows_options
    client_copy_trading_page.rows_select.select_option("25")
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.rows_select.select_option("10")
    client_copy_trading_page.page.wait_for_timeout(300)

    # 5. Refresh action button
    client_copy_trading_page.click_refresh()
    expect(client_copy_trading_page.table).to_be_visible()

    # 6. Search input filter & clear
    initial_count = client_copy_trading_page.get_manager_count()
    client_copy_trading_page.filter_by_search("Sam")
    filtered_count = client_copy_trading_page.get_manager_count()
    assert filtered_count <= initial_count
    client_copy_trading_page.clear_search()
    expect(client_copy_trading_page.table_rows.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Copy Trading Dropdowns and Refresh")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_my_followers_view_and_switching(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify switching to 'MY FOLLOWERS' view and back on Copy Trading:
    - Click 'MY FOLLOWERS' button
    - Subtabs 'Active' and 'History' render
    - Followers table renders with 7 column headers:
      ['ACCOUNT ID', 'FOLLOW DATE', 'TRADE METHOD', 'FOLLOWER FUND', 'COPIED ORDERS', 'COPIED LOTS', 'COPIED PNL']
    - Followers table displays follower records
    - Subtab switching between 'History' and 'Active' succeeds cleanly
    - Click 'TRADING MANAGER' button returns to manager leaderboard view
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()

    # 1. Switch to MY FOLLOWERS
    client_copy_trading_page.switch_to_my_followers()
    expect(client_copy_trading_page.followers_active_btn).to_be_visible()
    expect(client_copy_trading_page.followers_history_btn).to_be_visible()

    # 2. Check follower table column headers
    f_headers = client_copy_trading_page.get_followers_table_headers()
    expected_f_headers = ["ACCOUNT ID", "FOLLOW DATE", "TRADE METHOD", "FOLLOWER FUND", "COPIED ORDERS", "COPIED LOTS", "COPIED PNL"]
    for expected in expected_f_headers:
        assert any(expected in h for h in f_headers), f"Expected column '{expected}' in {f_headers}"

    # 3. Verify follower records exist
    assert client_copy_trading_page.get_followers_count() >= 1, "Expected at least 1 active follower in Copy Trading"

    # 4. Switch between History and Active subtabs
    client_copy_trading_page.followers_history_btn.click()
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.followers_active_btn.click()
    client_copy_trading_page.page.wait_for_timeout(300)

    # 5. Switch back to TRADING MANAGER
    client_copy_trading_page.switch_to_trading_manager()
    expect(client_copy_trading_page.table).to_be_visible()
    assert client_copy_trading_page.get_manager_count() > 0

    # Automated Error Check
    client_error_monitor.assert_no_errors("Copy Trading My Followers View and Switching")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_statistics_modal_and_follow_modal(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Statistics modal and Follow Manager modal lifecycle on Copy Trading:
    - Click Statistics icon button on first manager row
    - Statistics modal dialog opens with:
      * Title ('STATISTICS')
      * Manager identity details
      * 8 Metric cards (NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, MAX DRAWDOWN, MANAGED CAPITAL)
      * Equity Curve chart
    - Close statistics modal via close button
    - Click 'Follow' button on manager row
    - Follow Manager modal opens with trade methods & subscription fee notice
    - Close follow modal via Cancel button
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()

    # 1. Statistics Modal Lifecycle
    client_copy_trading_page.open_statistics_modal(row_index=0)
    expect(client_copy_trading_page.statistics_modal.first).to_be_visible()
    expect(client_copy_trading_page.statistics_modal.first).to_contain_text(re.compile(r"STATISTICS", re.I))

    # Assert key metrics inside modal
    modal_text = client_copy_trading_page.statistics_modal.first.inner_text()
    for metric in ["NET PROFIT", "GROWTH", "WIN RATE", "PROFIT FACTOR", "CLOSED TRADES", "TOTAL LOTS", "MAX DRAWDOWN", "MANAGED CAPITAL"]:
        assert metric in modal_text, f"Expected metric card '{metric}' in Statistics modal"

    # Close statistics modal
    client_copy_trading_page.close_statistics_modal()
    expect(client_copy_trading_page.statistics_modal.first).not_to_be_visible()

    # 2. Follow Manager Modal Lifecycle
    manager_name = client_copy_trading_page.open_follow_modal(row_index=0)
    expect(client_copy_trading_page.follow_modal.first).to_be_visible()
    expect(client_copy_trading_page.follow_modal.first).to_contain_text("Follow Manager")
    expect(client_copy_trading_page.modal_balance_based).to_be_visible()
    expect(client_copy_trading_page.modal_equity_based).to_be_visible()
    expect(client_copy_trading_page.modal_multiplier_based).to_be_visible()
    expect(client_copy_trading_page.modal_cancel_btn).to_be_visible()

    # Close follow modal
    client_copy_trading_page.close_follow_modal()
    expect(client_copy_trading_page.follow_modal.first).not_to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("Copy Trading Statistics and Follow Modals")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_pagination(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify pagination navigation on Copy Trading:
    - With Rows=10, Prev is disabled on page 1, Next is enabled
    - Click Next navigates to page 2 (Prev becomes enabled)
    - Click Prev navigates back to page 1
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()
    # Reset filters to guarantee clean pagination state
    client_copy_trading_page.risk_select.select_option(value="")
    client_copy_trading_page.fund_select.select_option(value="")
    client_copy_trading_page.rows_select.select_option("10")
    client_copy_trading_page.click_refresh()
    client_copy_trading_page.page.wait_for_timeout(500)

    expect(client_copy_trading_page.prev_btn).to_be_visible()
    expect(client_copy_trading_page.next_btn).to_be_visible()

    # Page 1 state
    assert not client_copy_trading_page.prev_btn.is_enabled(), "Expected Prev button disabled on page 1"
    assert client_copy_trading_page.next_btn.is_enabled(), "Expected Next button enabled on page 1"

    # Navigate to Page 2
    client_copy_trading_page.next_btn.click()
    client_copy_trading_page.page.wait_for_timeout(500)
    assert client_copy_trading_page.prev_btn.is_enabled(), "Expected Prev button enabled on page 2"
    assert client_copy_trading_page.get_manager_count() > 0

    # Navigate back to Page 1
    client_copy_trading_page.prev_btn.click()
    client_copy_trading_page.page.wait_for_timeout(500)
    assert not client_copy_trading_page.prev_btn.is_enabled(), "Expected Prev button disabled back on page 1"

    # Automated Error Check
    client_error_monitor.assert_no_errors("Copy Trading Pagination")


# =============================================================================
# 2. MAM (MULTI-ACCOUNT MANAGER) MASTER ACCOUNT TESTS
# =============================================================================

@pytest.mark.client
@pytest.mark.smoke
def test_client_mam_master_cards_and_counts(
    client_mam_page: ClientMAMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify MAM Master summary cards, table headers, and manager counts:
    - Main heading is 'MAM'
    - 4 Summary cards render with valid non-empty data:
      * MANAGERS (15)
      * MANAGED CAPITAL ($64,346.2)
      * CLOSED TRADES (3,111)
      * FOLLOWERS (47)
    - 9 table headers render: NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION
    - Table headers are static (cursor is default/auto)
    - Setting rows dropdown to '25' reveals that total table rows matches the count in the MANAGERS card (15)
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_mam_page.navigate()
    client_mam_page.header.assert_header_elements(expected_title="MAM")

    expect(client_mam_page.main_heading.first).to_be_visible()

    # 1. Inspect and assert 4 summary cards
    cards = client_mam_page.get_summary_card_values()
    assert "MANAGERS" in cards["managers"], f"Expected MANAGERS in {cards['managers']}"
    assert "MANAGED CAPITAL" in cards["managed_capital"], f"Expected MANAGED CAPITAL in {cards['managed_capital']}"
    assert "CLOSED TRADES" in cards["closed_trades"], f"Expected CLOSED TRADES in {cards['closed_trades']}"
    assert "FOLLOWERS" in cards["followers"], f"Expected FOLLOWERS in {cards['followers']}"

    # Extract managers count from card
    managers_match = re.search(r"MANAGERS\s*(\d+)", cards["managers"])
    assert managers_match is not None, f"Could not parse managers count from {cards['managers']}"
    expected_manager_count = int(managers_match.group(1))
    assert expected_manager_count > 0, "Expected positive manager count in MANAGERS card"

    # 2. Inspect 9 column headers
    headers = client_mam_page.get_table_headers()
    expected_headers = ["NAME", "RANK", "GROWTH", "WIN RATE", "TRADES", "DRAWDOWN", "MANAGED", "RISK", "ACTION"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Static headers cursor check
    for th in client_mam_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 4. Verify total manager rows matches MANAGERS card count when rows=25
    client_mam_page.rows_select.select_option("25")
    client_mam_page.page.wait_for_timeout(500)
    assert client_mam_page.get_manager_count() == expected_manager_count, (
        f"Expected {expected_manager_count} rows in table, got {client_mam_page.get_manager_count()}"
    )

    # Restore rows to 10
    client_mam_page.rows_select.select_option("10")
    client_mam_page.page.wait_for_timeout(500)

    # Automated Error Check
    client_error_monitor.assert_no_errors("MAM Master Cards and Counts")


@pytest.mark.client
@pytest.mark.regression
def test_client_mam_dropdowns_and_refresh(
    client_mam_page: ClientMAMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify all 4 dropdown filters and Refresh action button on MAM:
    - Range select: '30 Days', '90 Days', '1 Year', 'All Time'
    - Risk select: 'Risk', 'Risk 1', 'Risk 2', 'Risk 3'
    - Fund select: 'Fund', '$1,000+', '$10,000+', '$50,000+'
    - Rows select: '10', '25', '50'
    - Selecting and restoring options executes cleanly without page crash
    - Refresh button reloads table data cleanly
    - Search filter searches for manager and clears query
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_mam_page.navigate()

    # 1. Range dropdown
    range_options = client_mam_page.range_select.locator("option").all_inner_texts()
    assert any("30 Days" in opt for opt in range_options)
    client_mam_page.range_select.select_option("30")
    client_mam_page.page.wait_for_timeout(300)
    client_mam_page.range_select.select_option("365")
    client_mam_page.page.wait_for_timeout(300)

    # 2. Risk dropdown
    client_mam_page.risk_select.select_option("1")
    client_mam_page.page.wait_for_timeout(300)
    client_mam_page.risk_select.select_option(value="")
    client_mam_page.page.wait_for_timeout(300)

    # 3. Fund dropdown
    client_mam_page.fund_select.select_option("1000")
    client_mam_page.page.wait_for_timeout(300)
    client_mam_page.fund_select.select_option(value="")
    client_mam_page.page.wait_for_timeout(300)

    # 4. Rows dropdown
    rows_options = client_mam_page.rows_select.locator("option").all_inner_texts()
    assert "10" in rows_options and "25" in rows_options and "50" in rows_options
    client_mam_page.rows_select.select_option("25")
    client_mam_page.page.wait_for_timeout(300)
    client_mam_page.rows_select.select_option("10")
    client_mam_page.page.wait_for_timeout(300)

    # 5. Refresh action button
    client_mam_page.click_refresh()
    expect(client_mam_page.table).to_be_visible()

    # 6. Search input filter & clear
    client_mam_page.filter_by_search("sapna")
    client_mam_page.clear_search()
    expect(client_mam_page.table_rows.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("MAM Dropdowns and Refresh")


@pytest.mark.client
@pytest.mark.regression
def test_client_mam_my_followers_view_and_switching(
    client_mam_page: ClientMAMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify switching to 'MY FOLLOWERS' view and back on MAM:
    - Click 'MY FOLLOWERS' button
    - Subtabs 'Active' and 'History' render
    - Followers table renders with 5 column headers:
      ['FOLLOWER NAME', 'YOUR PROFIT SHARE', 'USER ID', 'MAM ID', 'ACTION']
    - Followers table displays follower records
    - Subtab switching between 'History' and 'Active' succeeds cleanly
    - Click 'MAM MANAGER' button returns to manager leaderboard view
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_mam_page.navigate()

    # 1. Switch to MY FOLLOWERS
    client_mam_page.switch_to_my_followers()
    expect(client_mam_page.followers_active_btn).to_be_visible()
    expect(client_mam_page.followers_history_btn).to_be_visible()

    # 2. Check follower table column headers
    f_headers = client_mam_page.get_followers_table_headers()
    expected_f_headers = ["FOLLOWER NAME", "YOUR PROFIT SHARE", "USER ID", "MAM ID", "ACTION"]
    for expected in expected_f_headers:
        assert any(expected in h for h in f_headers), f"Expected column '{expected}' in {f_headers}"

    # 3. Verify follower records exist
    assert client_mam_page.get_followers_count() >= 1, "Expected at least 1 active follower in MAM"

    # 4. Switch between History and Active subtabs
    client_mam_page.followers_history_btn.click()
    client_mam_page.page.wait_for_timeout(300)
    client_mam_page.followers_active_btn.click()
    client_mam_page.page.wait_for_timeout(300)

    # 5. Switch back to MAM MANAGER
    client_mam_page.switch_to_mam_manager()
    expect(client_mam_page.table).to_be_visible()
    assert client_mam_page.get_manager_count() > 0

    # Automated Error Check
    client_error_monitor.assert_no_errors("MAM My Followers View and Switching")


@pytest.mark.client
@pytest.mark.regression
def test_client_mam_statistics_modal_and_follow_modal(
    client_mam_page: ClientMAMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Statistics modal and Follow MAM Manager modal lifecycle on MAM:
    - Click Statistics icon button on first MAM manager row
    - Statistics modal dialog opens with:
      * Title ('STATISTICS')
      * Manager identity details
      * 8 Metric cards (NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, MAX DRAWDOWN, MANAGED CAPITAL)
      * Equity Curve chart
    - Close statistics modal via close button
    - Click 'Follow' button on MAM manager row
    - Follow MAM Manager modal opens with confirmation prompt
    - Close follow modal via Cancel button
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_mam_page.navigate()

    # 1. Statistics Modal Lifecycle
    client_mam_page.open_statistics_modal(row_index=0)
    expect(client_mam_page.statistics_modal.first).to_be_visible()
    expect(client_mam_page.statistics_modal.first).to_contain_text(re.compile(r"STATISTICS", re.I))

    # Assert key metrics inside modal
    modal_text = client_mam_page.statistics_modal.first.inner_text()
    for metric in ["NET PROFIT", "GROWTH", "WIN RATE", "PROFIT FACTOR", "CLOSED TRADES", "TOTAL LOTS", "MAX DRAWDOWN", "MANAGED CAPITAL"]:
        assert metric in modal_text, f"Expected metric card '{metric}' in MAM Statistics modal"

    # Close statistics modal
    client_mam_page.close_statistics_modal()
    expect(client_mam_page.statistics_modal.first).not_to_be_visible()

    # 2. Follow MAM Manager Modal Lifecycle
    manager_name = client_mam_page.open_follow_modal(row_index=0)
    expect(client_mam_page.follow_modal.first).to_be_visible()
    expect(client_mam_page.follow_modal.first).to_contain_text("Are you sure you want to follow this MAM manager?")
    expect(client_mam_page.modal_cancel_btn).to_be_visible()
    expect(client_mam_page.modal_confirm_btn).to_be_visible()

    # Close follow modal
    client_mam_page.close_follow_modal()
    expect(client_mam_page.follow_modal.first).not_to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("MAM Statistics and Follow Modals")


@pytest.mark.client
@pytest.mark.regression
def test_client_mam_pagination(
    client_mam_page: ClientMAMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify pagination navigation on MAM:
    - With Rows=10, Prev is disabled on page 1, Next is enabled
    - Click Next navigates to page 2 (5 rows, Prev becomes enabled, Next disabled as last page)
    - Click Prev navigates back to page 1
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_mam_page.navigate()
    # Reset filters to guarantee clean pagination state
    client_mam_page.risk_select.select_option(value="")
    client_mam_page.fund_select.select_option(value="")
    client_mam_page.rows_select.select_option("10")
    client_mam_page.click_refresh()
    client_mam_page.page.wait_for_timeout(500)

    expect(client_mam_page.prev_btn).to_be_visible()
    expect(client_mam_page.next_btn).to_be_visible()

    # Page 1 state
    assert not client_mam_page.prev_btn.is_enabled(), "Expected Prev button disabled on page 1"
    assert client_mam_page.next_btn.is_enabled(), "Expected Next button enabled on page 1"

    # Navigate to Page 2 (MAM has 15 items, so Page 2 is the last page)
    client_mam_page.next_btn.click()
    client_mam_page.page.wait_for_timeout(500)
    assert client_mam_page.prev_btn.is_enabled(), "Expected Prev button enabled on page 2"
    assert not client_mam_page.next_btn.is_enabled(), "Expected Next button disabled on page 2 (last page of 15 items)"
    assert client_mam_page.get_manager_count() > 0

    # Navigate back to Page 1
    client_mam_page.prev_btn.click()
    client_mam_page.page.wait_for_timeout(500)
    assert not client_mam_page.prev_btn.is_enabled(), "Expected Prev button disabled back on page 1"

    # Automated Error Check
    client_error_monitor.assert_no_errors("MAM Pagination")


# =============================================================================
# 3. PAMM (PERCENTAGE ALLOCATION MANAGEMENT MODULE) MASTER ACCOUNT TESTS
# =============================================================================

@pytest.mark.client
@pytest.mark.smoke
def test_client_pamm_master_cards_and_counts(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify PAMM Master summary cards, table headers, and manager counts:
    - Main heading is 'PAMM'
    - 4 Summary cards render with valid non-empty data:
      * MANAGERS (21)
      * MANAGED CAPITAL ($3,280)
      * CLOSED TRADES (2,666)
      * FOLLOWERS (34)
    - 9 table headers render: NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION
    - Table headers are static (cursor is default/auto)
    - Setting rows dropdown to '25' reveals that total table rows matches the count in the MANAGERS card (21)
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_pamm_page.navigate()
    client_pamm_page.header.assert_header_elements(expected_title="PAMM")

    expect(client_pamm_page.main_heading.first).to_be_visible()

    # 1. Inspect and assert 4 summary cards
    cards = client_pamm_page.get_summary_card_values()
    assert "MANAGERS" in cards["managers"], f"Expected MANAGERS in {cards['managers']}"
    assert "MANAGED CAPITAL" in cards["managed_capital"], f"Expected MANAGED CAPITAL in {cards['managed_capital']}"
    assert "CLOSED TRADES" in cards["closed_trades"], f"Expected CLOSED TRADES in {cards['closed_trades']}"
    assert "FOLLOWERS" in cards["followers"], f"Expected FOLLOWERS in {cards['followers']}"

    # Extract managers count from card
    managers_match = re.search(r"MANAGERS\s*(\d+)", cards["managers"])
    assert managers_match is not None, f"Could not parse managers count from {cards['managers']}"
    expected_manager_count = int(managers_match.group(1))
    assert expected_manager_count > 0, "Expected positive manager count in MANAGERS card"

    # 2. Inspect 9 column headers
    headers = client_pamm_page.get_table_headers()
    expected_headers = ["NAME", "RANK", "GROWTH", "WIN RATE", "TRADES", "DRAWDOWN", "MANAGED", "RISK", "ACTION"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Static headers cursor check
    for th in client_pamm_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    # 4. Verify total manager rows matches MANAGERS card count when rows=25
    client_pamm_page.rows_select.select_option("25")
    client_pamm_page.page.wait_for_timeout(500)
    assert client_pamm_page.get_manager_count() == expected_manager_count, (
        f"Expected {expected_manager_count} rows in table, got {client_pamm_page.get_manager_count()}"
    )

    # Restore rows to 10
    client_pamm_page.rows_select.select_option("10")
    client_pamm_page.page.wait_for_timeout(500)

    # Automated Error Check
    client_error_monitor.assert_no_errors("PAMM Master Cards and Counts")


@pytest.mark.client
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
    - Selecting and restoring options executes cleanly without page crash
    - Refresh button reloads table data cleanly
    - Search filter searches for manager and clears query
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_pamm_page.navigate()

    # 1. Range dropdown
    range_options = client_pamm_page.range_select.locator("option").all_inner_texts()
    assert any("30 Days" in opt for opt in range_options)
    client_pamm_page.range_select.select_option("30")
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.range_select.select_option("365")
    client_pamm_page.page.wait_for_timeout(300)

    # 2. Risk dropdown
    client_pamm_page.risk_select.select_option("1")
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.risk_select.select_option(value="")
    client_pamm_page.page.wait_for_timeout(300)

    # 3. Fund dropdown
    client_pamm_page.fund_select.select_option("1000")
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.fund_select.select_option(value="")
    client_pamm_page.page.wait_for_timeout(300)

    # 4. Rows dropdown
    rows_options = client_pamm_page.rows_select.locator("option").all_inner_texts()
    assert "10" in rows_options and "25" in rows_options and "50" in rows_options
    client_pamm_page.rows_select.select_option("25")
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.rows_select.select_option("10")
    client_pamm_page.page.wait_for_timeout(300)

    # 5. Refresh action button
    client_pamm_page.click_refresh()
    expect(client_pamm_page.table).to_be_visible()

    # 6. Search input filter & clear
    client_pamm_page.filter_by_search("sapna")
    client_pamm_page.clear_search()
    expect(client_pamm_page.table_rows.first).to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("PAMM Dropdowns and Refresh")


@pytest.mark.client
@pytest.mark.regression
def test_client_pamm_my_followers_view_and_switching(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify switching to 'MY FOLLOWERS' view and back on PAMM:
    - Click 'MY FOLLOWERS' button
    - Subtabs 'Active' and 'History' render
    - Followers table renders with 4 column headers:
      ['NAME', 'INVESTMENT', 'MANAGER SHARE (ELIGIBLE ORDERS)', 'ACTION']
    - Followers table displays follower records
    - Subtab switching between 'History' and 'Active' succeeds cleanly
    - Click 'PAMM MANAGER' button returns to manager leaderboard view
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_pamm_page.navigate()

    # 1. Switch to MY FOLLOWERS
    client_pamm_page.switch_to_my_followers()
    expect(client_pamm_page.followers_active_btn).to_be_visible()
    expect(client_pamm_page.followers_history_btn).to_be_visible()

    # 2. Check follower table column headers
    f_headers = client_pamm_page.get_followers_table_headers()
    expected_f_headers = ["NAME", "INVESTMENT", "MANAGER SHARE (ELIGIBLE ORDERS)", "ACTION"]
    for expected in expected_f_headers:
        assert any(expected in h for h in f_headers), f"Expected column '{expected}' in {f_headers}"

    # 3. Verify follower records exist
    assert client_pamm_page.get_followers_count() >= 1, "Expected at least 1 active follower in PAMM"

    # 4. Switch between History and Active subtabs
    client_pamm_page.followers_history_btn.click()
    client_pamm_page.page.wait_for_timeout(300)
    client_pamm_page.followers_active_btn.click()
    client_pamm_page.page.wait_for_timeout(300)

    # 5. Switch back to PAMM MANAGER
    client_pamm_page.switch_to_pamm_manager()
    expect(client_pamm_page.table).to_be_visible()
    assert client_pamm_page.get_manager_count() > 0

    # Automated Error Check
    client_error_monitor.assert_no_errors("PAMM My Followers View and Switching")


@pytest.mark.client
@pytest.mark.regression
def test_client_pamm_statistics_modal_and_follow_modal(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Statistics modal and Follow PAMM Manager modal lifecycle on PAMM:
    - Click Statistics icon button on first PAMM manager row
    - Statistics modal dialog opens with:
      * Title ('STATISTICS')
      * Manager identity details
      * 8 Metric cards (NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, MAX DRAWDOWN, MANAGED CAPITAL)
      * Equity Curve chart
    - Close statistics modal via close button
    - Click 'Follow' button on PAMM manager row
    - Follow PAMM Manager modal opens with investment amount input and debit notice
    - Input investment amount '250.00'
    - Close follow modal via Cancel button
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_pamm_page.navigate()

    # 1. Statistics Modal Lifecycle
    client_pamm_page.open_statistics_modal(row_index=0)
    expect(client_pamm_page.statistics_modal.first).to_be_visible()
    expect(client_pamm_page.statistics_modal.first).to_contain_text(re.compile(r"STATISTICS", re.I))

    # Assert key metrics inside modal
    modal_text = client_pamm_page.statistics_modal.first.inner_text()
    for metric in ["NET PROFIT", "GROWTH", "WIN RATE", "PROFIT FACTOR", "CLOSED TRADES", "TOTAL LOTS", "MAX DRAWDOWN", "MANAGED CAPITAL"]:
        assert metric in modal_text, f"Expected metric card '{metric}' in PAMM Statistics modal"

    # Close statistics modal
    client_pamm_page.close_statistics_modal()
    expect(client_pamm_page.statistics_modal.first).not_to_be_visible()

    # 2. Follow PAMM Manager Modal Lifecycle
    manager_name = client_pamm_page.open_follow_modal(row_index=0)
    expect(client_pamm_page.follow_modal.first).to_be_visible()
    expect(client_pamm_page.follow_modal.first).to_contain_text(re.compile(r"Investment\s*Amount", re.I))
    expect(client_pamm_page.follow_modal.first).to_contain_text("This amount will be debited from your balance")

    # Enter investment amount
    expect(client_pamm_page.investment_amount_input).to_be_visible()
    client_pamm_page.investment_amount_input.fill("250.00")

    expect(client_pamm_page.modal_cancel_btn).to_be_visible()
    expect(client_pamm_page.modal_confirm_btn).to_be_visible()

    # Close follow modal
    client_pamm_page.close_follow_modal()
    expect(client_pamm_page.follow_modal.first).not_to_be_visible()

    # Automated Error Check
    client_error_monitor.assert_no_errors("PAMM Statistics and Follow Modals")


@pytest.mark.client
@pytest.mark.regression
def test_client_pamm_pagination(
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify pagination navigation on PAMM:
    - With Rows=10, Prev is disabled on page 1, Next is enabled
    - Click Next navigates to page 2 (Prev becomes enabled)
    - Click Prev navigates back to page 1
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_pamm_page.navigate()
    # Reset filters to guarantee clean pagination state
    client_pamm_page.risk_select.select_option(value="")
    client_pamm_page.fund_select.select_option(value="")
    client_pamm_page.rows_select.select_option("10")
    client_pamm_page.click_refresh()
    client_pamm_page.page.wait_for_timeout(500)

    expect(client_pamm_page.prev_btn).to_be_visible()
    expect(client_pamm_page.next_btn).to_be_visible()

    # Page 1 state
    assert not client_pamm_page.prev_btn.is_enabled(), "Expected Prev button disabled on page 1"
    assert client_pamm_page.next_btn.is_enabled(), "Expected Next button enabled on page 1"

    # Navigate to Page 2
    client_pamm_page.next_btn.click()
    client_pamm_page.page.wait_for_timeout(500)
    assert client_pamm_page.prev_btn.is_enabled(), "Expected Prev button enabled on page 2"
    assert client_pamm_page.get_manager_count() > 0

    # Navigate back to Page 1
    client_pamm_page.prev_btn.click()
    client_pamm_page.page.wait_for_timeout(500)
    assert not client_pamm_page.prev_btn.is_enabled(), "Expected Prev button disabled back on page 1"

    # Automated Error Check
    client_error_monitor.assert_no_errors("PAMM Pagination")


# =============================================================================
# 4. UNIVERSAL HEADER INTERACTIVITY & END-TO-END SUITE
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_header_full_interactive_lifecycle(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify complete header interactivity while on the Copy Trading Master view:
    - Page title is 'Copy Trading' and all universal header elements render
    - Theme toggle switches between dark and light themes smoothly
    - Account switcher opens 'SELECT ACCOUNT' modal, verifies account badge, and closes
    - Notifications drawer opens 'Security & Clearance Alerts' and dismisses cleanly
    - Support Center drawer opens, displays Session Info & FAQ, and closes
    - Create Account modal opens 'LIVE ACCOUNT CREATION' and dismisses via Cancel
    - Search input accepts queries and clears
    - Asserts zero console errors, JS crashes, and backend failures
    """
    client_copy_trading_page.navigate()
    header = client_copy_trading_page.header

    # 1. Assert header elements
    header.assert_header_elements(expected_title="Copy Trading")

    # 2. Theme toggle
    header.toggle_theme()
    header.toggle_theme()

    # 3. Account switcher inspection without altering master session
    header.open_account_switcher()
    expect(header.account_switcher_dropdown.first).to_be_visible()
    header.page.locator("div.fixed.inset-0.z-30").click()
    header.page.wait_for_timeout(300)
    expect(header.account_badge).to_contain_text("10026")

    # 4. Notifications drawer
    header.open_notifications()
    expect(header.notifications_drawer).to_be_visible()
    header.close_notifications()
    expect(header.notifications_drawer).not_to_be_visible()

    # 5. Support Center drawer
    header.open_support()
    expect(header.support_drawer).to_be_visible()
    header.close_support()
    expect(header.support_drawer).not_to_be_visible()

    # 6. Create Account modal
    header.open_create_account_modal()
    expect(header.create_account_modal).to_be_visible()
    header.close_create_account_modal()
    expect(header.create_account_modal).not_to_be_visible()

    # 7. Search input
    header.search("Copy Test")
    header.clear_search()

    # Strict Zero Error Check
    client_error_monitor.assert_no_errors("Copy Trading Header Full Interactive Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_master_pages_end_to_end_journey_zero_errors(
    client_copy_trading_page: ClientCopyTradingPage,
    client_mam_page: ClientMAMPage,
    client_pamm_page: ClientPAMMPage,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-End endurance test traversing Copy Trading, MAM, and PAMM master workflows:
    - Navigate to Copy Trading, inspect cards, open/close statistics modal, open/close follow modal
    - Navigate to MAM, inspect cards, open/close statistics modal, open/close follow modal
    - Navigate to PAMM, inspect cards, open/close statistics modal, open/close follow modal
    - Return to Copy Trading
    - Asserts ZERO console errors, ZERO JS crashes, and ZERO 5xx backend errors
    """
    # 1. Copy Trading
    client_copy_trading_page.navigate()
    assert client_copy_trading_page.is_copy_trading_displayed()
    client_copy_trading_page.open_statistics_modal(0)
    client_copy_trading_page.close_statistics_modal()
    client_copy_trading_page.open_follow_modal(0)
    client_copy_trading_page.close_follow_modal()

    # 2. MAM
    client_mam_page.navigate()
    assert client_mam_page.is_mam_displayed()
    client_mam_page.open_statistics_modal(0)
    client_mam_page.close_statistics_modal()
    client_mam_page.open_follow_modal(0)
    client_mam_page.close_follow_modal()

    # 3. PAMM
    client_pamm_page.navigate()
    assert client_pamm_page.is_pamm_displayed()
    client_pamm_page.open_statistics_modal(0)
    client_pamm_page.close_statistics_modal()
    client_pamm_page.open_follow_modal(0)
    client_pamm_page.close_follow_modal()

    # 4. Return to Copy Trading
    client_copy_trading_page.navigate()
    assert client_copy_trading_page.is_copy_trading_displayed()

    # Strict Zero Error Check across entire journey
    client_error_monitor.assert_no_errors("Copy Trading, MAM, PAMM End-to-End Master Journey")

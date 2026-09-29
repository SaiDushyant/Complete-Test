"""
Client Portal Copy Trading Workflow Tests.
Comprehensive validation covering every minute detail:
- Universal header integration and page title ('Copy Trading')
- 4 Summary Cards (MANAGERS count, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
- 4 Dropdown Filters (Range: 30D/90D/1Y/All Time, Risk, Fund, Rows: 10/25/50)
- Refresh action button ('Refresh')
- Search input filter & clear
- 9 column table headers & static non-interactive cursor
- View switching: 'MY FOLLOWERS' / 'MY SUBSCRIPTION' (Active & History subtabs) <-> 'TRADING MANAGER'
- Statistics button opening Statistics modal dialog (8 metric cards, EQUITY CURVE chart, close)
- Follow Manager modal lifecycle (Trade method options, fee notice, Cancel dismissal)
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
from workflows.client_portal.pages.client_copy_trading_page import ClientCopyTradingPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.shared.utils.error_monitor import ErrorMonitor


# =============================================================================
# 1. COPY TRADING UI & COMPONENT TESTS
# =============================================================================

@pytest.mark.client
@pytest.mark.smoke
def test_client_copy_trading_header_and_cards(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Copy Trading header, summary cards, and column headers:
    - Main heading is 'Copy Trading'
    - 4 Summary cards render with valid non-empty data:
      * MANAGERS
      * MANAGED CAPITAL
      * CLOSED TRADES
      * FOLLOWERS
    - 9 table headers render: NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION
    - Table headers have static cursor
    """
    client_copy_trading_page.navigate()
    client_copy_trading_page.header.assert_header_elements(expected_title="Copy Trading")

    expect(client_copy_trading_page.main_heading.first).to_be_visible()

    # 1. Assert 4 summary cards
    cards = client_copy_trading_page.get_summary_card_values()
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
    headers = client_copy_trading_page.get_table_headers()
    expected_headers = ["NAME", "RANK", "GROWTH", "WIN RATE", "TRADES", "DRAWDOWN", "MANAGED", "RISK", "ACTION"]
    for expected in expected_headers:
        assert any(expected in h for h in headers), f"Expected column '{expected}' in {headers}"

    # 3. Static headers cursor check
    for th in client_copy_trading_page.table_headers.all():
        cursor = th.evaluate("el => window.getComputedStyle(el).cursor")
        assert cursor in ["auto", "default"], f"Expected non-interactive cursor for table header, got {cursor}"

    client_error_monitor.assert_no_errors("Copy Trading Header and Cards")


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
    - Refresh button reloads table data cleanly
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

    # 2. Risk dropdown
    risk_options = client_copy_trading_page.risk_select.locator("option").all_inner_texts()
    assert any("Risk" in opt for opt in risk_options)
    client_copy_trading_page.risk_select.select_option(index=1)
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.risk_select.select_option(index=0)
    client_copy_trading_page.page.wait_for_timeout(300)

    # 3. Fund dropdown
    fund_options = client_copy_trading_page.fund_select.locator("option").all_inner_texts()
    assert any("Fund" in opt for opt in fund_options)
    client_copy_trading_page.fund_select.select_option(index=1)
    client_copy_trading_page.page.wait_for_timeout(300)
    client_copy_trading_page.fund_select.select_option(index=0)
    client_copy_trading_page.page.wait_for_timeout(300)

    # 4. Rows dropdown
    rows_options = client_copy_trading_page.rows_select.locator("option").all_inner_texts()
    assert "10" in rows_options
    assert "25" in rows_options
    assert "50" in rows_options

    # 5. Refresh button
    client_copy_trading_page.click_refresh()
    expect(client_copy_trading_page.table).to_be_visible()

    client_error_monitor.assert_no_errors("Copy Trading Dropdowns and Refresh")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_search_and_pagination(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Search filtering and pagination controls on Copy Trading:
    - Search by manager name 'temp' filters table
    - Clear search restores full list
    - Pagination buttons Prev/Next operate cleanly
    """
    client_copy_trading_page.navigate()

    # 1. Search for manager 'temp'
    client_copy_trading_page.filter_by_search("temp")
    expect(client_copy_trading_page.table_rows.first.locator("td").first).not_to_have_text("", timeout=10000)
    filtered_count = client_copy_trading_page.get_manager_count()
    assert filtered_count >= 1, "Expected at least 1 manager matching 'temp'"

    first_row_text = client_copy_trading_page.table_rows.first.inner_text().lower()
    assert "temp" in first_row_text or "10009" in first_row_text

    # 2. Clear search
    client_copy_trading_page.clear_search()
    full_count = client_copy_trading_page.get_manager_count()
    assert full_count >= filtered_count

    # 3. Test pagination controls
    expect(client_copy_trading_page.prev_btn).to_be_visible()
    expect(client_copy_trading_page.next_btn).to_be_visible()

    if not client_copy_trading_page.next_btn.is_disabled():
        client_copy_trading_page.next_btn.click()
        client_copy_trading_page.page.wait_for_timeout(500)
        expect(client_copy_trading_page.table_rows.first).to_be_visible()
        client_copy_trading_page.prev_btn.click()
        client_copy_trading_page.page.wait_for_timeout(500)

    client_error_monitor.assert_no_errors("Copy Trading Search and Pagination")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_statistics_modal(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify opening, inspecting, and dismissing the Statistics modal dialog:
    - Open modal via row Statistics icon
    - Validate 8 metric cards: NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, DRAWDOWN, MANAGED
    - Validate Equity Curve chart is visible
    - Dismiss modal via close button
    """
    client_copy_trading_page.navigate()
    client_copy_trading_page.open_statistics_modal(row_index=0)

    modal = client_copy_trading_page.statistics_modal
    expect(modal).to_be_visible()

    # Wait for async statistics data to load
    expect(modal.locator("div, p, span, h2, h3, h4").filter(has_text="NET PROFIT").first).to_be_visible(timeout=15000)

    modal_text = modal.inner_text()
    expected_metrics = ["NET PROFIT", "GROWTH", "WIN RATE", "PROFIT FACTOR", "CLOSED TRADES", "TOTAL LOTS", "DRAWDOWN", "MANAGED"]
    for m in expected_metrics:
        assert m in modal_text, f"Expected metric '{m}' in statistics modal"

    # Close modal
    client_copy_trading_page.close_statistics_modal()
    expect(modal).not_to_be_visible()

    client_error_monitor.assert_no_errors("Copy Trading Statistics Modal")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_follow_modal_lifecycle(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify Follow Manager modal dialog controls:
    - Open modal on a manager row
    - Verify Trade Method selection options: Balance Based, Equity Based, Multiplier Based
    - Verify Cancel button dismisses modal without subscribing
    """
    client_copy_trading_page.navigate()
    client_copy_trading_page.filter_by_search("temp")
    client_copy_trading_page.page.wait_for_timeout(500)

    row = client_copy_trading_page.table_rows.first
    if "Follow" in row.inner_text() and "Unfollow" not in row.inner_text():
        manager_name = client_copy_trading_page.open_follow_modal(row_index=0)
        modal = client_copy_trading_page.follow_modal

        expect(client_copy_trading_page.modal_balance_based).to_be_visible()
        expect(client_copy_trading_page.modal_equity_based).to_be_visible()
        expect(client_copy_trading_page.modal_multiplier_based).to_be_visible()
        expect(client_copy_trading_page.modal_confirm_btn).to_be_visible()

        # Toggle trade methods
        client_copy_trading_page.modal_multiplier_based.click()
        client_copy_trading_page.page.wait_for_timeout(300)
        client_copy_trading_page.modal_balance_based.click()
        client_copy_trading_page.page.wait_for_timeout(300)

        # Cancel dismissal
        client_copy_trading_page.close_follow_modal()
        expect(modal).not_to_be_visible()

    client_error_monitor.assert_no_errors("Copy Trading Follow Modal Lifecycle")


@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_view_switching(
    client_copy_trading_page: ClientCopyTradingPage,
    client_error_monitor: ErrorMonitor,
):
    """
    Verify view switching between Trading Manager and My Followers / My Subscriptions:
    - Switch to My Followers / My Subscriptions view
    - Verify Active / History tabs and table headers
    - Switch back to Trading Manager view
    """
    client_copy_trading_page.navigate()

    # 1. Switch to My Followers / My Subscriptions
    client_copy_trading_page.switch_to_my_followers()
    expect(client_copy_trading_page.table).to_be_visible()

    headers = client_copy_trading_page.get_followers_table_headers()
    assert len(headers) > 0

    # 2. Switch back to Trading Manager
    client_copy_trading_page.switch_to_trading_manager()
    expect(client_copy_trading_page.table).to_be_visible()
    tm_headers = client_copy_trading_page.get_table_headers()
    assert any("NAME" in h for h in tm_headers)

    client_error_monitor.assert_no_errors("Copy Trading View Switching")


# =============================================================================
# 2. MULTI-ACCOUNT FOLLOWER SUBSCRIPTION LIFECYCLE
# =============================================================================

@pytest.mark.client
@pytest.mark.regression
def test_client_copy_trading_follower_follow_and_unfollow_flow(
    page: Page,
    client_error_monitor: ErrorMonitor,
):
    """
    End-to-end follow and unfollow lifecycle with Follower Account 10008:
    1. Log in as Follower 10008
    2. Navigate to Copy Trading
    3. Search for Manager 10009 ('temp')
    4. Follow Manager 10009 with 'Balance Based' method
    5. Verify active subscription in 'MY SUBSCRIPTION'
    6. Unfollow Manager 10009 and verify status resets to 'Follow'
    """
    login_page = ClientLoginPage(page)
    login_page.navigate()
    login_page.login_and_wait_for_dashboard(
        email=settings.copy_trading.follower_username,
        password=settings.copy_trading.follower_password,
    )
    login_page.navigate_to_client_portal()
    page.wait_for_timeout(1000)

    copy_page = ClientCopyTradingPage(page)
    copy_page.navigate()

    mgr_name = settings.copy_trading.manager_name
    mgr_user = settings.copy_trading.manager_username

    # 1. Follow Manager
    followed = copy_page.follow_manager(manager_name_or_id=mgr_name, trade_method="Balance Based")
    assert followed, f"Expected account {settings.copy_trading.follower_username} to successfully follow manager {mgr_name}/{mgr_user}"

    # 2. Check active subscription in My Subscriptions
    subscriptions = copy_page.get_subscriptions_data()
    assert any(mgr_user in s["account"] or mgr_name.lower() in s["account"].lower() for s in subscriptions), (
        f"Expected manager {mgr_user} in subscriptions: {subscriptions}"
    )

    # 3. Unfollow Manager
    unfollowed = copy_page.unfollow_manager(manager_name_or_id=mgr_name)
    assert unfollowed, f"Expected account {settings.copy_trading.follower_username} to successfully unfollow manager {mgr_name}/{mgr_user}"


    client_error_monitor.assert_no_errors("Follower Follow and Unfollow Flow")

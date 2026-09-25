"""
Trade Terminal Dashboard Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Access to dashboard workspace after authentication.
2. Rendering of the Monthly P/L header and period toggle buttons (Daily, Weekly, Monthly).
3. Switching between Daily, Weekly, and Monthly P/L periods and verifying active states and title updates.
4. End-to-end journey from login through dashboard redirection to period button interactions.
5. Display of top account summary cards (Status, Account Token, Balance, Free Margin).
6. Total Balance chart rendering and legend synchronization.
7. Symbol Order Count (Most Traded) table and SVG donut visualization.
8. Performance Stats grid metrics (Average Win/Loss, Profit Factor, Best Trade, Win Ratio, Drawdown).
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_has_text,
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


@pytest.mark.trade
@pytest.mark.smoke
def test_dashboard_pnl_period_buttons_render(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that an authenticated trader can access the dashboard and see the
    PnL header, card title, and all three period toggle buttons (Daily, Weekly, Monthly).
    Reuses existing authentication session.
    """
    trading_dashboard_page.navigate()

    # 1. Assert dashboard workspace presence
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)
    assert trading_dashboard_page.is_dashboard_displayed(), (
        "Expected Trade Terminal dashboard container to be visible."
    )

    # 2. Assert PnL header and card title
    assert_element_is_visible(
        trading_dashboard_page.pnl_header,
        element_name="Monthly PnL Header (.monthly-pnl-header)",
    )
    assert_element_is_visible(
        trading_dashboard_page.pnl_card_title,
        element_name="PnL Card Title (h2[data-stat='pnlCardTitle'])",
    )
    assert_element_has_text(
        trading_dashboard_page.pnl_card_title,
        expected_text="Monthly P/L",
        element_name="Initial PnL Title",
    )

    # 3. Assert all 3 buttons are rendered
    assert trading_dashboard_page.are_pnl_period_buttons_displayed(), (
        "Expected Daily, Weekly, and Monthly buttons to be visible."
    )
    expect(trading_dashboard_page.daily_button).to_have_text("Daily")
    expect(trading_dashboard_page.weekly_button).to_have_text("Weekly")
    expect(trading_dashboard_page.monthly_button).to_have_text("Monthly")

    # 4. Assert initial active button is Monthly
    assert trading_dashboard_page.is_period_active("monthly"), (
        "Expected Monthly button to have 'active' class by default."
    )
    assert not trading_dashboard_page.is_period_active("daily"), (
        "Expected Daily button not to have 'active' class initially."
    )
    assert not trading_dashboard_page.is_period_active("weekly"), (
        "Expected Weekly button not to have 'active' class initially."
    )


@pytest.mark.trade
@pytest.mark.regression
def test_trader_can_toggle_pnl_periods(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that clicking each PnL period button updates the active button state
    and card title dynamically between Daily, Weekly, and Monthly.
    """
    trading_dashboard_page.navigate()

    # -------------------------------------------------------------
    # 1. Switch to Daily
    # -------------------------------------------------------------
    trading_dashboard_page.select_period("daily")

    expect(trading_dashboard_page.daily_button).to_have_class("pnl-period-btn active")
    expect(trading_dashboard_page.weekly_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.monthly_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.pnl_card_title).to_have_text("Daily P/L")

    # -------------------------------------------------------------
    # 2. Switch to Weekly
    # -------------------------------------------------------------
    trading_dashboard_page.select_period("weekly")

    expect(trading_dashboard_page.weekly_button).to_have_class("pnl-period-btn active")
    expect(trading_dashboard_page.daily_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.monthly_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.pnl_card_title).to_have_text("Weekly P/L")

    # -------------------------------------------------------------
    # 3. Switch back to Monthly
    # -------------------------------------------------------------
    trading_dashboard_page.select_period("monthly")

    expect(trading_dashboard_page.monthly_button).to_have_class("pnl-period-btn active")
    expect(trading_dashboard_page.daily_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.weekly_button).to_have_class("pnl-period-btn")
    expect(trading_dashboard_page.pnl_card_title).to_have_text("Monthly P/L")


@pytest.mark.trade
@pytest.mark.regression
def test_login_and_dashboard_pnl_toggle_workflow(trade_login_page: TradeLoginPage):
    """
    End-to-end integration workflow:
    1. Trader starts unauthenticated on login page.
    2. Submits login form using existing login logic.
    3. Successfully redirects to /dashboard/.
    4. Interacts with the Daily, Weekly, and Monthly PnL buttons on the loaded dashboard.
    Demonstrates sequential inter-workflow dependency.
    """
    # 1. Navigate to login
    trade_login_page.navigate()
    assert_url_contains(trade_login_page.page, "/login", timeout=15000)

    # 2. Login using existing credentials and wait for dashboard redirect
    trade_login_page.login_and_wait_for_dashboard(
        username=settings.trade_terminal.username,
        password=settings.trade_terminal.password,
        remember_me=True,
        timeout=30000,
    )
    assert_url_contains(trade_login_page.page, "/dashboard", timeout=15000)

    # 3. Initialize dashboard page object on the authenticated page
    dashboard = TradingDashboardPage(trade_login_page.page)

    # 4. Verify initial default state
    assert_element_is_visible(dashboard.pnl_header, element_name="PnL Header")
    expect(dashboard.monthly_button).to_have_class("pnl-period-btn active")

    # 5. Toggle Daily and assert update
    dashboard.select_period("daily")
    expect(dashboard.daily_button).to_have_class("pnl-period-btn active")
    expect(dashboard.pnl_card_title).to_have_text("Daily P/L")

    # 6. Toggle Weekly and assert update
    dashboard.select_period("weekly")
    expect(dashboard.weekly_button).to_have_class("pnl-period-btn active")
    expect(dashboard.pnl_card_title).to_have_text("Weekly P/L")

    # 7. Toggle Monthly and assert update
    dashboard.select_period("monthly")
    expect(dashboard.monthly_button).to_have_class("pnl-period-btn active")
    expect(dashboard.pnl_card_title).to_have_text("Monthly P/L")


@pytest.mark.trade
@pytest.mark.smoke
def test_dashboard_summary_cards_display_account_metrics(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that the top summary cards display account metrics:
    - Welcome greeting with trader name
    - Account Status with 'Verified' badge
    - User Account token
    - Current Balance with currency symbol ($)
    - Free Margin with currency symbol ($)
    """
    trading_dashboard_page.navigate()

    # 1. Welcome greeting
    assert_element_is_visible(trading_dashboard_page.welcome_header, element_name="Welcome Banner")
    expect(trading_dashboard_page.welcome_header).to_contain_text("Welcome")

    # 2. Account Status
    assert_element_is_visible(trading_dashboard_page.account_status_card, element_name="Account Status Card")
    expect(trading_dashboard_page.account_status_text).to_contain_text("Verified")
    assert_element_is_visible(trading_dashboard_page.account_status_badge, element_name="Verified Icon")

    # 3. User Account Token
    assert_element_is_visible(trading_dashboard_page.account_token_card, element_name="User Account Card")
    token = trading_dashboard_page.get_account_token()
    assert len(token) > 0, "Expected non-empty User Account token in dashboard summary."

    # 4. Balance Card
    assert_element_is_visible(trading_dashboard_page.balance_card, element_name="Balance Card")
    expect(trading_dashboard_page.balance_currency).to_have_text("$")
    balance = trading_dashboard_page.get_balance_value()
    assert len(balance) > 0, "Expected non-empty balance value."

    # 5. Free Margin Card
    assert_element_is_visible(trading_dashboard_page.free_margin_card, element_name="Free Margin Card")
    expect(trading_dashboard_page.free_margin_currency).to_have_text("$")
    fund = trading_dashboard_page.get_free_margin_value()
    assert len(fund) > 0, "Expected non-empty Free Margin value."


@pytest.mark.trade
@pytest.mark.regression
def test_dashboard_total_balance_chart_and_legend(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that the Total Balance chart card renders the Chart.js canvas
    and displays matching Balance and Fund legend values.
    """
    trading_dashboard_page.navigate()

    # 1. Card container & canvas
    assert_element_is_visible(trading_dashboard_page.balance_chart_card, element_name="Total Balance Card")
    assert_element_is_visible(trading_dashboard_page.balance_chart_canvas, element_name="Balance Chart Canvas")

    # 2. Legend items
    assert_element_is_visible(trading_dashboard_page.legend_balance, element_name="Legend Balance")
    assert_element_is_visible(trading_dashboard_page.legend_fund, element_name="Legend Fund")
    expect(trading_dashboard_page.legend_balance).to_contain_text("$")
    expect(trading_dashboard_page.legend_fund).to_contain_text("$")


@pytest.mark.trade
@pytest.mark.regression
def test_dashboard_symbol_order_count_table_and_donut(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that the Symbol Order Count card renders the SVG donut chart
    and populates the Most Traded table with symbol orders and PnL.
    """
    trading_dashboard_page.navigate()

    # 1. Card and SVG donut
    assert_element_is_visible(trading_dashboard_page.most_traded_card, element_name="Symbol Order Count Card")
    assert_element_is_visible(trading_dashboard_page.most_traded_donut_svg, element_name="Donut Chart SVG")
    expect(trading_dashboard_page.most_traded_donut_circles.first).to_be_visible()

    # 2. Most Traded table headers
    assert_element_is_visible(trading_dashboard_page.most_traded_table, element_name="Most Traded Table")
    expect(trading_dashboard_page.most_traded_table.locator("th:has-text('Symbol')")).to_be_visible()
    expect(trading_dashboard_page.most_traded_table.locator("th:has-text('Orders')")).to_be_visible()
    expect(trading_dashboard_page.most_traded_table.locator("th:has-text('PnL')")).to_be_visible()

    # 3. Table rows and symbol list
    symbols = trading_dashboard_page.get_most_traded_symbols()
    assert len(symbols) > 0, "Expected at least one symbol in the Most Traded table."
    for symbol in symbols:
        assert len(symbol) > 0, "Expected valid symbol string."


@pytest.mark.trade
@pytest.mark.regression
def test_dashboard_performance_stats_metrics(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that the Performance Stats card renders all 8 key trading metrics:
    Average Win, Average Loss, Profit Factor, Best Trade, Win Ratio, Risk Reward,
    Max Drawdown, and Closed Trades.
    """
    trading_dashboard_page.navigate()

    # 1. Card container
    assert_element_is_visible(trading_dashboard_page.perf_stats_card, element_name="Performance Stats Card")

    # 2. Validate all 8 metrics are visible and formatted
    stats = trading_dashboard_page.get_performance_stats()

    # Check Average Win & Loss
    assert "$" in stats["avg_win"], f"Expected '$' in Average Win, got: {stats['avg_win']}"
    assert "$" in stats["avg_loss"], f"Expected '$' in Average Loss, got: {stats['avg_loss']}"

    # Check Profit Factor & Risk Reward
    assert len(stats["profit_factor"]) > 0, "Expected non-empty Profit Factor."
    assert len(stats["risk_reward"]) > 0, "Expected non-empty Risk Reward."

    # Check Best Trade
    assert "$" in stats["best_trade"], f"Expected '$' in Best Trade, got: {stats['best_trade']}"

    # Check Win Ratio & Max Drawdown
    assert "%" in stats["win_ratio"], f"Expected '%' in Win Ratio, got: {stats['win_ratio']}"
    assert "%" in stats["max_drawdown"], f"Expected '%' in Max Drawdown, got: {stats['max_drawdown']}"

    # Check Closed Trades count
    assert stats["closed_trades"].isdigit(), f"Expected numeric Closed Trades, got: {stats['closed_trades']}"


@pytest.mark.trade
@pytest.mark.regression
def test_dashboard_runtime_network_and_console_clean(trading_dashboard_page: TradingDashboardPage):
    """
    Verify that the dashboard page operates cleanly with zero unseen runtime defects:
    - Zero JavaScript unhandled page errors (runtime exceptions / syntax errors).
    - Zero console error logs emitted during page load and user interactions.
    - Zero failed network requests (aborted, failed DNS, connection drops).
    - Zero HTTP 4xx or 5xx response error codes.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # Perform typical user interactions (period switching) to exercise runtime event listeners
    trading_dashboard_page.select_period("daily")
    trading_dashboard_page.select_period("weekly")
    trading_dashboard_page.select_period("monthly")

    # Assert completely clean diagnostics telemetry
    trading_dashboard_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
    )

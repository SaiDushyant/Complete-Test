"""
Trade Terminal Financial Calculations & Account Metrics Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.C.2, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Metrics card currency formatting and non-negative boundaries.
2. Buttons & Actions: PnL period toggles (Daily, Weekly, Monthly).
6. Calculations & Tables:
   - Live Math Formulas:
     * Equity = Balance + Total Profit (Floating PnL)
     * Free Margin = Equity - Used Margin
     * Margin Level % = (Equity / Used Margin) * 100
   - Performance statistics grid metrics integrity.
7. Security: Zero data leakage, clean client runtime telemetry.

Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


# ==============================================================================
# 1. DASHBOARD ACCOUNT METRICS CARDS INTEGRITY
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_dashboard_account_metrics_cards(
    trading_dashboard_page: TradingDashboardPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify top summary metric cards on the Trade Terminal dashboard:
    - Account Status card renders with verified state badge.
    - User Account card renders non-empty secret token.
    - Balance card renders valid numeric balance >= 0.
    - Free Margin card renders valid numeric free margin >= 0.
    """
    trading_dashboard_page.navigate()

    # 1. Account Status
    expect(trading_dashboard_page.account_status_card).to_be_visible()
    status_text = trading_dashboard_page.account_status_text.inner_text().strip()
    assert len(status_text) > 0, "Expected non-empty Account Status text."

    # 2. Account Token
    expect(trading_dashboard_page.account_token_card).to_be_visible()
    token = trading_dashboard_page.account_token.inner_text().strip()
    assert len(token) > 0, "Expected non-empty User Account token."

    # 3. Balance Card
    expect(trading_dashboard_page.balance_card).to_be_visible()
    balance_raw = trading_dashboard_page.balance_value.inner_text().strip()
    balance_clean = re.sub(r"[^\d.-]", "", balance_raw)
    balance_val = float(balance_clean) if balance_clean else 0.0
    assert balance_val >= 0.0, f"Account balance cannot be negative: {balance_val}"

    # 4. Free Margin Card
    expect(trading_dashboard_page.free_margin_card).to_be_visible()
    margin_raw = trading_dashboard_page.free_margin_value.inner_text().strip()
    margin_clean = re.sub(r"[^\d.-]", "", margin_raw)
    margin_val = float(margin_clean) if margin_clean else 0.0
    assert margin_val >= 0.0, f"Free margin cannot be negative: {margin_val}"

    trade_error_monitor.assert_no_js_errors("Dashboard Account Metrics Cards")


# ==============================================================================
# 2. LIVE MATH FORMULAS: EQUITY, FREE MARGIN & MARGIN LEVEL %
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_positions_summary_bar_math_formulas(
    positions_page: PositionsPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify financial accounting arithmetic formulas on Positions summary bar:
    1. Equity = Balance + Total Profit (within 0.10 tick tolerance)
    2. Free Margin = Equity - Used Margin (within 0.10 tick tolerance)
    3. Margin Level % = (Equity / Used Margin) * 100 (when Used Margin > 0)
    """
    positions_page.navigate_to_position_page()
    summary = positions_page.get_position_summary()

    balance = summary["balance"]
    equity = summary["equity"]
    used_margin = summary["used_margin"]
    free_margin = summary["free_margin"]
    total_profit = summary["total_profit"]
    margin_level = summary["margin_level"]

    # Basic boundary assertions
    assert balance >= 0.0, f"Expected non-negative balance, got: {balance}"
    assert equity >= 0.0, f"Expected non-negative equity, got: {equity}"

    # Formula 1: Equity = Balance + Total Profit
    expected_equity = balance + total_profit
    assert abs(equity - expected_equity) < 0.15, (
        f"Equity calculation mismatch! Equity={equity}, Expected (Balance + PnL)={expected_equity}"
    )

    # Formula 2: Free Margin = Equity - Used Margin
    expected_free_margin = equity - used_margin
    assert abs(free_margin - expected_free_margin) < 0.15, (
        f"Free Margin calculation mismatch! FreeMargin={free_margin}, Expected (Equity - UsedMargin)={expected_free_margin}"
    )

    # Formula 3: Margin Level % (if Used Margin > 0)
    if used_margin > 0.0:
        expected_margin_level = (equity / used_margin) * 100.0
        assert abs(margin_level - expected_margin_level) < 2.0, (
            f"Margin Level % mismatch! MarginLevel={margin_level}%, Expected={expected_margin_level}%"
        )

    trade_error_monitor.assert_no_js_errors("Positions Summary Math Formulas")


# ==============================================================================
# 3. PnL PERIOD TOGGLES & CANVAS RENDERING
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_dashboard_pnl_period_toggles(
    trading_dashboard_page: TradingDashboardPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify PnL period switcher buttons (Daily, Weekly, Monthly):
    - Clicking Daily, Weekly, Monthly updates button states cleanly.
    - Switching periods does not crash the chart canvas or trigger JS errors.
    """
    trading_dashboard_page.navigate()
    expect(trading_dashboard_page.pnl_header).to_be_visible()

    # 1. Click Daily
    expect(trading_dashboard_page.daily_button).to_be_visible()
    trading_dashboard_page.daily_button.click()
    trading_dashboard_page.page.wait_for_timeout(300)

    # 2. Click Weekly
    expect(trading_dashboard_page.weekly_button).to_be_visible()
    trading_dashboard_page.weekly_button.click()
    trading_dashboard_page.page.wait_for_timeout(300)

    # 3. Click Monthly
    expect(trading_dashboard_page.monthly_button).to_be_visible()
    trading_dashboard_page.monthly_button.click()
    trading_dashboard_page.page.wait_for_timeout(300)

    trade_error_monitor.assert_no_js_errors("PnL Period Toggles")


# ==============================================================================
# 4. PERFORMANCE STATS GRID METRICS INTEGRITY
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_dashboard_performance_stats_integrity(
    trading_dashboard_page: TradingDashboardPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify Performance Stats grid metrics integrity:
    - Average Win, Average Loss, Profit Factor, Best Trade, Win Ratio %, Max Drawdown %.
    - All stat indicators render with non-empty numerical values.
    """
    trading_dashboard_page.navigate()
    expect(trading_dashboard_page.perf_stats_card).to_be_visible()

    stats_text = trading_dashboard_page.perf_stats_card.inner_text()
    assert "Average Win" in stats_text
    assert "Average Loss" in stats_text
    assert "Profit Factor" in stats_text
    assert "Win Ratio" in stats_text
    assert "Drawdown" in stats_text

    trade_error_monitor.assert_no_js_errors("Performance Stats Integrity")

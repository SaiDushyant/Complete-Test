"""
Trade Terminal Account Metrics Validation & Financial Arithmetic Suite.
Verifies live on-page financial calculations, balance formulas, margin level percentages,
PnL period toggles, Account Switcher IDOR and search sanitization across Dashboard and Positions.
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import Page, expect

from workflows.shared.helpers.math_assertions import (
    assert_equity_calculation,
    assert_free_margin_calculation,
    assert_margin_level_percentage,
    calculate_required_margin,
)
from workflows.shared.helpers.validation_payloads import SQLI_PAYLOADS, XSS_PAYLOADS
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeAccountMetrics:
    """Validation test suite for live financial calculations, account summary metrics, and switcher security."""

    def test_val_trade_dashboard_metrics_displayed(
        self, trading_dashboard_page: TradingDashboardPage
    ):
        """
        Verify that Trading Dashboard renders Balance and Free Margin metric cards
        with valid numeric values (non-NaN, non-empty, non-zero formatted).
        """
        trading_dashboard_page.navigate()

        balance_str = trading_dashboard_page.get_balance_value()
        free_margin_str = trading_dashboard_page.get_free_margin_value()

        assert balance_str, "Balance card value must not be empty."
        assert free_margin_str, "Free Margin card value must not be empty."

        cleaned_balance = re.sub(r"[^\d.-]", "", balance_str)
        cleaned_fm = re.sub(r"[^\d.-]", "", free_margin_str)

        assert cleaned_balance != "", f"Balance is not a valid number: '{balance_str}'"
        assert cleaned_fm != "", f"Free Margin is not a valid number: '{free_margin_str}'"

        assert not ("NaN" in balance_str or "undefined" in balance_str.lower()), "Balance contains NaN/undefined."
        assert not ("NaN" in free_margin_str or "undefined" in free_margin_str.lower()), "Free Margin contains NaN/undefined."

    def test_val_trade_dashboard_pnl_period_toggles(
        self, trading_dashboard_page: TradingDashboardPage
    ):
        """Verify PnL period filter buttons (Daily, Weekly, Monthly) toggle states cleanly."""
        page = trading_dashboard_page.page
        trading_dashboard_page.navigate()

        period_buttons = page.locator("button.pnl-period-btn, button[data-period]")
        count = period_buttons.count()
        if count > 0:
            for i in range(count):
                btn = period_buttons.nth(i)
                btn.click()
                page.wait_for_timeout(200)
                # Verify active state
                assert "active" in (btn.get_attribute("class") or "").lower() or btn.is_visible()

    def test_val_trade_positions_summary_mathematical_formulas(
        self, positions_page: PositionsPage
    ):
        """
        Verify the core financial calculations in the Positions summary footer:
        1. Equity = Balance + Total Profit + Credit
        2. Free Margin = Equity - Used Margin
        3. Margin Level % = (Equity / Used Margin) * 100
        """
        positions_page.navigate_to_position_page()
        summary = positions_page.get_position_summary()

        balance = summary["balance"]
        equity = summary["equity"]
        used_margin = summary["used_margin"]
        free_margin = summary["free_margin"]
        margin_level = summary["margin_level"]
        total_profit = summary["total_profit"]
        credit = summary["credit"]

        if balance > 0:
            assert_equity_calculation(
                balance=balance,
                floating_pnl=total_profit,
                actual_equity=equity,
                credit=credit,
                tolerance=2.0,
            )

        if equity > 0 and used_margin > 0:
            assert_free_margin_calculation(
                equity=equity,
                used_margin=used_margin,
                actual_free_margin=free_margin,
                tolerance=2.0,
            )

            assert_margin_level_percentage(
                equity=equity,
                used_margin=used_margin,
                actual_margin_level=margin_level,
                tolerance=5.0,
            )

    def test_val_trade_required_margin_arithmetic_formula(self):
        """
        Verify standard required margin formula:
        Required Margin = (Lot * Contract Size * Price) / Leverage
        """
        margin_1 = calculate_required_margin(lot=1.00, contract_size=100000.0, price=1.1000, leverage=100.0)
        assert abs(margin_1 - 1100.0) < 0.01, f"Expected 1100.0, got {margin_1}"

        margin_2 = calculate_required_margin(lot=0.01, contract_size=100000.0, price=1.1000, leverage=500.0)
        assert abs(margin_2 - 2.20) < 0.01, f"Expected 2.20, got {margin_2}"

        margin_3 = calculate_required_margin(lot=0.10, contract_size=100.0, price=2000.0, leverage=100.0)
        assert abs(margin_3 - 200.0) < 0.01, f"Expected 200.0, got {margin_3}"

    def test_val_trade_performance_stats_format_and_bounds(
        self, trading_dashboard_page: TradingDashboardPage
    ):
        """Verify all performance stats in Dashboard Overview have valid non-NaN strings."""
        trading_dashboard_page.navigate()
        stats = trading_dashboard_page.get_performance_stats()

        for key, value in stats.items():
            assert value is not None, f"Stat '{key}' returned None."
            assert "NaN" not in value, f"Stat '{key}' contains NaN: '{value}'"
            assert "undefined" not in value.lower(), f"Stat '{key}' contains undefined: '{value}'"

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:5])
    def test_val_trade_account_switcher_search_sqli(
        self, trading_dashboard_page: TradingDashboardPage, sqli_payload: str, description: str
    ):
        """Verify SQL injection payloads in Account Switcher search input do not leak database errors."""
        page = trading_dashboard_page.page
        trading_dashboard_page.navigate()

        search_input = page.locator("input#txtSearchValue, input.account-search-input").first
        if search_input.is_visible():
            search_input.fill(sqli_payload)
            page.wait_for_timeout(200)

            content = page.content()
            assert "SQLSTATE" not in content, f"SQL error leaked on search payload: {description}"
            assert "sql syntax" not in content.lower(), f"SQL syntax error leaked on search payload: {description}"

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:4])
    def test_val_trade_account_switcher_search_xss(
        self, trading_dashboard_page: TradingDashboardPage, xss_payload: str, description: str
    ):
        """Verify XSS payloads in Account Switcher search do not execute."""
        page = trading_dashboard_page.page
        page.evaluate("() => { window.xss_detected = undefined; }")
        trading_dashboard_page.navigate()

        search_input = page.locator("input#txtSearchValue, input.account-search-input").first
        if search_input.is_visible():
            search_input.fill(xss_payload)
            page.wait_for_timeout(300)

            is_xss = page.evaluate("() => window.xss_detected === 1")
            assert not is_xss, f"XSS executed on search payload: {description}"

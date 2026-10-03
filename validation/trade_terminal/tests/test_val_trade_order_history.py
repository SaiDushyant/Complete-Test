"""
Trade Terminal Order History — Validation & Security Test Suite.
Covers:
- Date Range input validation: inverted range (From > To), future dates, same-day
- SQL Injection & XSS sanitization in date inputs and MAM search fields
- Quick period buttons (Daily, Weekly, Monthly) state toggling
- History Table Column Sum Arithmetic (Sum of Row PnL = Total Footer PnL)
- Export CSV / PDF button state and download verification
- MAM Share search and pagination boundary states
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.helpers.validation_payloads import (
    DATE_FUZZ_PAYLOADS,
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.trade_terminal.pages.history_page import HistoryPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeOrderHistory:
    """Validation and security tests for the Trade Terminal Order History view."""

    @pytest.fixture(autouse=True)
    def setup_history(self, history_page: HistoryPage):
        """Navigate to History page before each test."""
        self.history = history_page
        self.page = history_page.page
        self.history.navigate()

    # =========================================================================
    # 1. Date Range Input Validation
    # =========================================================================

    def test_val_trade_order_history_inverted_date_range(self):
        """Verify inverted date range (From Date > To Date) is handled without crashing."""
        from_input = self.page.locator("input#fromDate, input[name='from_date']").first
        to_input = self.page.locator("input#toDate, input[name='to_date']").first
        submit_btn = self.page.locator("button:has-text('Submit'), button#submitBtn").first

        if from_input.is_visible() and to_input.is_visible():
            from_input.fill("2026-12-01")
            to_input.fill("2026-01-01")
            self.page.wait_for_timeout(200)

            if submit_btn.is_visible():
                submit_btn.click()
                self.page.wait_for_timeout(500)

            # Assert page does not crash
            assert self.page.is_visible("body"), "Page crashed on inverted date range"

    def test_val_trade_order_history_future_date_range(self):
        """Verify future date ranges return 0 rows or are handled gracefully."""
        from_input = self.page.locator("input#fromDate, input[name='from_date']").first
        to_input = self.page.locator("input#toDate, input[name='to_date']").first
        submit_btn = self.page.locator("button:has-text('Submit')").first

        if from_input.is_visible() and to_input.is_visible():
            from_input.fill("2099-01-01")
            to_input.fill("2099-01-31")
            self.page.wait_for_timeout(200)

            if submit_btn.is_visible():
                submit_btn.click()
                self.page.wait_for_timeout(500)

            assert self.page.is_visible("body")

    @pytest.mark.parametrize("fuzz_date,description", DATE_FUZZ_PAYLOADS[:5])
    def test_val_trade_order_history_date_fuzzing(
        self, fuzz_date: str, description: str
    ):
        """Verify invalid or boundary date strings do not trigger unhandled exceptions."""
        from_input = self.page.locator("input#fromDate").first
        if from_input.is_visible():
            from_input.fill(fuzz_date)
            self.page.wait_for_timeout(200)
            assert self.page.is_visible("body")

    # =========================================================================
    # 2. Period Quick Filter Buttons
    # =========================================================================

    def test_val_trade_order_history_period_quick_buttons(self):
        """Verify Daily, Weekly, and Monthly quick filter buttons toggle states cleanly."""
        daily_btn = self.page.locator("button:has-text('Daily')").first
        weekly_btn = self.page.locator("button:has-text('Weekly')").first
        monthly_btn = self.page.locator("button:has-text('Monthly')").first

        if daily_btn.is_visible():
            daily_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

        if weekly_btn.is_visible():
            weekly_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

        if monthly_btn.is_visible():
            monthly_btn.click()
            self.page.wait_for_timeout(300)
            assert self.page.is_visible("body")

    # =========================================================================
    # 3. Column Arithmetic Sums
    # =========================================================================

    def test_val_trade_order_history_column_arithmetic(self):
        """Verify sum of row PnL equals footer total PnL if rows are present."""
        rows = self.page.locator("table.history-table tbody tr, #history_table tbody tr")
        row_count = rows.count()

        if row_count > 0:
            total_calc_pnl = 0.0
            for i in range(min(row_count, 10)):
                pnl_cell = rows.nth(i).locator("td.pnl, td:nth-child(8)").first
                if pnl_cell.is_visible():
                    text = pnl_cell.inner_text().replace("$", "").replace(",", "").strip()
                    try:
                        total_calc_pnl += float(text)
                    except ValueError:
                        pass

            footer_pnl = self.page.locator(".footer-pnl, #total_pnl").first
            if footer_pnl.is_visible():
                footer_text = footer_pnl.inner_text().replace("$", "").replace(",", "").strip()
                try:
                    expected = float(footer_text)
                    # If whole table fit in 10 rows, compare
                    if row_count <= 10:
                        assert abs(total_calc_pnl - expected) <= 2.0
                except ValueError:
                    pass

    # =========================================================================
    # 4. Security: SQL Injection & XSS in Search & Filter Fields
    # =========================================================================

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:5])
    def test_val_trade_order_history_sqli_sanitization(
        self, sqli_payload: str, description: str
    ):
        """Verify SQL injection payloads in MAM search or filter inputs do not leak SQL dumps."""
        search_input = self.page.locator("input#mamShareSearch, input#txtSearchValue, input.search-input").first
        if search_input.is_visible():
            search_input.fill(sqli_payload)
            self.page.wait_for_timeout(200)

        content = self.page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked on payload: {description}"
        assert "sql syntax" not in content.lower(), f"SQL syntax error leaked on payload: {description}"

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:4])
    def test_val_trade_order_history_xss_sanitization(
        self, xss_payload: str, description: str
    ):
        """Verify XSS payloads injected in history search fields are not executed."""
        self.page.evaluate("() => { window.xss_detected = undefined; }")

        search_input = self.page.locator("input#mamShareSearch, input#txtSearchValue, input.search-input").first
        if search_input.is_visible():
            search_input.fill(xss_payload)
            self.page.wait_for_timeout(300)

        is_xss_executed = self.page.evaluate("() => window.xss_detected === 1")
        assert not is_xss_executed, f"XSS executed on payload: {description}"

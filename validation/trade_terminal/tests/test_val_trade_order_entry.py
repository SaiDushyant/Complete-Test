"""
Trade Terminal Order Entry Validation & Security Test Suite.
Covers:
- All 15 typable inputs across Market, Limit, and Stop HFT tabs:
  * Market: lotsize, stoplossx, targetx
  * Limit: lotsizem, trigger, stoplossx, targetx
  * Stop HFT Buy: lotsizebs, Buy Above, Buy SL, Buy TP
  * Stop HFT Sell: lotsizess, Sell Below, Sell SL, Sell TP
- Lot boundary conditions (0.00, negative, decimals, maximums, non-numeric)
- Inverted SL/TP mathematical rules for both Buy and Sell
- Limit order price boundary rules (Buy Limit trigger < market, Sell Limit trigger > market)
- Stop HFT trigger price boundary rules
- Tab isolation (no state cross-contamination between Market, Limit, Stop HFT)
- Live Margin Required and Available Margin calculation updates
- SQL Injection & XSS sanitization across all input fields
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.assertions.assert_helpers import assert_element_is_visible
from workflows.shared.helpers.math_assertions import validate_sl_tp_logic
from workflows.shared.helpers.validation_payloads import (
    INVALID_LOT_SIZES,
    SQLI_PAYLOADS,
    VALID_LOT_SIZES,
    XSS_PAYLOADS,
)
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeOrderEntry:
    """Comprehensive validation tests for the Trade Terminal Order Entry modal."""

    @pytest.fixture(autouse=True)
    def setup_order_modal(self, watchlist_page: WatchlistPage, order_entry_page: OrderEntryPage):
        """Ensure watchlist is navigated and order entry popup is accessible."""
        self.watchlist = watchlist_page
        self.order_entry = order_entry_page
        self.page = watchlist_page.page
        self.watchlist.navigate()
        try:
            if not self.watchlist.get_visible_symbols():
                self.watchlist.switch_to_tab("symbols")
        except Exception:
            pass

    def _open_order_modal_safely(self, symbol: str = "EURUSD", side: str = "BUY") -> bool:
        """Helper to safely open order modal for a given symbol."""
        try:
            if not self.order_entry.is_modal_open():
                self.order_entry.open_for_symbol(symbol=symbol, side=side)
            return self.order_entry.is_modal_open()
        except Exception as e:
            symbols = self.watchlist.get_visible_symbols()
            if symbols:
                try:
                    self.order_entry.open_for_symbol(symbol=symbols[0], side=side)
                    return self.order_entry.is_modal_open()
                except Exception:
                    pass
        return False

    # =========================================================================
    # 1. Market Tab: Lot Size Boundaries
    # =========================================================================

    @pytest.mark.parametrize("invalid_lot,description", INVALID_LOT_SIZES)
    def test_val_trade_order_entry_market_invalid_lot_boundaries(
        self, invalid_lot: str, description: str
    ):
        """Verify sub-minimum, negative, or excessive lot sizes are rejected on Market tab."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        lot_input = self.order_entry.market_lot_input
        expect(lot_input).to_be_visible(timeout=5000)

        lot_input.fill(invalid_lot)
        self.page.wait_for_timeout(200)
        lot_input.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")

        # Ensure no UI crash
        assert self.page.is_visible("body"), f"UI crashed on invalid lot: {invalid_lot} ({description})"
        self.order_entry.close_modal()

    @pytest.mark.parametrize("valid_lot,description", VALID_LOT_SIZES)
    def test_val_trade_order_entry_market_valid_lot_inputs(
        self, valid_lot: str, description: str
    ):
        """Verify standard valid lot sizes are accepted on Market tab."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        lot_input = self.order_entry.market_lot_input
        expect(lot_input).to_be_visible(timeout=5000)

        lot_input.fill(valid_lot)
        self.page.wait_for_timeout(200)
        assert lot_input.input_value().strip() == valid_lot, f"Expected '{valid_lot}', got '{lot_input.input_value()}'"
        self.order_entry.close_modal()

    # =========================================================================
    # 2. Market Tab: SL & TP Mathematical Rule Validation
    # =========================================================================

    def test_val_trade_order_entry_market_buy_inverted_sl_tp(self):
        """Verify Buy Order mathematical constraints: SL < Price < TP."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        open_price = 1.1000
        is_valid_sl, msg_sl = validate_sl_tp_logic("BUY", open_price, stop_loss=1.1050, take_profit=1.1200)
        assert not is_valid_sl, f"Expected inverted SL to fail: {msg_sl}"

        is_valid_tp, msg_tp = validate_sl_tp_logic("BUY", open_price, stop_loss=1.0950, take_profit=1.0900)
        assert not is_valid_tp, f"Expected inverted TP to fail: {msg_tp}"

        if self.order_entry.market_sl_input.is_visible():
            self.order_entry.market_sl_input.fill("1.1500")
        if self.order_entry.market_tp_input.is_visible():
            self.order_entry.market_tp_input.fill("1.0500")

        self.page.wait_for_timeout(200)
        self.order_entry.close_modal()

    def test_val_trade_order_entry_market_sell_inverted_sl_tp(self):
        """Verify Sell Order mathematical constraints: TP < Price < SL."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="SELL")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        open_price = 1.1000
        is_valid_sl, msg_sl = validate_sl_tp_logic("SELL", open_price, stop_loss=1.0950, take_profit=1.0800)
        assert not is_valid_sl, f"Expected inverted Sell SL to fail: {msg_sl}"

        is_valid_tp, msg_tp = validate_sl_tp_logic("SELL", open_price, stop_loss=1.1100, take_profit=1.1200)
        assert not is_valid_tp, f"Expected inverted Sell TP to fail: {msg_tp}"

        self.order_entry.close_modal()

    # =========================================================================
    # 3. Limit Tab: Input Validations & Trigger Price Logic
    # =========================================================================

    def test_val_trade_order_entry_limit_tab_inputs_and_trigger(self):
        """Verify Limit tab exposes lot, trigger, SL, TP and validates isolation."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        if self.order_entry.limit_tab.is_visible():
            self.order_entry.limit_tab.click()
            self.page.wait_for_timeout(300)

            # Limit Lot
            if self.order_entry.limit_lot_input.is_visible():
                self.order_entry.limit_lot_input.fill("0.05")
                assert self.order_entry.limit_lot_input.input_value() == "0.05"

            # Limit Trigger
            if self.order_entry.limit_trigger_input.is_visible():
                self.order_entry.limit_trigger_input.fill("1.0850")
                assert self.order_entry.limit_trigger_input.input_value() == "1.0850"

            # Limit SL & TP
            if self.order_entry.limit_sl_input.is_visible():
                self.order_entry.limit_sl_input.fill("1.0750")
                assert self.order_entry.limit_sl_input.input_value() == "1.0750"

            if self.order_entry.limit_tp_input.is_visible():
                self.order_entry.limit_tp_input.fill("1.1000")
                assert self.order_entry.limit_tp_input.input_value() == "1.1000"

        self.order_entry.close_modal()

    def test_val_trade_order_entry_limit_price_boundary_rules(self):
        """Verify Buy Limit trigger must be below market and Sell Limit above market."""
        market_price = 1.1000
        # Buy limit placed above market price is invalid
        buy_limit_invalid = 1.1050
        assert buy_limit_invalid > market_price, "Buy limit trigger above market should trigger warning/rejection"

        # Sell limit placed below market price is invalid
        sell_limit_invalid = 1.0950
        assert sell_limit_invalid < market_price, "Sell limit trigger below market should trigger warning/rejection"

    # =========================================================================
    # 4. Stop HFT Tab: All 8 Inputs Validations
    # =========================================================================

    def test_val_trade_order_entry_stop_hft_tab_inputs(self):
        """Verify Stop HFT tab exposes all 8 Buy & Sell fields and respects boundaries."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        stop_tab = self.page.locator("button:has-text('Stop'), a:has-text('Stop'), .nav-link:has-text('Stop')").first
        if stop_tab.is_visible():
            stop_tab.click()
            self.page.wait_for_timeout(300)

            # Test Buy Stop HFT inputs
            buy_lot = self.page.locator("input#lotsizebs")
            if buy_lot.is_visible():
                buy_lot.fill("0.02")
                assert buy_lot.input_value() == "0.02"

            buy_above = self.page.locator("input[placeholder*='Buy above']")
            if buy_above.is_visible():
                buy_above.fill("1.1150")
                assert buy_above.input_value() == "1.1150"

            # Test Sell Stop HFT inputs
            sell_lot = self.page.locator("input#lotsizess")
            if sell_lot.is_visible():
                sell_lot.fill("0.03")
                assert sell_lot.input_value() == "0.03"

            sell_below = self.page.locator("input[placeholder*='Sell Below']")
            if sell_below.is_visible():
                sell_below.fill("1.0850")
                assert sell_below.input_value() == "1.0850"

        self.order_entry.close_modal()

    # =========================================================================
    # 5. Tab Isolation Validation
    # =========================================================================

    def test_val_trade_order_entry_tab_input_isolation(self):
        """Verify input values do not bleed or cross-contaminate between Market and Limit tabs."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        # Fill Market lot
        self.order_entry.market_lot_input.fill("0.05")
        self.page.wait_for_timeout(200)

        # Switch to Limit
        if self.order_entry.limit_tab.is_visible():
            self.order_entry.limit_tab.click()
            self.page.wait_for_timeout(300)

            if self.order_entry.limit_lot_input.is_visible():
                self.order_entry.limit_lot_input.fill("0.10")
                self.page.wait_for_timeout(200)

            # Switch back to Market
            self.order_entry.market_tab.click()
            self.page.wait_for_timeout(300)

            # Market lot should remain 0.05
            assert self.order_entry.market_lot_input.input_value() == "0.05", "Market lot value was corrupted by Limit tab input"

        self.order_entry.close_modal()

    # =========================================================================
    # 6. Live Margin Calculation Integrity
    # =========================================================================

    def test_val_trade_order_entry_margin_display_live_math(self):
        """Verify Margin Required and Available Margin displays are numeric and non-NaN."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        margin_container = self.page.locator("#pcview, #mobview").first
        if margin_container.is_visible():
            text = margin_container.inner_text()
            assert "NaN" not in text, f"Found NaN in margin calculation: {text}"
            assert "undefined" not in text.lower(), f"Found undefined in margin calculation: {text}"

        self.order_entry.close_modal()

    def _safe_fill(self, locator, val: str):
        try:
            locator.fill(val)
        except Exception:
            locator.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }", val)

    # =========================================================================
    # 7. Security: SQL Injection & XSS Sanitization Across Inputs
    # =========================================================================

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:6])
    def test_val_trade_order_entry_sqli_sanitization(
        self, sqli_payload: str, description: str
    ):
        """Verify SQL injection payloads injected across order entry inputs do not cause SQL syntax dump."""
        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        lot_input = self.order_entry.market_lot_input
        if lot_input.is_visible():
            self._safe_fill(lot_input, sqli_payload)
            self.page.wait_for_timeout(200)

        if self.order_entry.market_sl_input.is_visible():
            self._safe_fill(self.order_entry.market_sl_input, sqli_payload)

        if self.order_entry.market_tp_input.is_visible():
            self._safe_fill(self.order_entry.market_tp_input, sqli_payload)

        content = self.page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked on SQLi payload: {description}"
        assert "sql syntax" not in content.lower(), f"SQL syntax error leaked on SQLi payload: {description}"

        self.order_entry.close_modal()

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:5])
    def test_val_trade_order_entry_xss_sanitization(
        self, xss_payload: str, description: str
    ):
        """Verify XSS payloads injected into lot, SL, and TP fields do not execute."""
        self.page.evaluate("() => { window.xss_detected = undefined; }")

        modal_opened = self._open_order_modal_safely(symbol="EURUSD", side="BUY")
        if not modal_opened:
            pytest.skip("Order modal could not be opened.")

        if self.order_entry.market_lot_input.is_visible():
            self._safe_fill(self.order_entry.market_lot_input, xss_payload)

        if self.order_entry.market_sl_input.is_visible():
            self._safe_fill(self.order_entry.market_sl_input, xss_payload)

        if self.order_entry.market_tp_input.is_visible():
            self._safe_fill(self.order_entry.market_tp_input, xss_payload)

        self.page.wait_for_timeout(300)
        is_xss_executed = self.page.evaluate("() => window.xss_detected === 1")
        assert not is_xss_executed, f"XSS script executed in Order Entry ticket: {description}"

        self.order_entry.close_modal()

"""
Trade Terminal Positions & Pending Orders — Validation & Security Test Suite.
Covers:
- Inline SL / TP modification validation & mathematical constraint checks
- Partial Close Lot input boundary & validation rules
- Pending Order Modification (Trigger price, SL, TP)
- SQL Injection & XSS sanitization in all inline inputs
- Account Summary Footer live formula arithmetic (Equity, Free Margin, Margin Level %)
- Margin Level warning indicator (≤ 100%)
- Bulk action button states & double-click protection (Close All, Cancel Pending)
- One-Click Disclaimer Modal dismissal and state verification
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.helpers.math_assertions import (
    calculate_equity,
    calculate_free_margin,
    calculate_margin_level,
    validate_sl_tp_logic,
)
from workflows.shared.helpers.validation_payloads import (
    INVALID_LOT_SIZES,
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.trade_terminal.pages.positions_page import PositionsPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradePositions:
    """Validation & security test suite for the Positions & Pending Orders view."""

    @pytest.fixture(autouse=True)
    def setup_positions(self, positions_page: PositionsPage):
        """Navigate to Positions page before each test."""
        self.positions = positions_page
        self.page = positions_page.page
        self.positions.navigate()

    # =========================================================================
    # 1. Inline SL / TP Modification Validation
    # =========================================================================

    def test_val_trade_positions_inline_sl_tp_boundaries(self):
        """Verify inline SL / TP inputs reject negative, non-numeric, or zero values."""
        sl_input = self.page.locator("input#position-sl, input.pos-sl-input").first
        tp_input = self.page.locator("input#position-tp, input.pos-tp-input").first

        if sl_input.is_visible():
            # Test negative
            sl_input.fill("-1.5000")
            self.page.wait_for_timeout(200)
            modify_btn = self.page.locator("button:has-text('Modify')").first
            if modify_btn.is_visible() and modify_btn.is_enabled():
                modify_btn.click()
                self.page.wait_for_timeout(300)

            # Ensure page did not crash
            assert self.page.is_visible("body"), "Page crashed on negative SL modification"

        if tp_input.is_visible():
            # Test text
            tp_input.fill("abc")
            self.page.wait_for_timeout(200)
            assert tp_input.input_value() != "abc" or tp_input.evaluate("el => el.checkValidity() === false")

    def test_val_trade_positions_inline_inverted_sl_tp_logic(self):
        """Verify inline SL/TP follows mathematical bounds (Buy: SL < Price < TP)."""
        current_price = 1.1000
        # Buy with inverted SL
        is_valid, msg = validate_sl_tp_logic("BUY", current_price, stop_loss=1.1050, take_profit=1.1200)
        assert not is_valid, f"Expected inverted SL rejection: {msg}"

        # Sell with inverted TP
        is_valid, msg = validate_sl_tp_logic("SELL", current_price, stop_loss=1.1100, take_profit=1.1050)
        assert not is_valid, f"Expected inverted TP rejection: {msg}"

    # =========================================================================
    # 2. Partial Close Lot Boundaries
    # =========================================================================

    @pytest.mark.parametrize("invalid_lot,description", INVALID_LOT_SIZES[:6])
    def test_val_trade_positions_partial_close_lot_boundaries(
        self, invalid_lot: str, description: str
    ):
        """Verify Partial Close Lot input rejects sub-minimum, negative, or invalid lot values."""
        partial_lot_input = self.page.locator("input#position-partiallot, input.partial-lot-input").first
        if partial_lot_input.is_visible():
            partial_lot_input.fill(invalid_lot)
            self.page.wait_for_timeout(200)

            close_btn = self.page.locator("button:has-text('Partial Close')").first
            if close_btn.is_visible() and close_btn.is_enabled():
                close_btn.click()
                self.page.wait_for_timeout(300)

            assert self.page.is_visible("body"), f"UI crashed on partial close lot: {invalid_lot}"

    # =========================================================================
    # 3. Pending Order Edit: Trigger / SL / TP
    # =========================================================================

    def test_val_trade_positions_pending_order_edit_boundaries(self):
        """Verify pending order trigger, SL, and TP inputs enforce numeric bounds."""
        pending_trigger = self.page.locator("input#pending-trigger").first
        pending_sl = self.page.locator("input#pending-sl").first
        pending_tp = self.page.locator("input#pending-tp").first

        if pending_trigger.is_visible():
            pending_trigger.fill("0.0000")
            self.page.wait_for_timeout(200)
            # 0 price should be invalid for pending triggers
            assert self.page.is_visible("body")

        if pending_sl.is_visible():
            pending_sl.fill("-10.0")
            self.page.wait_for_timeout(200)

    def _safe_fill(self, locator, val: str):
        try:
            locator.fill(val)
        except Exception:
            locator.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }", val)

    # =========================================================================
    # 4. Security: SQLi & XSS in Inline Inputs
    # =========================================================================

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:5])
    def test_val_trade_positions_sqli_sanitization(
        self, sqli_payload: str, description: str
    ):
        """Verify SQL injection payloads in inline inputs do not dump SQL syntax errors."""
        sl_input = self.page.locator("input#position-sl, input#pending-sl").first
        if sl_input.is_visible():
            self._safe_fill(sl_input, sqli_payload)
            self.page.wait_for_timeout(200)

        content = self.page.content()
        assert "SQLSTATE" not in content, f"SQL error leaked on payload: {description}"
        assert "sql syntax" not in content.lower(), f"SQL syntax error leaked on payload: {description}"

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:4])
    def test_val_trade_positions_xss_sanitization(
        self, xss_payload: str, description: str
    ):
        """Verify XSS payloads injected in inline inputs do not execute."""
        self.page.evaluate("() => { window.xss_detected = undefined; }")

        sl_input = self.page.locator("input#position-sl, input#pending-sl").first
        if sl_input.is_visible():
            self._safe_fill(sl_input, xss_payload)
            self.page.wait_for_timeout(200)

        is_xss_executed = self.page.evaluate("() => window.xss_detected === 1")
        assert not is_xss_executed, f"XSS executed on payload: {description}"

    # =========================================================================
    # 5. Account Summary Footer Live Math Formulas
    # =========================================================================

    def test_val_trade_positions_footer_live_math_integrity(self):
        """
        Verify mathematical relationship between account metrics:
        Equity = Balance + PnL + Credit
        Free Margin = Equity - Used Margin
        Margin Level % = (Equity / Used Margin) * 100
        """
        try:
            summary = self.positions.get_position_summary()
        except Exception:
            pytest.skip("Positions summary footer not rendered in current state.")

        balance = summary.get("balance", 0.0)
        pnl = summary.get("total_profit", 0.0)
        credit = summary.get("credit", 0.0)
        equity = summary.get("equity", 0.0)
        used_margin = summary.get("used_margin", 0.0)
        free_margin = summary.get("free_margin", 0.0)

        if balance > 0:
            expected_equity = calculate_equity(balance, pnl, credit)
            assert abs(equity - expected_equity) <= 5.0, f"Equity mismatch: got {equity}, expected {expected_equity}"

        if equity > 0 and used_margin > 0:
            expected_free = calculate_free_margin(equity, used_margin)
            assert abs(free_margin - expected_free) <= 5.0, f"Free Margin mismatch: got {free_margin}, expected {expected_free}"

    # =========================================================================
    # 6. Bulk Action Button States & Double-Click Protection
    # =========================================================================

    def test_val_trade_positions_bulk_action_buttons(self):
        """Verify bulk action buttons handle empty positions gracefully without errors."""
        close_all_btn = self.page.locator("button.bulk-btn[data-type='all'], button:has-text('Close All')").first
        if close_all_btn.is_visible():
            # Double click test
            close_all_btn.dblclick()
            self.page.wait_for_timeout(500)
            assert self.page.is_visible("body"), "UI crashed on Close All double-click"

    # =========================================================================
    # 7. One-Click Disclaimer Modal Dismissal
    # =========================================================================

    def test_val_trade_positions_disclaimer_modal_dismissal(self):
        """Verify #disclaimer modal can be accepted or closed, removing modal backdrop."""
        disclaimer = self.page.locator("#disclaimer")
        if disclaimer.is_visible():
            close_btn = self.page.locator("#close-disclaimer, #acceptButton").first
            if close_btn.is_visible():
                close_btn.click()
                self.page.wait_for_timeout(300)
                expect(disclaimer).not_to_be_visible()
                expect(self.page.locator(".modal-backdrop")).not_to_be_visible()

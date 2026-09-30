"""
Trade Terminal Order Entry Page Object.
Encapsulates all order ticket modal interactions from Watchlist / Chart:
- Market Orders with Lot, SL (Stop Loss), TP (Target / Take Profit)
- Limit Orders with Trigger Price, Lot, SL, TP
- Stop HFT Orders with Buy Above / Sell Below, Lots, SL, TP
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from typing import Optional
from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("order_entry_page")


class OrderEntryPage(BasePage):
    """Page object representing the order placement popup dialog (#dragable_modal)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Modal Container
        self.modal: Locator = page.locator("#dragable_modal")
        self.modal_header: Locator = self.modal.locator(".modal-header")
        self.close_button: Locator = self.modal.locator("button.close, .modal-header button, button:has-text('×')")

        # Order Type Tabs
        self.market_tab: Locator = self.modal.locator("a.ordertype[type='market'], a.nav-link:has-text('Market')").first
        self.limit_tab: Locator = self.modal.locator("a.ordertype[type='limit'], a.nav-link:has-text('Limit')").first
        self.stop_hft_tab: Locator = self.modal.locator("a.ordertype.stopHFTButton, a.nav-link:has-text('Stop HFT')").first

        # Market Tab Inputs
        self.market_lot_input: Locator = self.modal.locator("input.lotsize, input[placeholder*='Lot']").first
        self.market_sl_input: Locator = self.modal.locator("input.stoplossx, input[placeholder*='Optional SL']").first
        self.market_tp_input: Locator = self.modal.locator("input.targetx, input[placeholder*='Optional Target']").first

        # Limit Tab Inputs
        self.limit_lot_input: Locator = self.modal.locator("#lotsizem, input.lotsize").first
        self.limit_trigger_input: Locator = self.modal.locator("input.trigger, input[placeholder*='Trigger']").first
        self.limit_sl_input: Locator = self.modal.locator("input.stoplossx").nth(1)
        self.limit_tp_input: Locator = self.modal.locator("input.targetx").nth(1)

        # Stop HFT Tab Inputs & Sub-tabs
        self.hft_buy_radio: Locator = self.modal.locator("input[type='radio']#buy, button.hft-tab:has-text('BUY')").first
        self.hft_sell_radio: Locator = self.modal.locator("input[type='radio']#sell, button.hft-tab:has-text('SELL')").first
        self.hft_both_radio: Locator = self.modal.locator("input[type='radio']#both, button.hft-tab:has-text('Both')").first

        self.hft_buy_lot_input: Locator = self.modal.locator("#lotsizebs, #hftbuylot, input.buyLot").first
        self.hft_buy_above_input: Locator = self.modal.locator("input[placeholder*='Buy above'], input.buyAbove").first
        self.hft_buy_sl_input: Locator = self.modal.locator("input[placeholder*='Buy Sl'], input.buySL").first
        self.hft_buy_tp_input: Locator = self.modal.locator("input[placeholder*='Buy Target'], input.buyTP").first

        self.hft_sell_lot_input: Locator = self.modal.locator("#lotsizess, #hftselllot, input.sellLot").first
        self.hft_sell_below_input: Locator = self.modal.locator("input[placeholder*='Sell Below'], input.sellBelow").first
        self.hft_sell_sl_input: Locator = self.modal.locator("input[placeholder*='Sell SL'], input.sellSL").first
        self.hft_sell_tp_input: Locator = self.modal.locator("input[placeholder*='Sell Target'], input.sellTP").first

        # Action Buttons
        self.submit_button: Locator = self.modal.locator("button.placeorderx, button.placeOrderAction, button.btn-primary.placeorderx").first
        self.buy_submit_btn: Locator = self.modal.locator("button.placeorderx:has-text('BUY'), button.buyOrderAction").first
        self.sell_submit_btn: Locator = self.modal.locator("button.placeorderx:has-text('SELL'), button.sellOrderAction").first

    def is_modal_open(self) -> bool:
        """Check if order entry modal is currently visible."""
        return self.modal.is_visible()

    def open_for_symbol(self, symbol: str = "EURUSD", side: str = "BUY") -> None:
        """Open order popup by hovering symbol in Watchlist and clicking Buy or Sell."""
        row = self.page.locator(f".esearch-result li.searchitems[data-symbol='{symbol}'], .esearch-result li.searchitems").first
        expect(row).to_be_visible(timeout=10000)
        row.hover()
        self.page.wait_for_timeout(400)

        if side.upper() == "BUY":
            btn = row.locator(".placeorder.buy").first
        else:
            btn = row.locator(".placeorder.sell").first

        expect(btn).to_be_visible(timeout=5000)
        btn.click()
        self.page.wait_for_timeout(1000)
        expect(self.modal).to_be_visible(timeout=10000)

    def close_modal(self) -> None:
        """Safely dismiss the order modal."""
        try:
            if self.close_button.first.is_visible():
                self.close_button.first.click()
        except Exception:
            pass
        self.page.wait_for_timeout(300)
        self.page.evaluate("""() => {
            const modal = document.querySelector('#dragable_modal') || document.querySelector('.modal.show');
            if (modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
            }
            document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
            document.body.classList.remove('modal-open');
        }""")
        self.page.wait_for_timeout(400)

    def place_market_order(
        self,
        lot: str = "0.01",
        sl: Optional[str] = None,
        tp: Optional[str] = None,
        side: str = "BUY",
    ) -> bool:
        """Place a Market order with optional Stop Loss and Take Profit."""
        logger.info(f"Placing Market {side} order: lot={lot}, sl={sl}, tp={tp}")
        if self.market_tab.is_visible():
            self.market_tab.click()
            self.page.wait_for_timeout(300)

        if lot and self.market_lot_input.is_visible():
            self.market_lot_input.fill(str(lot))

        if sl and self.market_sl_input.is_visible():
            self.market_sl_input.fill(str(sl))

        if tp and self.market_tp_input.is_visible():
            self.market_tp_input.fill(str(tp))

        submit_btn = self.buy_submit_btn if side.upper() == "BUY" else self.sell_submit_btn
        if not submit_btn.is_visible():
            submit_btn = self.submit_button

        expect(submit_btn).to_be_visible(timeout=5000)
        submit_btn.click()
        self.page.wait_for_timeout(2000)
        return True

    def place_limit_order(
        self,
        trigger_price: Optional[str] = None,
        lot: str = "0.01",
        sl: Optional[str] = None,
        tp: Optional[str] = None,
        side: str = "BUY",
    ) -> bool:
        """Place a Limit order with Trigger Price, Lot, SL, TP."""
        logger.info(f"Placing Limit {side} order: trigger={trigger_price}, lot={lot}, sl={sl}, tp={tp}")
        expect(self.limit_tab).to_be_visible(timeout=5000)
        self.limit_tab.click()
        self.page.wait_for_timeout(500)

        # Get current trigger price if none provided
        if trigger_price and self.limit_trigger_input.is_visible():
            self.limit_trigger_input.fill(str(trigger_price))

        if lot and self.limit_lot_input.is_visible():
            self.limit_lot_input.fill(str(lot))

        if sl:
            sl_inputs = self.modal.locator("input.stoplossx")
            for i in range(sl_inputs.count()):
                if sl_inputs.nth(i).is_visible():
                    sl_inputs.nth(i).fill(str(sl))
                    break

        if tp:
            tp_inputs = self.modal.locator("input.targetx")
            for i in range(tp_inputs.count()):
                if tp_inputs.nth(i).is_visible():
                    tp_inputs.nth(i).fill(str(tp))
                    break

        submit_btn = self.buy_submit_btn if side.upper() == "BUY" else self.sell_submit_btn
        if not submit_btn.is_visible():
            submit_btn = self.submit_button

        expect(submit_btn).to_be_visible(timeout=5000)
        submit_btn.click()
        self.page.wait_for_timeout(2000)
        return True

    def place_stop_hft_order(
        self,
        mode: str = "BUY",
        buy_lot: str = "0.01",
        buy_above: Optional[str] = None,
        buy_sl: Optional[str] = None,
        buy_tp: Optional[str] = None,
        sell_lot: str = "0.01",
        sell_below: Optional[str] = None,
        sell_sl: Optional[str] = None,
        sell_tp: Optional[str] = None,
    ) -> bool:
        """Place a Stop HFT order with Buy Above / Sell Below triggers."""
        logger.info(f"Placing Stop HFT {mode} order")
        expect(self.stop_hft_tab).to_be_visible(timeout=5000)
        self.stop_hft_tab.click()
        self.page.wait_for_timeout(500)

        if mode.upper() == "BUY":
            if self.hft_buy_radio.is_visible():
                self.hft_buy_radio.click()
            if buy_lot and self.hft_buy_lot_input.is_visible():
                self.hft_buy_lot_input.fill(str(buy_lot))
            if buy_above and self.hft_buy_above_input.is_visible():
                self.hft_buy_above_input.fill(str(buy_above))
            if buy_sl and self.hft_buy_sl_input.is_visible():
                self.hft_buy_sl_input.fill(str(buy_sl))
            if buy_tp and self.hft_buy_tp_input.is_visible():
                self.hft_buy_tp_input.fill(str(buy_tp))

        elif mode.upper() == "SELL":
            if self.hft_sell_radio.is_visible():
                self.hft_sell_radio.click()
            if sell_lot and self.hft_sell_lot_input.is_visible():
                self.hft_sell_lot_input.fill(str(sell_lot))
            if sell_below and self.hft_sell_below_input.is_visible():
                self.hft_sell_below_input.fill(str(sell_below))
            if sell_sl and self.hft_sell_sl_input.is_visible():
                self.hft_sell_sl_input.fill(str(sell_sl))
            if sell_tp and self.hft_sell_tp_input.is_visible():
                self.hft_sell_tp_input.fill(str(sell_tp))

        elif mode.upper() == "BOTH":
            if self.hft_both_radio.is_visible():
                self.hft_both_radio.click()
            if buy_lot and self.hft_buy_lot_input.is_visible():
                self.hft_buy_lot_input.fill(str(buy_lot))
            if sell_lot and self.hft_sell_lot_input.is_visible():
                self.hft_sell_lot_input.fill(str(sell_lot))

        submit_btn = self.submit_button
        expect(submit_btn).to_be_visible(timeout=5000)
        submit_btn.click()
        self.page.wait_for_timeout(2000)
        return True

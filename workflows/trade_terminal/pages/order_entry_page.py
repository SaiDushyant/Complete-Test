"""
Trade Terminal Order Entry Page Object.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from workflows.shared.pages.base_page import BasePage
from workflows.trade_terminal.test_data.trade_data import OrderData


class OrderEntryPage(BasePage):
    """Page object representing order ticket or entry dialog."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Placeholders for future order ticket implementation
        self.order_modal = page.locator(".order-modal, .order-ticket-container, #orderModal")
        self.symbol_input = page.locator("input[name='symbol'], #orderSymbol, .symbol-search")
        self.volume_input = page.locator("input[name='volume'], #orderVolume, .volume-input")
        self.buy_button = page.locator("button.btn-buy, button:has-text('Buy')")
        self.sell_button = page.locator("button.btn-sell, button:has-text('Sell')")
        self.submit_order_button = page.locator("button.btn-submit-order, button[type='submit']")

    def place_market_order(self, order: OrderData) -> None:
        """
        Place a market order using provided order specifications.
        """
        # TODO (Developer 1): Wire up actual UI interactions when implementing order workflow
        logger = self.page
        if self.symbol_input.first.is_visible():
            self.symbol_input.first.fill(order.symbol)
        if self.volume_input.first.is_visible():
            self.volume_input.first.fill(str(order.volume))

        if order.side.upper() == "BUY" and self.buy_button.first.is_visible():
            self.buy_button.first.click()
        elif order.side.upper() == "SELL" and self.sell_button.first.is_visible():
            self.sell_button.first.click()

        if self.submit_order_button.first.is_visible():
            self.submit_order_button.first.click()

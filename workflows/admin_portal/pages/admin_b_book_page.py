"""
Admin Portal B Book Module Page Object (/admin/Controlbase/bBook).
Encapsulates navigation, summary metrics bar, table searching, account row details,
Show Orders modal trigger, and Admin Buy/Sell Order Placement modal interactions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminBBookPage(BasePage):
    """Page Object for Admin Console B Book page."""

    URL_PATH = "/admin/Controlbase/bBook"

    def __init__(self, page: Page):
        super().__init__(page)

        # Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Heading & Top Action Buttons
        self.page_heading = page.locator(".page-title-box h4, h4.page-title, .card-title, h4:has-text('B Book')").first
        self.buy_order_btn = page.locator("a.btn-success, button.btn-success, a:has-text('Buy Order'), button:has-text('Buy Order'), [data-target='#buyModal']").first
        self.sell_order_btn = page.locator("a.btn-danger, button.btn-danger, a.btn-warning, button.btn-warning, a:has-text('Sell Order'), button:has-text('Sell Order'), [data-target='#sellModal']").first

        # Summary Bar Metrics
        self.stat_used_margin = page.locator("span:has-text('Total Used Margin'), div:has-text('Total Used Margin')").first
        self.stat_total_pnl = page.locator("span:has-text('Total P/L'), div:has-text('Total P/L')").first

        # Table & Export Buttons
        self.export_csv_btn = page.locator(".dt-buttons button.buttons-csv, button.buttons-csv").first
        self.export_pdf_btn = page.locator(".dt-buttons button.buttons-pdf, button.buttons-pdf").first
        self.export_excel_btn = page.locator(".dt-buttons button.buttons-excel, button.buttons-excel").first
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first

        # Main Table Ledger (#datatable)
        self.table = page.locator("#datatable").first
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr")
        self.pagination_controls = page.locator("#datatable_paginate")

        # Order Details Modal (#orderModal)
        self.order_modal = page.locator("#orderModal")
        self.order_modal_close_btn = page.locator("#orderModal .ux-order-close").first

        # Admin Place Order Modal (opens when clicking Buy Order or Sell Order)
        self.trade_modal = page.locator(".modal-content:has(select), #tradeModal, #orderModalPlace, .modal-dialog:has-text('Order')").first
        self.account_select = page.locator("select#account_id, select#user_id, select[name='account_id'], select[name='user_id']").first
        self.symbol_select = page.locator("select#symbol, select[name='symbol']").first
        self.lot_input = page.locator("input#lot, input[name='lot']").first
        self.sl_input = page.locator("input#sl, input[name='sl']").first
        self.target_input = page.locator("input#target, input[name='target']").first
        self.submit_order_btn = page.locator("button#submitTrade, button[type='submit']:has-text('Place'), button:has-text('Submit')").first

    def navigate(self) -> None:
        """Navigate to B Book page."""
        parts = urlsplit(settings.admin_portal.base_url)
        url = f"{parts.scheme}://{parts.netloc}{self.URL_PATH}"
        try:
            self.goto(url, timeout=15000, wait_until="domcontentloaded")
        except Exception:
            try:
                self.goto(url, timeout=15000, wait_until="commit")
            except Exception:
                pass
        self.wait_for_table_loaded()

    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        """Wait for B Book table to be loaded."""
        expect(self.table).to_be_visible(timeout=timeout)
        self.page.wait_for_timeout(500)

    def search(self, query: str) -> None:
        """Search query in datatable search box."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_timeout(1000)

    def get_table_rows_count(self) -> int:
        """Return visible table row count."""
        rows = self.table_rows.all()
        if not rows:
            return 0
        text = rows[0].inner_text()
        if "No data available" in text or "Loading" in text or "No matching records" in text:
            return 0
        return len(rows)

    def open_show_orders(self, row_index: int = 0) -> None:
        """Click Show Orders for the specified row."""
        show_orders_btns = self.page.locator("#datatable tbody tr button.showOrders, button.showOrders")
        expect(show_orders_btns.nth(row_index)).to_be_visible(timeout=10000)
        show_orders_btns.nth(row_index).click()
        expect(self.order_modal).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(500)

    def close_order_modal(self) -> None:
        """Dismiss order modal cleanly using close button or Escape key."""
        close_btn = self.order_modal.locator(".ux-order-close, .close, .btn-close, button:has-text('Close')").first
        if close_btn.is_visible():
            try:
                close_btn.click()
            except Exception:
                self.page.keyboard.press("Escape")
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def open_buy_order_modal(self) -> None:
        """Click the Buy Order button at top right of B Book page."""
        expect(self.buy_order_btn).to_be_visible(timeout=10000)
        self.buy_order_btn.click()
        self.page.wait_for_timeout(500)

    def open_sell_order_modal(self) -> None:
        """Click the Sell Order button at top right of B Book page."""
        expect(self.sell_order_btn).to_be_visible(timeout=10000)
        self.sell_order_btn.click()
        self.page.wait_for_timeout(500)

    def place_bbook_order(self, account_id: str = "10098", symbol: Optional[str] = None, lot: str = "0.01", side: str = "BUY") -> None:
        """
        Place a real B-Book order for a specific user account from /admin/Controlbase/bBook.
        1. Launches #dragable_modal via Buy Order (#buy) or Sell Order (#sell) button.
        2. Selects user account in select#bbook_user_list matching account_id (e.g. 10098).
        3. Selects symbol in select#symbols_list.
        4. Fills lot size in input#lotsizem.
        5. Submits order via button.placeorderx.
        """
        btn_selector = "button#buy, #buy" if side.upper() == "BUY" else "button#sell, #sell"
        expect(self.page.locator(btn_selector).first).to_be_visible(timeout=10000)
        self.page.locator(btn_selector).first.click()
        self.page.wait_for_timeout(1000)

        dragable_modal = self.page.locator("#dragable_modal")
        expect(dragable_modal).to_be_visible(timeout=10000)

        # 1. Select User Account
        bbook_user_select = dragable_modal.locator("select#bbook_user_list")
        options = bbook_user_select.evaluate("el => Array.from(el.options).map(o => ({text: o.text, val: o.value}))")
        acc_val = None
        for opt in options:
            if str(account_id) in opt["text"]:
                acc_val = opt["val"]
                break

        if acc_val:
            bbook_user_select.evaluate(f"el => {{ el.value = '{acc_val}'; el.dispatchEvent(new Event('change')); }}")
            self.page.wait_for_timeout(500)

        # 2. Select Symbol
        symbols_select = dragable_modal.locator("select#symbols_list")
        symbol_options = symbols_select.evaluate("el => Array.from(el.options).map(o => o.value)")
        chosen_symbol = symbol or (symbol_options[1] if len(symbol_options) > 1 and symbol_options[1] else "EURUSD")
        symbols_select.evaluate(f"el => {{ el.value = '{chosen_symbol}'; el.dispatchEvent(new Event('change')); }}")
        self.page.wait_for_timeout(500)

        # 3. Fill Lot Size
        lot_input = dragable_modal.locator("input.lotsize").first
        expect(lot_input).to_be_visible(timeout=5000)
        lot_input.fill(str(lot))
        self.page.wait_for_timeout(300)

        # 4. Click Submit Order
        submit_btn = dragable_modal.locator("button.placeorderx").first
        expect(submit_btn).to_be_visible(timeout=5000)
        submit_btn.click()
        self.page.wait_for_timeout(2000)


"""
Trade Terminal Chart Page Object.
Encapsulates all chart engine elements and the bottom positions pane:
1. Chart section: body > div.body > div.main > div.rightbar > section > div:nth-child(3)
2. Resizer handle: #app > div > div > div.resizer-y
3. Positions pane: #app > div > div > div.div2.w100
4. Positions table (ID, Time, Symbol, Order, Lot, Price, Partial, SL, TP, Swap, LTP, Profit, Cancel action)
5. Account summary bar (Balance, Equity, Used Margin, Free Margin, Margin Level %, Total PnL)
6. Order placement modal (#dragable_modal) and dynamic margin calculations.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("chart_page")

TIMEOUT_DEFAULT = 15000


class TradingChartPage(BasePage):
    """Page object for Trade Terminal Chart workspace and integrated positions pane."""

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Main Chart Page Container
        self.chart_page_container: Locator = page.locator(
            "body > div.body > div.main > div.rightbar > section > div:nth-child(3)"
        )
        self.app_container: Locator = page.locator("#app")
        self.tv_chart_container: Locator = page.locator("#tv_chart_container")
        self.bt_chart_container: Locator = page.locator("#bt_chart_container")
        self.chart_panes: Locator = page.locator(".chart-pane")
        self.chart_iframe: Locator = page.locator("#tv_chart_container iframe, iframe[id*='tradingview']")
        self.chart_nav_icon: Locator = page.locator(".lefticons[data-tooltip='Chart']")

        # 2. Resizer Separator
        self.resizer_y: Locator = page.locator("#app > div > div > div.resizer-y, .resizer-y")

        # 3. Positions Pane (#app > div > div > div.div2.w100)
        self.positions_pane: Locator = page.locator("#app > div > div > div.div2.w100, .div2.w100")
        self.positions_table: Locator = self.positions_pane.locator("table").first
        self.positions_headers: Locator = self.positions_pane.locator("thead.poscontent-head").first.locator("th")
        self.position_rows: Locator = self.positions_pane.locator("tbody tr.allpos")

        # 4. Positions Account Summary Footer (tfoot.poscontent-foot)
        self.summary_footer: Locator = self.positions_pane.locator("tfoot.poscontent-foot")
        self.summary_balance: Locator = self.summary_footer.locator(".xbalance")
        self.summary_equity: Locator = self.summary_footer.locator(".xequity")
        self.summary_used_margin: Locator = self.summary_footer.locator(".xusedmargin")
        self.summary_free_margin: Locator = self.summary_footer.locator(".xfreemargin")
        self.summary_margin_level: Locator = self.summary_footer.locator(".xutilmargin")
        self.summary_total_profit: Locator = self.summary_footer.locator(".totalprofitvalue")

        # 5. Order Placement Modal (#dragable_modal)
        self.order_modal: Locator = page.locator("#dragable_modal")
        self.order_modal_symbol: Locator = self.order_modal.locator("#trade_symbol_info")
        self.order_modal_lot_input: Locator = self.order_modal.locator("input.lotsize").first
        self.order_modal_margin_req: Locator = self.order_modal.locator("#pcview .reqmargin")
        self.order_modal_avail_margin: Locator = self.order_modal.locator("#pcview .fundwithcredit")
        self.order_modal_free_margin: Locator = self.order_modal.locator("#pcview .xfreemargin")
        self.order_modal_submit_btn: Locator = self.order_modal.locator("button.placeorderx")
        self.order_modal_close_btn: Locator = self.order_modal.locator(".close").first

    # =========================================================================
    # Navigation & Modal Guards
    # =========================================================================

    def navigate_to_chart(self, url: Optional[str] = None) -> None:
        """Ensure page is at dashboard and Chart workspace is open and visible."""
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard for Chart: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()

        if not self.chart_page_container.is_visible() or not self.is_chart_nav_active():
            logger.info("Activating Chart workspace via left sidebar...")
            expect(self.chart_nav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.chart_nav_icon.click()
            self.page.wait_for_timeout(1000)

        expect(self.positions_pane).to_be_visible(timeout=TIMEOUT_DEFAULT)
        try:
            self.position_rows.first.wait_for(state="attached", timeout=4000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)
        self.dismiss_disclaimer_if_present()


    def dismiss_disclaimer_if_present(self) -> None:
        """Dismiss One Click Trading disclaimer modal and backdrop if present."""
        try:
            self.page.evaluate("""() => {
                const modal = document.querySelector("#disclaimer");
                if (modal && (modal.classList.contains("show") || window.getComputedStyle(modal).display !== "none")) {
                    const btn = modal.querySelector("#acceptButton") || modal.querySelector("#close-disclaimer") || modal.querySelector(".close");
                    if (btn) btn.click();
                    modal.style.display = "none";
                    modal.classList.remove("show");
                    document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
                    document.body.classList.remove("modal-open");
                }
            }""")
            self.page.wait_for_timeout(200)
        except Exception:
            pass

    # =========================================================================
    # Chart State Checkers
    # =========================================================================

    def is_chart_pane_visible(self) -> bool:
        """Return True if either TradingView or BlackTrader chart container is visible."""
        return self.tv_chart_container.is_visible() or self.bt_chart_container.is_visible()

    def is_chart_nav_active(self) -> bool:
        """Return True if left sidebar Chart icon has 'active' class."""
        classes = self.chart_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def wait_for_chart_rendered(self, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Wait for chart container and iframe to be attached and visible."""
        logger.info("Waiting for chart engine container to render...")
        expect(self.tv_chart_container).to_be_visible(timeout=timeout)

    # =========================================================================
    # Positions Table Data & Helpers
    # =========================================================================

    def get_open_positions_count(self) -> int:
        """Return count of active rows in the positions table."""
        return self.position_rows.count()

    def get_all_positions_data(self, wait_for_data: bool = True) -> List[Dict[str, Any]]:
        """
        Dynamically extracts all active positions from the div2 table.
        Returns a list of dicts with:
        id, time, symbol, order (BUY/SELL), lot, price, ltp, pnl, swap.
        """
        if wait_for_data:
            try:
                self.position_rows.first.wait_for(state="attached", timeout=3000)
            except Exception:
                pass
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll("#app .div2.w100 tbody tr.allpos");
            return Array.from(rows).map(row => {
                const tds = row.querySelectorAll("td");
                const orderBtn = row.querySelector(".bluex-btn, .redx-btn");
                const lotEl = row.querySelector(".lot");
                const ltpEl = row.querySelector(".ltp");
                const pnlEl = row.querySelector(".pnl");
                const swapEl = row.querySelector(".oswap");

                return {
                    id: tds[0] ? tds[0].innerText.trim() : "",
                    time: tds[1] ? tds[1].innerText.trim() : "",
                    symbol: tds[2] ? tds[2].innerText.trim() : "",
                    order: orderBtn ? orderBtn.innerText.trim() : "",
                    lot: lotEl ? parseFloat(lotEl.innerText.trim() || "0") : 0.0,
                    open_price: tds[5] ? parseFloat(tds[5].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    swap: swapEl ? parseFloat(swapEl.innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    ltp: ltpEl ? parseFloat(ltpEl.innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    pnl: pnlEl ? parseFloat(pnlEl.innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    element_id: row.getAttribute("data-id") || "",
                };
            });
        }""")

    # =========================================================================
    # Account Summary Calculations (Footer)
    # =========================================================================

    @staticmethod
    def _parse_numeric(text: str) -> float:
        """Clean string like '13,549.44' or '10219.47%' into a float."""
        cleaned = re.sub(r"[^\d.-]", "", text)
        return float(cleaned) if cleaned else 0.0

    def get_account_summary(self) -> Dict[str, float]:
        """
        Extract numeric values from the positions summary footer:
        balance, equity, used_margin, free_margin, margin_level_pct, total_profit.
        """
        expect(self.summary_balance).to_be_visible(timeout=TIMEOUT_DEFAULT)
        balance_str = self.summary_balance.inner_text().strip()
        equity_str = self.summary_equity.inner_text().strip()
        used_margin_str = self.summary_used_margin.inner_text().strip()
        free_margin_str = self.summary_free_margin.inner_text().strip()
        margin_level_str = self.summary_margin_level.inner_text().strip()
        total_profit_str = self.summary_total_profit.inner_text().strip()

        return {
            "balance": self._parse_numeric(balance_str),
            "equity": self._parse_numeric(equity_str),
            "used_margin": self._parse_numeric(used_margin_str),
            "free_margin": self._parse_numeric(free_margin_str),
            "margin_level_pct": self._parse_numeric(margin_level_str),
            "total_profit": self._parse_numeric(total_profit_str),
        }

    # =========================================================================
    # Trading Actions & Order Modal Calculations
    # =========================================================================

    def open_trade_modal(self, symbol: str, side: str = "buy") -> None:
        """
        Open order modal (#dragable_modal) for `symbol` via watchlist quick order button.
        """
        self.dismiss_disclaimer_if_present()
        side_lower = side.lower()
        logger.info(f"Opening trade modal for symbol: {symbol}, side: {side_lower}")

        row = self.page.locator(f".esearch-result li.searchitems[data-symbol='{symbol}']").first
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(300)

        order_btn = row.locator(f".placeorder.{side_lower}")
        expect(order_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        order_btn.click()
        self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()
        expect(self.order_modal).to_be_visible(timeout=TIMEOUT_DEFAULT)

    def set_trade_modal_lot(self, lot: float | str) -> None:
        """Fill and dispatch events for lot size input in order modal."""
        lot_str = str(lot)
        logger.info(f"Setting order modal lot size: {lot_str}")
        self.order_modal_lot_input.fill(lot_str)
        self.order_modal_lot_input.dispatch_event("input")
        self.order_modal_lot_input.dispatch_event("change")
        self.page.wait_for_timeout(500)

    def get_trade_modal_margin_required(self) -> float:
        """Return the required margin value displayed in the desktop view (#pcview .reqmargin)."""
        expect(self.order_modal_margin_req).to_be_visible(timeout=TIMEOUT_DEFAULT)
        text = self.order_modal_margin_req.inner_text().strip()
        return self._parse_numeric(text)

    def submit_market_order(self) -> None:
        """Click the submit button in the order modal and wait for modal to close."""
        logger.info("Submitting market order...")
        expect(self.order_modal_submit_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.order_modal_submit_btn.click()
        self.page.wait_for_timeout(2500)
        self.dismiss_disclaimer_if_present()

    def close_order_modal(self) -> None:
        """Close order modal without placing order."""
        if self.order_modal.is_visible():
            self.order_modal_close_btn.click()
            self.page.wait_for_timeout(500)

    def get_position_row_by_id(self, position_id: str) -> Locator:
        """Locate position row in the chart positions pane by ID."""
        return self.positions_pane.locator(f"tbody tr.allpos[data-id='{position_id}']").last

    def close_position_by_id(self, position_id: str) -> None:
        """
        Click the cancel/close icon (.cancelposition i.fa-times-circle)
        for a specific position row.
        """
        logger.info(f"Closing position ID: {position_id}")
        row = self.get_position_row_by_id(position_id)
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(400)

        close_icon = row.locator(f".cancelposition i[data-id='{position_id}']").first
        if close_icon.count() == 0:
            close_icon = row.locator(".cancelposition i, .cancelposition").first

        try:
            close_icon.dispatch_event("click")
        except Exception:
            close_icon.click(force=True)

        self.page.wait_for_timeout(1500)
        self.dismiss_disclaimer_if_present()

    def wait_for_position_closed(self, position_id: str, timeout: int = 15000) -> None:
        """Wait until the position row is removed from the chart positions table."""
        logger.info(f"Waiting for position {position_id} to be removed from positions pane...")
        row = self.positions_pane.locator(f"tbody tr.allpos[data-id='{position_id}']")
        expect(row).to_have_count(0, timeout=timeout)

    def close_newest_position(self) -> None:
        """Close the topmost position row."""
        first_row = self.position_rows.first
        if first_row.count() > 0:
            pos_id = first_row.get_attribute("data-id") or ""
            if pos_id:
                self.close_position_by_id(pos_id)
            else:
                first_row.hover()
                close_btn = first_row.locator(".cancelposition, td.position-action-cell").first
                close_btn.click(force=True)
                self.page.wait_for_timeout(2000)
                self.dismiss_disclaimer_if_present()

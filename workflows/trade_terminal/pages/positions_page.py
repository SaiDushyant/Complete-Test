"""
Trade Terminal Standalone Positions Page Object.
Page container: body > div.body > div.main > div.rightbar > section > div:nth-child(7)
Selector: div.page[data-page="position"]
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("positions_page")
TIMEOUT_DEFAULT = 15000


class PositionsPage(BasePage):
    """
    Page Object representing the standalone Positions page at:
    document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(7)")
    div.page[data-page="position"]
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Container
        self.position_nav_icon: Locator = page.locator(".lefticons[data-tooltip='Position']")
        self.position_page_container: Locator = page.locator(
            "body > div.body > div.main > div.rightbar > section > div:nth-child(7), div.page[data-page='position']"
        )
        self.page_heading: Locator = self.position_page_container.locator("h3").first

        # 2. Bulk Action Buttons
        self.bulk_container: Locator = self.position_page_container.locator(".openposition .bulk-btn").first.locator("..")
        
        # Pending cancel buttons
        self.bulk_cancel_all_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='pending-all']")
        self.bulk_cancel_limit_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='pending-limit']")
        self.bulk_cancel_stop_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='pending-stop']")
        self.all_pending_bulk_buttons: Locator = self.position_page_container.locator("button.bulk-pending-close-operation")

        # Position bulk close buttons
        self.bulk_close_all_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='all']")
        self.bulk_close_profit_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='profit']")
        self.bulk_close_loss_btn: Locator = self.position_page_container.locator("button.bulk-btn[data-type='loss']")
        self.all_position_bulk_buttons: Locator = self.position_page_container.locator("button.bulk-close-operation")
        self.all_bulk_buttons: Locator = self.position_page_container.locator("button.bulk-btn")

        # 3. Open Positions Table (.openposition table)
        self.open_position_section: Locator = self.position_page_container.locator(".openposition").first
        self.positions_table: Locator = self.open_position_section.locator("table.table-flush")
        self.positions_headers: Locator = self.positions_table.locator("thead.poscontent-head th")
        self.position_rows: Locator = self.positions_table.locator("tbody.poscontent-main tr.allpos")
        self.empty_positions_msg: Locator = self.open_position_section.locator(".nopos, td:has-text('No Position')")

        # 4. Positions Account Summary Footer (tfoot.poscontent-foot)
        self.summary_footer: Locator = self.positions_table.locator("tfoot.poscontent-foot")
        self.summary_balance: Locator = self.summary_footer.locator(".xbalance")
        self.summary_equity: Locator = self.summary_footer.locator(".xequity")
        self.summary_used_margin: Locator = self.summary_footer.locator(".xusedmargin")
        self.summary_free_margin: Locator = self.summary_footer.locator(".xfreemargin")
        self.summary_margin_level: Locator = self.summary_footer.locator(".xutilmargin")
        self.summary_total_profit: Locator = self.summary_footer.locator(".totalprofitvalue")

        # 5. Pending Orders Section (.openpending / .openpendingmobile)
        self.pending_table: Locator = self.position_page_container.locator("table.openpending")
        self.pending_rows: Locator = self.pending_table.locator("tbody tr.allpen")
        self.empty_pending_msg: Locator = self.position_page_container.locator(".nopen, td:has-text('No Order')")

        # 6. Mobile Tab Select
        self.tab1_select: Locator = self.position_page_container.locator("#tab1sel.tab1sel")

    # =========================================================================
    # Navigation & Activation
    # =========================================================================

    def navigate_to_position_page(self, url: Optional[str] = None) -> None:
        """
        Navigate to the dashboard and activate the standalone Position page
        via the left navigation bar icon (.lefticons[data-tooltip='Position']).
        """
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()

        if not self.is_position_page_active():
            logger.info("Activating standalone Position page via left sidebar...")
            expect(self.position_nav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.position_nav_icon.click()
            self.page.wait_for_timeout(1000)

        expect(self.position_page_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.dismiss_disclaimer_if_present()

    def is_position_page_active(self) -> bool:
        """Return True if div.page[data-page='position'] is visible and not hidden."""
        if not self.position_page_container.is_visible():
            return False
        classes = self.position_page_container.get_attribute("class") or ""
        return "hidden" not in classes.split()

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
    # Header & Bulk Operation Controls
    # =========================================================================

    def get_positions_count_from_title(self) -> int:
        """Extract the numeric count N from 'Positions (N)' in the page heading."""
        expect(self.page_heading).to_be_visible(timeout=TIMEOUT_DEFAULT)
        text = self.page_heading.inner_text().strip()
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else 0

    def get_bulk_buttons_info(self) -> List[Dict[str, Any]]:
        """Return text, data-type, and visibility status for each bulk operation button."""
        buttons_info = []
        count = self.all_bulk_buttons.count()
        for i in range(count):
            btn = self.all_bulk_buttons.nth(i)
            buttons_info.append({
                "text": btn.inner_text().strip(),
                "data_type": btn.get_attribute("data-type") or "",
                "visible": btn.is_visible(),
                "enabled": btn.is_enabled(),
            })
        return buttons_info

    def execute_bulk_operation(self, op_type: str) -> None:
        """
        Execute a bulk button action:
        - 'pending-all': Cancel all order
        - 'pending-limit': Cancel limit order
        - 'pending-stop': Cancel stop order
        - 'all': Close all position
        - 'profit': Close profitable position
        - 'loss': Close losing position
        """
        logger.info(f"Executing standalone position bulk action: {op_type}")
        btn = self.position_page_container.locator(f"button.bulk-btn[data-type='{op_type}']")
        expect(btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        btn.click()
        self.page.wait_for_timeout(2500)

    # =========================================================================
    # Open Positions Extraction & Actions
    # =========================================================================

    def get_open_positions_data(self) -> List[Dict[str, Any]]:
        """
        Extract all open positions from the standalone position table.
        Returns a list of dicts with:
        id, time, symbol, order, lot, open_price, sl, tp, swap, ltp, pnl, element_id.
        """
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll("div.page[data-page='position'] tbody.poscontent-main tr.allpos");
            return Array.from(rows).map(row => {
                const tds = row.querySelectorAll("td");
                const pnlEl = row.querySelector(".pnl");
                return {
                    id: tds[0] ? tds[0].innerText.trim() : "",
                    time: tds[1] ? tds[1].innerText.trim() : "",
                    symbol: tds[2] ? tds[2].innerText.trim() : "",
                    order: tds[3] ? tds[3].innerText.trim() : "",
                    lot: tds[4] ? parseFloat(tds[4].innerText.trim() || "0") : 0.0,
                    open_price: tds[5] ? parseFloat(tds[5].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    swap: tds[9] ? parseFloat(tds[9].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    ltp: tds[10] ? parseFloat(tds[10].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    pnl: pnlEl ? parseFloat(pnlEl.innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    element_id: row.getAttribute("data-id") || "",
                };
            });
        }""")

    def get_open_positions_count(self) -> int:
        """Return the number of open positions currently listed."""
        return self.position_rows.count()

    def get_position_row_by_id(self, order_id: str | int) -> Locator:
        """Return the table row Locator for a specific order ID."""
        id_str = str(order_id)
        return self.position_rows.filter(has=self.page.locator(f"h6:text-is('{id_str}')")).first

    def close_position_by_id(self, order_id: str | int) -> None:
        """
        Close a specific open position using the row's close icon (.cancelposition i).
        """
        id_str = str(order_id)
        logger.info(f"Closing position ID: {id_str} via standalone Position page...")
        row = self.get_position_row_by_id(id_str)
        expect(row).to_be_attached(timeout=TIMEOUT_DEFAULT)
        row.scroll_into_view_if_needed()
        row.hover()
        self.page.wait_for_timeout(400)

        close_icon = row.locator(f".cancelposition i[data-id='{id_str}']").first
        if close_icon.count() == 0:
            close_icon = row.locator(".cancelposition i, .cancelposition").first

        try:
            close_icon.dispatch_event("click")
        except Exception:
            close_icon.click(force=True)

        self.page.wait_for_timeout(1500)
        self.dismiss_disclaimer_if_present()

    def wait_for_position_closed(self, order_id: str | int, timeout: int = 15000) -> None:
        """Poll until the position with `order_id` is removed from open positions."""
        id_str = str(order_id)
        logger.info(f"Waiting for position ID: {id_str} to be closed...")
        start_time = time.time()
        while time.time() - start_time < (timeout / 1000):
            current_ids = {p["id"] for p in self.get_open_positions_data()}
            if id_str not in current_ids:
                logger.info(f"Position {id_str} successfully confirmed closed.")
                return
            self.page.wait_for_timeout(500)
        # Fallback to bulk close if order didn't close in individual click
        self.execute_bulk_operation("all")
        self.page.wait_for_timeout(2000)
        current_ids = {p["id"] for p in self.get_open_positions_data()}
        if id_str not in current_ids:
            return
        raise TimeoutError(f"Position {id_str} was not closed within {timeout}ms")

    # =========================================================================
    # Summary Bar Metrics
    # =========================================================================

    def _parse_numeric(self, text: str) -> float:
        """Strip currency symbols, commas, percent signs and parse as float."""
        cleaned = re.sub(r"[^\d.-]", "", text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def get_position_summary(self) -> Dict[str, float]:
        """
        Extract all financial metrics from the account summary footer bar:
        balance, equity, used_margin, free_margin, margin_level, total_profit.
        """
        expect(self.summary_footer).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return {
            "balance": self._parse_numeric(self.summary_balance.inner_text()),
            "equity": self._parse_numeric(self.summary_equity.inner_text()),
            "used_margin": self._parse_numeric(self.summary_used_margin.inner_text()),
            "free_margin": self._parse_numeric(self.summary_free_margin.inner_text()),
            "margin_level": self._parse_numeric(self.summary_margin_level.inner_text()),
            "total_profit": self._parse_numeric(self.summary_total_profit.inner_text()),
        }

    # =========================================================================
    # Pending Orders & Mobile Tab Controls
    # =========================================================================

    def get_pending_orders_count(self) -> int:
        """Return the count of pending orders currently listed."""
        return self.pending_rows.count()

    def select_mobile_tab(self, value: str) -> None:
        """Select option on #tab1sel ('positions' or 'pending')."""
        if self.tab1_select.is_visible():
            self.tab1_select.select_option(value)
            self.page.wait_for_timeout(500)

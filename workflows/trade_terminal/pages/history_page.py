"""
Trade Terminal History Page Object.
Encapsulates all elements and user interactions on the standalone/tab History page:
Page container: div.page[data-page="history"] / #tab-1 > div.row.tab2content.order-history
Selector: document.querySelector("#tab-1 > div.row.tab2content.order-history")
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

logger = get_logger("history_page")
TIMEOUT_DEFAULT = 15000


class HistoryPage(BasePage):
    """
    Page Object representing the Trade Terminal History page at:
    document.querySelector("#tab-1 > div.row.tab2content.order-history")
    div.page[data-page="history"]
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Navigation & Container
        self.history_nav_icon: Locator = page.locator(
            ".leftlist .lefticons[data-tooltip='History'], .leftlist .lefticons[data-nav='history'], .lefticons[data-tooltip='History']"
        ).first
        self.history_page_container: Locator = page.locator("div.page[data-page='history']")
        self.history_tab_container: Locator = page.locator(
            "#tab-1 > div.row.tab2content.order-history, #tab-1 .order-history, .order-history"
        )
        self.page_heading: Locator = self.history_tab_container.locator("h3.title-custom, h3").first

        # 2. Filter Box & Export Controls
        self.filter_box: Locator = self.history_tab_container.locator(".dropdown.filter-box, .filter-box").first
        self.export_button: Locator = self.filter_box.locator("#exportBtn")
        self.dropdown_toggle: Locator = self.filter_box.locator("button.dropdown-toggle[data-toggle='dropdown'], button.dropdown-toggle")
        self.dropdown_menu: Locator = self.filter_box.locator("ul.dropdown-menu")
        self.filter_items: Locator = self.dropdown_menu.locator("li.filter_list")

        # 3. Custom Filter Modal (opens when 'custom' duration is selected)
        self.custom_filter_modal: Locator = page.locator(".modal-content:has(#fromDate)")
        self.custom_modal_title: Locator = self.custom_filter_modal.locator("h4.modal-title, h4.cus-modal-head")
        self.custom_modal_from_date: Locator = self.custom_filter_modal.locator("#fromDate")
        self.custom_modal_to_date: Locator = self.custom_filter_modal.locator("#toDate")
        self.custom_modal_from_label: Locator = self.custom_filter_modal.locator("label[for='accno'], label:has-text('From Date')")
        self.custom_modal_to_label: Locator = self.custom_filter_modal.locator("label[for='ifsc'], label:has-text('To Date')")
        self.custom_modal_submit: Locator = self.custom_filter_modal.locator("button.historyOrderSubmit")
        self.custom_modal_close_btn: Locator = self.custom_filter_modal.locator("button.historyOrderModalClose").first
        self.custom_modal_footer_close: Locator = self.custom_filter_modal.locator("button.btn-danger.historyOrderModalClose")

        # 3. Order History Table
        self.table_responsive: Locator = self.history_tab_container.locator(".table-responsive").first
        self.history_table: Locator = self.history_tab_container.locator("table.table-flush, table.table-striped").first
        self.history_headers: Locator = self.history_table.locator("thead th, tbody.tablecontent2 tr:first-child th, th")
        self.history_tbody: Locator = self.history_table.locator("tbody.tablecontent2, tbody").first
        self.history_rows: Locator = self.history_tbody.locator("tr[data-id], tr:not(:has(th))")

        # 4. Bottom Statistics & Calculation Bar
        self.statics_bar: Locator = page.locator(".cus-statics-pad, .history-statics").first
        self.stat_balance: Locator = self.statics_bar.locator("#total_balance").first
        self.stat_deposit: Locator = self.statics_bar.locator("#total_deposit").first
        self.stat_withdraw: Locator = self.statics_bar.locator("#total_withdraw").first
        self.stat_commission: Locator = self.statics_bar.locator("#totalbrokerage").first
        self.stat_swap: Locator = self.statics_bar.locator("#tswap").first
        self.stat_profit: Locator = self.statics_bar.locator("#totalprofit").first

    # =========================================================================
    # Navigation & Modal Guards
    # =========================================================================

    def navigate_to_history_page(self, url: Optional[str] = None) -> None:
        """
        Navigate to the dashboard and activate the History page
        via the left navigation bar icon (.lefticons[data-tooltip='History']).
        """
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()

        if not self.is_history_page_active():
            logger.info("Activating History page via left sidebar...")
            expect(self.history_nav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.history_nav_icon.click()
            self.page.wait_for_timeout(1000)

        expect(self.history_tab_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.dismiss_disclaimer_if_present()

    def is_history_page_active(self) -> bool:
        """Return True if History container is visible and active."""
        if not self.history_tab_container.is_visible():
            return False
        classes = self.history_page_container.get_attribute("class") or ""
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
    # Header & Title
    # =========================================================================

    def get_history_count_from_title(self) -> int:
        """Extract the numeric count N from 'Order History (N)' in the page heading."""
        expect(self.page_heading).to_be_visible(timeout=TIMEOUT_DEFAULT)
        text = self.page_heading.inner_text().strip()
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else 0

    # =========================================================================
    # Filter Dropdown & Export Button Actions
    # =========================================================================

    def get_filter_options(self) -> List[Dict[str, Any]]:
        """
        Return the list of all available filter durations and their active status:
        [{text: 'Today', duration: '1d', active: False}, ...]
        """
        return self.page.evaluate("""() => {
            const items = document.querySelectorAll("#tab-1 .filter-box ul.dropdown-menu li.filter_list, .filter-box ul.dropdown-menu li.filter_list");
            return Array.from(items).map(li => ({
                text: li.innerText.trim(),
                duration: li.getAttribute("data-duration") || "",
                active: li.classList.contains("active"),
            }));
        }""")

    def get_active_filter(self) -> Optional[Dict[str, str]]:
        """Return the currently active filter option."""
        options = self.get_filter_options()
        for opt in options:
            if opt.get("active"):
                return opt
        return None

    def open_filter_dropdown(self) -> None:
        """Open the filter duration dropdown if not already open."""
        expect(self.dropdown_toggle).to_be_visible(timeout=TIMEOUT_DEFAULT)
        if not self.dropdown_menu.is_visible():
            self.dropdown_toggle.click()
            self.page.wait_for_timeout(400)

    def select_filter(self, duration: str) -> None:
        """
        Select a filter duration by data-duration attribute (e.g. '1d', '1w', '3w', '1m', '3m', '1y', 'all', 'custom').
        """
        logger.info(f"Selecting History filter duration: '{duration}'")
        self.open_filter_dropdown()
        item = self.dropdown_menu.locator(f"li.filter_list[data-duration='{duration}']")
        expect(item).to_be_visible(timeout=TIMEOUT_DEFAULT)
        item.click()
        self.page.wait_for_timeout(1000)

    def click_export_button(self) -> None:
        """Click the export excel button (#exportBtn)."""
        logger.info("Clicking History export button (#exportBtn)...")
        expect(self.export_button).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.export_button.click()
        self.page.wait_for_timeout(500)

    # =========================================================================
    # Custom Filter Modal
    # =========================================================================

    def is_custom_modal_open(self) -> bool:
        """Return True if the Custom Filter modal is currently visible."""
        return self.custom_filter_modal.is_visible()

    def open_custom_filter_modal(self) -> None:
        """
        Select the 'custom' filter duration to open the Custom Filter modal,
        then wait until the modal is visible.
        """
        logger.info("Opening Custom Filter modal via 'custom' filter option...")
        self.open_filter_dropdown()
        item = self.dropdown_menu.locator("li.filter_list[data-duration='custom']")
        expect(item).to_be_visible(timeout=TIMEOUT_DEFAULT)
        item.click()
        expect(self.custom_filter_modal).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.page.wait_for_timeout(400)

    def close_custom_filter_modal(self, use_footer_close: bool = False) -> None:
        """
        Close the Custom Filter modal using the header X button (default)
        or the footer 'Close' button when `use_footer_close=True`.
        """
        logger.info(f"Closing Custom Filter modal (footer={use_footer_close})...")
        if use_footer_close:
            expect(self.custom_modal_footer_close).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.custom_modal_footer_close.click()
        else:
            expect(self.custom_modal_close_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.custom_modal_close_btn.click()
        self.page.wait_for_timeout(500)

    def set_custom_date_range(self, from_date: str, to_date: str) -> None:
        """
        Fill the Custom Filter modal date fields.

        Args:
            from_date: ISO date string 'YYYY-MM-DD' for #fromDate input.
            to_date:   ISO date string 'YYYY-MM-DD' for #toDate input.
        """
        logger.info(f"Setting custom date range: from={from_date}, to={to_date}")
        expect(self.custom_modal_from_date).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.custom_modal_from_date.fill(from_date)
        expect(self.custom_modal_to_date).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.custom_modal_to_date.fill(to_date)
        self.page.wait_for_timeout(300)

    def submit_custom_filter(self) -> None:
        """Click the Submit button inside the Custom Filter modal."""
        logger.info("Submitting Custom Filter form...")
        expect(self.custom_modal_submit).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.custom_modal_submit.click()
        self.page.wait_for_timeout(1000)


    def get_history_records(self) -> List[Dict[str, Any]]:
        """
        Extract all closed order records displayed in the History table.
        Returns a list of dicts with:
        id, time, symbol, order, lot, status, type, sl, tp, entry, exit, commission, pnl, swap, close_time, data_id
        """
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll("#tab-1 table.table-flush tbody.tablecontent2 tr, table.table-flush tbody.tablecontent2 tr");
            const records = [];
            for (const row of rows) {
                const ths = row.querySelectorAll("th");
                if (ths.length > 0) continue; // Skip header row if inside tbody

                const tds = row.querySelectorAll("td");
                if (tds.length < 10) continue;

                records.push({
                    id: tds[0] ? tds[0].innerText.trim() : "",
                    time: tds[1] ? tds[1].innerText.trim() : "",
                    symbol: tds[2] ? tds[2].innerText.trim() : "",
                    order: tds[3] ? tds[3].innerText.trim() : "",
                    lot: tds[4] ? parseFloat(tds[4].innerText.trim() || "0") : 0.0,
                    status: tds[5] ? tds[5].innerText.trim() : "",
                    type: tds[6] ? tds[6].innerText.trim() : "",
                    sl: tds[7] ? parseFloat(tds[7].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    tp: tds[8] ? parseFloat(tds[8].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    entry: tds[9] ? parseFloat(tds[9].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    exit: tds[10] ? parseFloat(tds[10].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    commission: tds[11] ? parseFloat(tds[11].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    pnl: tds[12] ? parseFloat(tds[12].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    swap: tds[13] ? parseFloat(tds[13].innerText.trim().replace(/,/g, "") || "0") : 0.0,
                    close_time: tds[14] ? tds[14].innerText.trim() : "",
                    data_id: row.getAttribute("data-id") || (tds[0] ? tds[0].innerText.trim() : ""),
                });
            }
            return records;
        }""")

    def get_last_order_record(self) -> Optional[Dict[str, Any]]:
        """Return the topmost (most recent) order record in history, or None if empty."""
        records = self.get_history_records()
        return records[0] if records else None

    def get_history_record_by_id(self, order_id: str | int) -> Optional[Dict[str, Any]]:
        """Find and return history record dictionary matching `order_id`."""
        id_str = str(order_id).strip()
        records = self.get_history_records()
        for rec in records:
            if rec.get("id") == id_str or rec.get("data_id") == id_str:
                return rec
        return None

    def wait_for_history_record(self, order_id: str | int, timeout: int = 20000) -> Dict[str, Any]:
        """
        Poll until the history table contains an order record matching `order_id`.
        """
        id_str = str(order_id).strip()
        logger.info(f"Waiting for History record with ID: {id_str}...")
        start_time = time.time()
        while time.time() - start_time < (timeout / 1000):
            rec = self.get_history_record_by_id(id_str)
            if rec:
                logger.info(f"Found History record for order {id_str}: {rec}")
                return rec
            self.page.wait_for_timeout(500)

        # In case page needs a tab re-click or scroll to refresh
        self.navigate_to_history_page()
        rec = self.get_history_record_by_id(id_str)
        if rec:
            return rec

        raise TimeoutError(f"History record with ID '{id_str}' did not appear within {timeout}ms")

    # =========================================================================
    # Bottom Calculation & Statistics Bar
    # =========================================================================

    def _parse_numeric(self, text: str) -> float:
        """Strip currency symbols, commas, percent signs and parse as float."""
        cleaned = re.sub(r"[^\d.-]", "", text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def get_bottom_calculations(self) -> Dict[str, float]:
        """
        Extract all financial metrics from the bottom statistics calculation bar:
        balance, deposit, withdraw, commission, swap, profit.
        """
        expect(self.stat_balance).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return {
            "balance": self._parse_numeric(self.stat_balance.inner_text()),
            "deposit": self._parse_numeric(self.stat_deposit.inner_text()) if self.stat_deposit.count() > 0 else 0.0,
            "withdraw": self._parse_numeric(self.stat_withdraw.inner_text()) if self.stat_withdraw.count() > 0 else 0.0,
            "commission": self._parse_numeric(self.stat_commission.inner_text()) if self.stat_commission.count() > 0 else 0.0,
            "swap": self._parse_numeric(self.stat_swap.inner_text()) if self.stat_swap.count() > 0 else 0.0,
            "profit": self._parse_numeric(self.stat_profit.inner_text()) if self.stat_profit.count() > 0 else 0.0,
        }

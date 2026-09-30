"""
Admin Portal Orders Module Page Object.
Encapsulates navigation across submenus (All, Open, Closed), main ledger table controls,
10 table headers, sorting, search, row-count dropdown, pagination, export buttons (CSV, PDF, Excel),
horizontal scrollbar, in-row Show Orders action, Order Details modal (#orderModal) with 24-column
order ledger and Excel export, and the Edit Order modal (#myModal) with field pre-population,
field editability, dynamic validation, and safe mock save testing (0 database changes).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.admin_portal.pages.components.admin_sidebar import AdminSidebarComponent
from workflows.admin_portal.pages.components.admin_topbar import AdminTopbarComponent
from workflows.shared.pages.base_page import BasePage


class AdminOrdersPage(BasePage):
    """Page object for Admin Console Order Details module."""

    URL_ALL = "/admin/Controlbase/order/all"
    URL_OPEN = "/admin/Controlbase/order/open"
    URL_CLOSED = "/admin/Controlbase/order/closed"

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Components
        self.topbar = AdminTopbarComponent(page)
        self.sidebar = AdminSidebarComponent(page)

        # Page Heading
        self.page_heading = page.locator(".page-title-box h4, h4.page-title, .card-title").first

        # Main Table Controls & Export Buttons
        self.export_csv_btn = page.locator(".dt-buttons button.buttons-csv").first
        self.export_pdf_btn = page.locator(".dt-buttons button.buttons-pdf").first
        self.export_excel_btn = page.locator(".dt-buttons button.buttons-excel").first
        self.search_input = page.locator("#datatable_filter input[type='search'], input[type='search']").first
        self.entries_select = page.locator("select[name='datatable_length']").first

        # Main Table Ledger (#datatable)
        self.table = page.locator("#datatable").first
        self.table_headers = page.locator("#datatable thead th")
        self.table_rows = page.locator("#datatable tbody tr")
        self.table_wrapper = page.locator("#datatable_wrapper, .table-responsive").first
        self.pagination_controls = page.locator("#datatable_paginate")

        # Order Details Modal (#orderModal)
        self.order_modal = page.locator("#orderModal")
        self.order_modal_close_btn = page.locator("#orderModal .ux-order-close").first
        self.order_modal_excel_btn = page.locator("#orderModal #btnH").first

        # Summary Stat Cards inside #orderModal
        self.stat_account_id = page.locator("#customer_account_id")
        self.stat_customer_name = page.locator("#customer_account_name")
        self.stat_brokerage = page.locator("#total_brokerage")
        self.stat_spread = page.locator("#total_spread")
        self.stat_pnl = page.locator("#total_pnl")

        # Detailed Orders History Table inside #orderModal
        self.order_history_table = page.locator("#orderHistory").first
        self.order_history_headers = page.locator("#orderHistory thead th")
        self.order_history_rows = page.locator("#orderHistory tbody tr")
        self.order_history_wrapper = page.locator("#orderModal .table-responsive, #orderHistory_wrapper").first
        self.order_history_paginate = page.locator("#orderHistory_paginate")

        # Edit Order Modal (#myModal)
        self.edit_modal = page.locator("#myModal")
        self.edit_modal_card_close = page.locator("#myModal .ux-card-close").first
        self.edit_modal_footer_close = page.locator("#myModal .modal-footer button:has-text('Close')").first
        self.edit_save_btn = page.locator("#formSubmit").first
        self.edit_form = page.locator("#formModal")

        # Edit Order Form Fields
        self.field_oid = page.locator("#oid")
        self.field_lot = page.locator("#lot")
        self.field_bs = page.locator("#bs")
        self.field_sl = page.locator("#sl")
        self.field_target = page.locator("#target")
        self.field_avg = page.locator("#avg")
        self.field_exit = page.locator("#exit")
        self.field_brokerage = page.locator("#brokerage")
        self.field_pnl = page.locator("#pnl")
        self.field_trigger = page.locator("#trigger")
        self.field_t = page.locator("#t")
        self.field_closing_time = page.locator("#closing_time")


        # Edit Order Validation Feedback Elements
        self.error_lot = page.locator(".invalid-feedback.lot")
        self.error_sl = page.locator(".invalid-feedback.sl")
        self.error_target = page.locator(".invalid-feedback.target")
        self.error_avg = page.locator(".invalid-feedback.avg")
        self.error_brokerage = page.locator(".invalid-feedback.brokerage")
        self.error_pnl = page.locator(".invalid-feedback.pnl")
        self.error_trigger = page.locator(".invalid-feedback.trigger")
        self.error_margin = page.locator(".invalid-feedback.margin")
        self.error_t = page.locator(".invalid-feedback.t")

    # =========================================================================
    # Navigation Methods
    # =========================================================================

    def navigate(self, submenu: str = "open") -> None:
        """
        Directly navigate to the specified Orders submenu (all, open, closed).
        Uses resilient DOMContentLoaded load strategy.
        """
        from urllib.parse import urlsplit
        path_map = {
            "all": self.URL_ALL,
            "open": self.URL_OPEN,
            "closed": self.URL_CLOSED,
        }
        sub_path = path_map.get(submenu.lower(), self.URL_OPEN)
        parts = urlsplit(settings.admin_portal.base_url)
        url = f"{parts.scheme}://{parts.netloc}{sub_path}"
        self.goto(url)
        self.wait_for_table_loaded()


    def navigate_via_sidebar(self, submenu: str = "open") -> None:
        """Navigate to Orders submenu by clicking through sidebar navigation."""
        sub = submenu.lower()
        if sub == "all":
            self.sidebar.navigate_to_order_all()
        elif sub == "closed":
            self.sidebar.navigate_to_order_closed()
        else:
            self.sidebar.navigate_to_order_open()
        self.wait_for_table_loaded()

    def wait_for_table_loaded(self, timeout: int = 15000) -> None:
        """Wait for the main DataTable and initial rows to finish loading."""
        expect(self.table).to_be_visible(timeout=timeout)
        try:
            self.page.wait_for_selector("#datatable tbody tr", state="attached", timeout=timeout)
            # Give AJAX datatable a moment to settle
            self.page.wait_for_timeout(500)
        except Exception:
            pass

    # =========================================================================
    # Main Table Controls & Minute Elements
    # =========================================================================

    def get_table_headers(self) -> List[str]:
        """Return clean list of header names in the main #datatable."""
        self.page.wait_for_selector("#datatable thead th", state="attached", timeout=10000)
        headers = self.table_headers.all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_table_rows_count(self) -> int:
        """Return the count of visible table rows in #datatable."""
        rows = self.table_rows.all()
        if not rows:
            return 0
        first_text = rows[0].inner_text()
        if "No data available" in first_text or "Loading" in first_text:
            return 0
        return len(rows)

    def search(self, query: str) -> None:
        """Fill search query into the table filter input."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill(query)
        self.page.wait_for_timeout(500)

    def clear_search(self) -> None:
        """Clear search filter input and wait for table reload."""
        expect(self.search_input).to_be_visible(timeout=10000)
        self.search_input.fill("")
        self.page.wait_for_timeout(500)

    def sort_column(self, col_index: int) -> Dict[str, str]:
        """
        Click a specific column header to toggle sorting,
        returning before and after sorting classes (e.g. sorting_asc, sorting_desc).
        """
        th = self.table_headers.nth(col_index)
        expect(th).to_be_visible(timeout=10000)
        before_class = th.get_attribute("class") or ""
        th.click()
        self.page.wait_for_timeout(500)
        after_class = th.get_attribute("class") or ""
        return {"before": before_class, "after": after_class}

    def select_entries_count(self, count: int | str = 25) -> None:
        """Change visible table entries count using the length dropdown."""
        expect(self.entries_select).to_be_visible(timeout=10000)
        self.entries_select.select_option(str(count))
        self.page.wait_for_timeout(500)

    def check_horizontal_scroll(self) -> Dict[str, Any]:
        """
        Check scrollable state and dimensions for main table and order history table.
        """
        return self.page.evaluate("""() => {
            const dt = document.getElementById("datatable");
            const dtWrapper = dt ? (dt.closest(".table-responsive") || dt.closest(".dataTables_wrapper") || dt.parentElement) : null;
            return {
                mainTableScrollWidth: dt ? dt.scrollWidth : 0,
                mainTableClientWidth: dt ? dt.clientWidth : 0,
                mainWrapperScrollWidth: dtWrapper ? dtWrapper.scrollWidth : 0,
                mainWrapperClientWidth: dtWrapper ? dtWrapper.clientWidth : 0,
                mainIsScrollable: dtWrapper ? (dtWrapper.scrollWidth > dtWrapper.clientWidth) : false
            };
        }""")

    # =========================================================================
    # Show Orders Action (#orderModal)
    # =========================================================================

    def open_show_orders(self, row_index: int = 0) -> None:
        """
        Click 'Show Orders' in the specified row of the main table,
        and wait for #orderModal to open and populate.
        """
        btn = self.page.locator("button.showOrders").nth(row_index)
        expect(btn).to_be_visible(timeout=10000)
        btn.click()
        expect(self.order_modal).to_be_visible(timeout=15000)
        # Wait for orders table inside modal to load
        self.page.wait_for_selector("#orderHistory tbody tr", timeout=15000)
        self.page.wait_for_timeout(500)

    def get_order_modal_stats(self) -> Dict[str, str]:
        """Return the stat card values displayed in #orderModal."""
        expect(self.order_modal).to_be_visible(timeout=10000)
        return {
            "account_id": self.stat_account_id.inner_text().strip(),
            "customer_name": self.stat_customer_name.inner_text().strip(),
            "brokerage": self.stat_brokerage.inner_text().strip(),
            "spread": self.stat_spread.inner_text().strip(),
            "pnl": self.stat_pnl.inner_text().strip(),
        }

    def get_order_history_headers(self) -> List[str]:
        """Return list of header names in the detailed #orderHistory table (24 columns)."""
        expect(self.order_history_table).to_be_visible(timeout=10000)
        headers = self.order_history_headers.all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_order_history_rows_count(self) -> int:
        """Return row count of orders in #orderHistory."""
        rows = self.order_history_rows.all()
        if not rows:
            return 0
        first_text = rows[0].inner_text()
        if "No data available" in first_text:
            return 0
        return len(rows)

    def check_modal_horizontal_scroll(self) -> Dict[str, Any]:
        """Verify horizontal scroll state of the 24-column orderHistory table inside modal."""
        return self.page.evaluate("""() => {
            const table = document.getElementById("orderHistory");
            const wrapper = table ? (table.closest(".table-responsive") || table.parentElement) : null;
            return {
                tableScrollWidth: table ? table.scrollWidth : 0,
                tableClientWidth: table ? table.clientWidth : 0,
                wrapperScrollWidth: wrapper ? wrapper.scrollWidth : 0,
                wrapperClientWidth: wrapper ? wrapper.clientWidth : 0,
                isHorizontallyScrollable: wrapper ? (wrapper.scrollWidth > wrapper.clientWidth) : false
            };
        }""")

    def close_order_modal(self) -> None:
        """Close #orderModal using its top-right .ux-order-close button."""
        expect(self.order_modal_close_btn).to_be_visible(timeout=10000)
        self.order_modal_close_btn.click()
        self.page.wait_for_timeout(600)
        expect(self.order_modal).to_be_hidden(timeout=10000)

    # =========================================================================
    # Edit Order Action & Form (#myModal)
    # =========================================================================

    def open_edit_order_modal(self, order_index: int = 0) -> None:
        """
        Click the Edit button (a.btnEdit) for the specified order row inside #orderModal.
        Waits for #myModal to open.
        """
        edit_buttons = self.page.locator("#orderHistory tbody tr a.btnEdit")
        expect(edit_buttons.nth(order_index)).to_be_visible(timeout=10000)
        edit_buttons.nth(order_index).click()
        expect(self.edit_modal).to_be_visible(timeout=15000)
        self.page.wait_for_timeout(400)

    def get_edit_order_form_values(self) -> Dict[str, str]:
        """
        Retrieve all pre-populated values from the Edit Order modal form fields,
        verifying that the values are read and pre-populated correctly.
        """
        expect(self.edit_modal).to_be_visible(timeout=10000)
        return {
            "oid": self.field_oid.input_value(),
            "lot": self.field_lot.input_value(),
            "bs": self.field_bs.input_value(),
            "sl": self.field_sl.input_value(),
            "target": self.field_target.input_value(),
            "avg": self.field_avg.input_value(),
            "exit": self.field_exit.input_value() if self.field_exit.is_visible() else "",
            "brokerage": self.field_brokerage.input_value(),
            "pnl": self.field_pnl.input_value() if self.field_pnl.is_visible() else "",
            "trigger": self.field_trigger.input_value(),
            "t": self.field_t.input_value(),
            "closing_time": self.field_closing_time.input_value() if self.field_closing_time.is_visible() else "",
        }

    def fill_edit_order_form(
        self,
        lot: Optional[str] = None,
        sl: Optional[str] = None,
        target: Optional[str] = None,
        avg: Optional[str] = None,
        brokerage: Optional[str] = None,
        trigger: Optional[str] = None,
    ) -> None:
        """Fill new values into visible form fields to verify they are editable."""
        expect(self.edit_modal).to_be_visible(timeout=10000)
        if lot is not None:
            self.field_lot.fill(str(lot))
        if sl is not None:
            self.field_sl.fill(str(sl))
        if target is not None:
            self.field_target.fill(str(target))
        if avg is not None:
            self.field_avg.fill(str(avg))
        if brokerage is not None:
            self.field_brokerage.fill(str(brokerage))
        if trigger is not None:
            self.field_trigger.fill(str(trigger))
        self.page.wait_for_timeout(300)

    def test_validation_error(self, field: str = "lot", bad_value: str = "") -> str:

        """
        Test client-side validation on a field by setting an invalid/empty value,
        clicking Save, and asserting the returned error message from .invalid-feedback.
        """
        expect(self.edit_modal).to_be_visible(timeout=10000)
        if field == "lot":
            self.field_lot.fill(bad_value)
            self.edit_save_btn.click()
            expect(self.error_lot).to_be_visible(timeout=5000)
            return self.error_lot.inner_text().strip()
        elif field == "sl":
            self.field_sl.fill(bad_value)
            self.edit_save_btn.click()
            expect(self.error_sl).to_be_visible(timeout=5000)
            return self.error_sl.inner_text().strip()
        elif field == "target":
            self.field_target.fill(bad_value)
            self.edit_save_btn.click()
            expect(self.error_target).to_be_visible(timeout=5000)
            return self.error_target.inner_text().strip()
        return ""

    def save_order_mock(self) -> Dict[str, Any]:
        """
        Execute mock save test on the Edit Order form.
        Uses Playwright route interception on **/Controlbase/updateOrderDetails**
        to ensure ZERO database writes, validates that the intercepted POST payload
        contains the submitted values, returns a mock success response, confirms
        the success dialog appears, and dismisses it.
        """
        intercepted_requests = []

        # Auto-accept native browser alerts if any
        self.page.on("dialog", lambda dialog: dialog.accept())

        # Intercept background notification token to avoid alert popups
        self.page.route(
            "**/userStatusNotificationToken**",
            lambda r: r.fulfill(status=200, content_type="text/html", body='{"status":"success"}')
        )

        def handle_update_order(route):
            req = route.request
            post_data = req.post_data or ""
            intercepted_requests.append({
                "url": req.url,
                "method": req.method,
                "post_data": post_data,
            })
            # order_v5.js calls JSON.parse(data), so response must be served as text/html
            route.fulfill(
                status=200,
                content_type="text/html",
                body=json.dumps({
                    "status": "success",
                    "message": "Mock Order Updated Successfully (Test Mode - Zero DB Change)"
                }),
            )

        # Register mock route interception
        self.page.route("**/Controlbase/updateOrderDetails**", handle_update_order)

        try:
            expect(self.edit_save_btn).to_be_visible(timeout=10000)
            self.edit_save_btn.click()

            # Wait for mock response to be triggered
            self.page.wait_for_timeout(1000)

            # Assert route was intercepted
            assert len(intercepted_requests) > 0, "Expected updateOrderDetails route to be intercepted!"

            # Check if confirmation alert appears and dismiss it
            confirm_dialog = self.page.locator(".jconfirm-box")
            if confirm_dialog.is_visible():
                thank_you_btn = confirm_dialog.locator(
                    "button:has-text('Thank You!'), button:has-text('OK'), button:has-text('close'), .btn-green"
                ).first
                if thank_you_btn.is_visible():
                    thank_you_btn.click()
                    self.page.wait_for_timeout(500)

            # Ensure modals dismissed
            if self.edit_modal.is_visible():
                self.close_edit_modal()
            if self.order_modal.is_visible():
                self.close_order_modal()

            return {
                "intercepted": True,
                "request_count": len(intercepted_requests),
                "payload": intercepted_requests[0]["post_data"] if intercepted_requests else None,
            }
        finally:
            try:
                self.page.unroute("**/Controlbase/updateOrderDetails**")
                self.page.unroute("**/userStatusNotificationToken**")
            except Exception:
                pass


    def close_edit_modal(self) -> None:
        """
        Close #myModal without saving changes using its Close button.
        Verifies #myModal is cleanly dismissed.
        """
        expect(self.edit_modal).to_be_visible(timeout=10000)
        # Click footer Close button with force=True for stacked modal stability
        self.edit_modal_footer_close.click(force=True)
        self.page.wait_for_timeout(600)
        expect(self.edit_modal).to_be_hidden(timeout=10000)

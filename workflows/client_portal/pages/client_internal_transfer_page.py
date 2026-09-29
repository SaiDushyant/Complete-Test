"""
Client Portal Internal Transfer Page Object.
Comprehensive encapsulation of all minute controls:
- Universal header integration and page title ('Internal Transfer')
- Transfer Details Form:
  * Source account / wallet selector (WITHDRAW FROM / SOURCE)
  * Destination account / wallet selector
  * Transfer amount input
  * Optional reference / memo input
  * Cancel and Review Transfer action buttons
- Review Internal Transfer Modal Dialog:
  * Displays transferring amount, source, destination, and memo
  * 'Edit Details' button to return and modify form
  * 'Close' button to dismiss modal
  * 'EXECUTE TRANSFER' button
- Recent Transfers Transaction Ledger:
  * 4 columns (DATE, DETAILS, AMOUNT, STATUS)
  * Rows per page dropdown (10, 25, 50, 100)
  * Multi-page pagination controls (Previous / Next)
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import Dict, List
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_internal_transfer_page")


class ClientInternalTransferPage(BasePage):
    """Page object for Client Portal Internal Transfer workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Headings & Subtitles
        self.main_heading = page.locator("main h1").filter(has_text=re.compile(r"Internal\s*Transfer", re.I))
        self.subtitle = page.locator("main p").filter(has_text=re.compile(r"Move\s*funds\s*securely", re.I))

        # Transfer Details Form
        self.transfer_details_heading = page.locator("main h3").filter(has_text=re.compile(r"Transfer\s*Details", re.I))
        self.source_select = page.locator("main select").nth(0)
        self.destination_select = page.locator("main select").nth(1)
        self.amount_input = page.locator("main input").nth(0)
        self.memo_input = page.locator("main input").nth(1)

        self.cancel_button = page.locator("main button").filter(has_text="Cancel").first
        self.review_transfer_button = page.locator("main button").filter(has_text=re.compile(r"Review\s*Transfer", re.I)).first
        self.validation_error_message = page.locator("main").filter(
            has_text=re.compile(r"Please\s*enter\s*a\s*valid\s*transfer\s*amount", re.I)
        )


        # Review Internal Transfer Modal Dialog
        self.review_modal = page.locator("div.fixed.inset-0.z-50").filter(
            has_text=re.compile(r"Review\s*Internal\s*Transfer", re.I)
        )
        self.modal_amount = self.review_modal.locator("div").filter(has_text="TRANSFERRING AMOUNT")
        self.modal_source = self.review_modal.locator("div").filter(has_text="SOURCE")
        self.modal_destination = self.review_modal.locator("div").filter(has_text="DESTINATION")
        self.modal_close_btn = self.review_modal.locator("button").filter(has_text="Close").first
        self.modal_edit_btn = self.review_modal.locator("button").filter(has_text=re.compile(r"Edit\s*Details", re.I)).first
        self.modal_execute_btn = self.review_modal.locator("button").filter(has_text=re.compile(r"EXECUTE\s*TRANSFER", re.I)).first

        # Recent Transfers Transaction Ledger
        self.recent_transfers_heading = page.locator("main h3").filter(has_text=re.compile(r"Recent\s*Transfers", re.I))
        self.history_rows_select = page.locator("main select").nth(2)
        self.table = page.locator("main table")
        self.table_headers = page.locator("main table th")
        self.table_rows = page.locator("main table tbody tr")
        self.prev_page_button = page.locator("main button").filter(has_text="Previous").first
        self.next_page_button = page.locator("main button").filter(has_text="Next").first
        self.pagination_summary = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Showing\s+\d+-\d+\s+of\s+\d+\s+transfers", re.I)
        ).first
        self.page_indicator = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Page\s+\d+\s+/\s+\d+", re.I)
        ).first

    def navigate(self) -> None:
        """Navigate to Internal Transfer view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_internal_transfer()
        expect(self.header.title_heading.first).to_have_text("Internal Transfer", timeout=15000)
        expect(self.main_heading.first).to_be_visible(timeout=10000)
        expect(self.transfer_details_heading.first).to_be_visible(timeout=10000)
        expect(self.source_select.locator("option").first).to_be_attached(timeout=10000)

    def select_source(self, identifier: str | None = None) -> None:
        """Select source account or wallet."""
        expect(self.source_select.locator("option").first).to_be_attached(timeout=10000)
        options = self.source_select.locator("option").all()
        matched_val = None
        target = identifier or settings.client_portal.username
        if target:
            for opt in options:
                opt_text = opt.inner_text().lower()
                opt_val = (opt.get_attribute("value") or "").lower()
                if target.lower() in opt_text or target.lower() == opt_val:
                    matched_val = opt.get_attribute("value")
                    break
        if matched_val:
            self.source_select.select_option(matched_val)
        else:
            if len(options) > 1:
                self.source_select.select_option(index=len(options) - 1)
            else:
                self.source_select.select_option(index=1)
        self.page.wait_for_timeout(300)

    def select_destination(self, identifier: str | None = None) -> None:
        """Select destination account or wallet."""
        expect(self.destination_select.locator("option").first).to_be_attached(timeout=10000)
        options = self.destination_select.locator("option").all()
        matched_val = None
        if identifier:
            for opt in options:
                opt_text = opt.inner_text().lower()
                opt_val = (opt.get_attribute("value") or "").lower()
                if identifier.lower() in opt_text or identifier.lower() == opt_val:
                    matched_val = opt.get_attribute("value")
                    break
        if matched_val:
            self.destination_select.select_option(matched_val)
        else:
            if len(options) > 2:
                self.destination_select.select_option(index=2)
            elif len(options) > 1:
                self.destination_select.select_option(index=1)
        self.page.wait_for_timeout(300)

    def enter_amount(self, amount: str) -> None:
        """Fill in transfer amount."""
        self.amount_input.fill(amount)
        self.page.wait_for_timeout(200)

    def enter_memo(self, memo: str) -> None:
        """Fill in optional reference memo."""
        self.memo_input.fill(memo)
        self.page.wait_for_timeout(200)

    def is_review_transfer_enabled(self) -> bool:
        """Check if Review Transfer button is enabled."""
        return self.review_transfer_button.is_enabled()

    def click_review_transfer(self) -> None:
        """Click Review Transfer button and wait for confirmation modal."""
        expect(self.review_transfer_button).to_be_enabled(timeout=5000)
        self.review_transfer_button.click()
        expect(self.review_modal.first).to_be_visible(timeout=5000)

    def submit_review_transfer_without_waiting_modal(self) -> None:
        """Click Review Transfer button directly without asserting modal visibility."""
        self.review_transfer_button.click()


    def close_review_modal(self) -> None:
        """Dismiss review modal via Close button."""
        if self.review_modal.is_visible():
            expect(self.modal_close_btn).to_be_visible(timeout=5000)
            self.modal_close_btn.click()
            self.page.wait_for_timeout(500)

    def click_edit_details_modal(self) -> None:
        """Click Edit Details in modal to return to the form."""
        if self.review_modal.is_visible():
            expect(self.modal_edit_btn).to_be_visible(timeout=5000)
            self.modal_edit_btn.click()
            self.page.wait_for_timeout(500)

    def execute_transfer_modal(self) -> None:
        """Click 'EXECUTE TRANSFER' in review modal and wait for completion."""
        expect(self.modal_execute_btn).to_be_visible(timeout=5000)
        self.modal_execute_btn.click()
        expect(self.review_modal.first).not_to_be_visible(timeout=10000)
        self.page.wait_for_timeout(1000)

    def get_source_options(self) -> List[str]:
        """Return available source options."""
        expect(self.source_select.locator("option").first).to_be_attached(timeout=10000)
        return [opt.inner_text().strip() for opt in self.source_select.locator("option").all()]

    def get_destination_options(self) -> List[str]:
        """Return available destination options."""
        expect(self.destination_select.locator("option").first).to_be_attached(timeout=10000)
        return [opt.inner_text().strip() for opt in self.destination_select.locator("option").all()]

    def get_table_headers(self) -> List[str]:
        """Return table column headers."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def get_history_row_count(self) -> int:
        """Return count of history records in the table."""
        return self.table_rows.count()

    def get_first_history_row_data(self) -> Dict[str, str]:
        """Extract data from first recent transfer row."""
        if self.table_rows.count() == 0:
            return {}
        row = self.table_rows.first
        expect(row.locator("td").nth(2)).not_to_have_text("", timeout=10000)
        cells = row.locator("td").all()
        return {
            "date": cells[0].inner_text().strip() if len(cells) > 0 else "",
            "details": cells[1].inner_text().strip() if len(cells) > 1 else "",
            "amount": cells[2].inner_text().strip() if len(cells) > 2 else "",
            "status": cells[3].inner_text().strip() if len(cells) > 3 else "",
        }

    def select_history_rows_per_page(self, rows: str) -> None:
        """Select rows count per page (10, 25, 50, 100)."""
        self.history_rows_select.select_option(rows)
        self.page.wait_for_timeout(300)

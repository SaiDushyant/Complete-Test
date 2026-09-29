"""
Client Portal Deposit & Funding Page Object.
Comprehensive encapsulation of all minute controls:
- Universal header integration and page title
- Funding rail payment cards (Bank Transfer, BITCOIN, USDT TRC20, Crypto Gateway, etc.)
- Deposit Request Form:
  * Destination account / wallet selector
  * Mode of payment selector
  * Deposit amount input with minimum threshold validation
  * Proof of payment file uploader (drag & drop / file input)
  * Submit button enabling condition lifecycle
- Deposit History Transaction Ledger:
  * 5 columns (DATE, METHOD, AMOUNT, STATUS, DETAIL)
  * Rows per page dropdown (10, 25, 50, 100)
  * Refresh button
  * Pagination navigation (Previous / Next)
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_deposit_page")


class ClientDepositPage(BasePage):
    """Page object for Client Portal Deposit & Funding workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Page Headings
        self.main_heading = page.locator("main h1").filter(has_text=re.compile(r"Deposit\s*Funds", re.I))
        self.refresh_top_button = page.locator("main button").filter(has_text="Refresh").first

        # =====================================================================
        # Funding Rail Cards (Top payment method selector buttons)
        # =====================================================================
        self.rail_cards = page.locator("main button").filter(has_text="Minimum deposit")
        self.bank_transfer_card = page.locator("main button").filter(has_text=re.compile(r"Bank\s*Transfer", re.I)).first
        self.bitcoin_card = page.locator("main button").filter(has_text=re.compile(r"BITCOIN", re.I)).first
        self.crypto_gateway_card = page.locator("main button").filter(has_text=re.compile(r"Crypto\s*Payment\s*Gateway", re.I)).first
        self.usdt_trc20_card = page.locator("main button").filter(has_text=re.compile(r"USDT\s*TRC20", re.I)).first

        # =====================================================================
        # Deposit Request Form
        # =====================================================================
        self.deposit_request_heading = page.locator("main h3").filter(has_text=re.compile(r"Deposit\s*Request", re.I))
        self.selected_account_summary = page.locator("main div").filter(has_text="SELECTED ACCOUNT").first

        # Form Selects & Inputs
        self.destination_account_select = page.locator("main select").nth(0)
        self.payment_method_select = page.locator("main select").nth(1)
        self.amount_input = page.locator("main input[type='number']").first
        self.proof_upload_input = page.locator("main input[type='file']").first
        self.proof_upload_label = page.locator("main div").filter(has_text="Drop payment proof").first
        self.submit_button = page.locator("main button").filter(has_text=re.compile(r"Submit\s*Deposit\s*Request", re.I)).first
        self.success_toast = page.locator("div").filter(
            has_text=re.compile(r"Payment\s*Deposit\s*Request\s*Received", re.I)
        )

        # =====================================================================
        # Deposit History Transaction Ledger
        # =====================================================================
        self.history_heading = page.locator("main h3").filter(has_text=re.compile(r"Deposit\s*History", re.I))
        self.history_rows_select = page.locator("main select").nth(2)
        self.table = page.locator("main table")
        self.table_headers = page.locator("main table th")
        self.table_rows = page.locator("main table tbody tr")
        self.prev_page_button = page.locator("main button").filter(has_text="Previous").first
        self.next_page_button = page.locator("main button").filter(has_text="Next").first
        self.pagination_summary = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Showing\s+\d+-\d+\s+of\s+\d+\s+records", re.I)
        ).first
        self.page_indicator = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Page\s+\d+\s+/\s+\d+", re.I)
        ).first
        self.minimum_deposit_hint = page.locator("main div").filter(
            has_text=re.compile(r"Minimum\s*deposit:\s*\$", re.I)
        )
        self.visible_modal_dialogs = page.locator("div[role='dialog']:visible, .modal:visible")


    def navigate(self) -> None:
        """Navigate to Deposit view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_deposit()
        expect(self.header.title_heading.first).to_have_text("Deposit", timeout=15000)
        expect(self.main_heading.first).to_be_visible(timeout=10000)
        expect(self.rail_cards.first).to_be_visible(timeout=15000)

    def is_deposit_displayed(self) -> bool:
        """Verify presence of deposit form and elements."""
        return self.main_heading.first.is_visible() and self.deposit_request_heading.first.is_visible()

    def get_funding_rails_info(self) -> List[Dict[str, str]]:
        """Return structured list of all available funding rail cards with minimums."""
        rails: List[Dict[str, str]] = []
        for card in self.rail_cards.all():
            text = card.inner_text().strip().replace("\n", " ")
            match = re.search(r"Minimum deposit:\s*(\$[\d\.,]+)", text, re.I)
            min_deposit = match.group(1) if match else ""
            rails.append({
                "full_text": text,
                "minimum_deposit": min_deposit,
            })
        return rails

    def select_funding_rail(self, name: str) -> None:
        """Click a payment method rail card by name."""
        card = self.rail_cards.filter(has_text=re.compile(name, re.I)).first
        expect(card).to_be_visible(timeout=10000)
        card.click()
        self.page.wait_for_timeout(300)

    def select_destination_account(self, account_identifier: str) -> None:
        """Select destination account or wallet from dropdown."""
        # Find matching option by text
        options = self.destination_account_select.locator("option").all()
        matched_value = None
        for opt in options:
            if account_identifier in opt.inner_text():
                matched_value = opt.get_attribute("value")
                break
        if matched_value:
            self.destination_account_select.select_option(matched_value)
        else:
            # Fallback to index 1 or 2 if not empty
            self.destination_account_select.select_option(index=1)
        self.page.wait_for_timeout(300)

    def select_payment_method(self, method_name: str) -> None:
        """Select payment method from dropdown."""
        options = self.payment_method_select.locator("option").all()
        matched_value = None
        for opt in options:
            if method_name.lower() in opt.inner_text().lower():
                matched_value = opt.get_attribute("value")
                break
        if matched_value:
            self.payment_method_select.select_option(matched_value)
        self.page.wait_for_timeout(300)

    def enter_deposit_amount(self, amount: str) -> None:
        """Fill in deposit amount input field."""
        self.amount_input.fill(amount)
        self.page.wait_for_timeout(200)

    def upload_payment_proof(self, file_path: str) -> None:
        """Upload receipt/proof file."""
        self.proof_upload_input.set_input_files(file_path)
        self.page.wait_for_timeout(300)

    def is_submit_enabled(self) -> bool:
        """Check if Submit Deposit Request button is currently enabled."""
        return self.submit_button.is_enabled()

    def submit_deposit(self) -> None:
        """Click Submit Deposit Request button."""
        expect(self.submit_button).to_be_enabled(timeout=5000)
        self.submit_button.click()
        self.page.wait_for_timeout(1000)

    def get_table_headers(self) -> List[str]:
        """Return list of table header names."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def get_history_row_count(self) -> int:
        """Return number of displayed rows in the deposit history ledger."""
        return self.table_rows.count()

    def get_first_history_row_data(self) -> Dict[str, str]:
        """Extract data from first deposit history transaction row."""
        if self.table_rows.count() == 0:
            return {}
        cells = self.table_rows.first.locator("td").all()
        return {
            "date": cells[0].inner_text().strip() if len(cells) > 0 else "",
            "method": cells[1].inner_text().strip() if len(cells) > 1 else "",
            "amount": cells[2].inner_text().strip() if len(cells) > 2 else "",
            "status": cells[3].inner_text().strip() if len(cells) > 3 else "",
            "detail": cells[4].inner_text().strip() if len(cells) > 4 else "",
        }

    def select_history_rows_per_page(self, rows: str) -> None:
        """Select rows count per page (10, 25, 50, 100)."""
        self.history_rows_select.select_option(rows)
        self.page.wait_for_timeout(300)

    def get_payment_method_options(self) -> List[str]:
        """Return all payment method option names from the select dropdown."""
        return [opt.inner_text().strip() for opt in self.payment_method_select.locator("option").all()]

    def click_next_page(self) -> None:
        """Click next page pagination button."""
        expect(self.next_page_button).to_be_enabled(timeout=5000)
        self.next_page_button.click()
        self.page.wait_for_timeout(500)

    def click_prev_page(self) -> None:
        """Click previous page pagination button."""
        expect(self.prev_page_button).to_be_enabled(timeout=5000)
        self.prev_page_button.click()
        self.page.wait_for_timeout(500)

    def get_pagination_summary_text(self) -> str:
        """Return pagination summary text (e.g. 'Showing 1-25 of 33 records')."""
        return self.pagination_summary.inner_text().strip()

    def get_page_indicator_text(self) -> str:
        """Return page indicator text (e.g. 'Page 1 / 2')."""
        return self.page_indicator.inner_text().strip()

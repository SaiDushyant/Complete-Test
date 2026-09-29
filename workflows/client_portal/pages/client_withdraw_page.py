"""
Client Portal Withdraw & Payout Page Object.
Comprehensive encapsulation of all minute controls:
- Universal header integration and page title ('Withdraw')
- Bank Payout Details:
  * Bank Name, Account Number, IFSC Code, BIC / SWIFT Code, Branch, Location
- Withdraw Addresses (Crypto & Alternative):
  * USDT TRC20, USDT BEP, UPI payment, SS payment
  * SAVE DETAILS button lifecycle and confirmation toast
- Request Payout Form:
  * Available source summary (FUND, WITHDRAWABLE)
  * Source account / wallet selector (WITHDRAW FROM)
  * Mode of payment selector
  * Withdraw amount input with balance validation
  * REQUEST WITHDRAW button enabling lifecycle
  * Enter Withdraw OTP modal dialog (input, Confirm Withdraw, Close)
- Withdraw History Ledger Table:
  * 5 columns (DATE, METHOD, AMOUNT, STATUS, ADDRESS / DETAIL)
  * Rows per page dropdown (10, 25, 50, 100)
  * Pagination navigation (Previous / Next)
  * Refresh button
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

logger = get_logger("client_withdraw_page")


class ClientWithdrawPage(BasePage):
    """Page object for Client Portal Withdraw & Payout workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Main Headings & Top Controls
        self.main_heading = page.locator("main h1").filter(has_text=re.compile(r"Withdraw\s*Funds", re.I))
        self.subtitle = page.locator("main p").filter(has_text=re.compile(r"Save\s*payout\s*instructions", re.I))
        self.refresh_top_button = page.locator("main button").filter(has_text="Refresh").first

        # =====================================================================
        # Bank Payout Details Section
        # =====================================================================
        self.bank_payout_heading = page.locator("main h3").filter(has_text=re.compile(r"Bank\s*Payout\s*Details", re.I))
        self.bank_name_input = page.locator("main input[placeholder*='Bank Name' i]").first
        self.account_number_input = page.locator("main input[placeholder*='account number' i]").first
        self.ifsc_code_input = page.locator("main input[placeholder*='IFSC' i]").first
        self.swift_code_input = page.locator("main input[placeholder*='SWIFT' i]").first
        self.branch_input = page.locator("main input[placeholder*='Branch' i]").first
        self.location_input = page.locator("main input[placeholder*='Location' i]").first

        # =====================================================================
        # Withdraw Addresses Section (Crypto / Alternative)
        # =====================================================================
        # Withdraw Addresses & Copy Buttons
        self.withdraw_addresses_heading = page.locator("main h3").filter(has_text=re.compile(r"Withdraw\s*Addresses", re.I))
        self.usdt_trc20_input = page.locator("main input[placeholder*='USDT TRC20 address' i]").first
        self.usdt_bep_input = page.locator("main input[placeholder*='USDT BEP address' i]").first
        self.upi_input = page.locator("main input[placeholder*='UPI' i]").first
        self.ss_payment_input = page.locator("main input[placeholder*='SS payment' i]").first

        self.usdt_trc20_copy_button = self.usdt_trc20_input.locator("..").locator("button[title='Copy']").first
        self.usdt_bep_copy_button = self.usdt_bep_input.locator("..").locator("button[title='Copy']").first
        self.upi_copy_button = self.upi_input.locator("..").locator("button[title='Copy']").first
        self.ss_payment_copy_button = self.ss_payment_input.locator("..").locator("button[title='Copy']").first

        self.save_details_button = page.locator("main button").filter(has_text=re.compile(r"SAVE\s*DETAILS", re.I)).first
        self.save_changes_button = self.save_details_button  # Alias for Save Changes
        self.save_success_toast = page.locator("div").filter(
            has_text=re.compile(r"Successfully\s*Saved\s*Payment\s*details", re.I)
        )

        # =====================================================================
        # Request Payout Form
        # =====================================================================
        self.request_payout_heading = page.locator("main h3").filter(has_text=re.compile(r"Request\s*Payout", re.I))
        self.available_source_box = page.locator("main div").filter(has_text="AVAILABLE SOURCE").first
        self.fund_amount_display = page.locator("main div").filter(has_text="FUND").first
        self.withdrawable_amount_display = page.locator("main div").filter(has_text="WITHDRAWABLE").first

        self.withdraw_from_select = page.locator("main select").nth(0)
        self.payment_method_select = page.locator("main select").nth(1)
        self.amount_input = page.locator("main input[type='number']").first
        self.request_withdraw_button = page.locator("main button").filter(
            has_text=re.compile(r"REQUEST\s*WITHDRAW", re.I)
        ).first

        # =====================================================================
        # Enter Withdraw OTP Modal Dialog
        # =====================================================================
        self.otp_modal = page.locator("div.fixed.inset-0.z-50").filter(
            has_text=re.compile(r"Enter\s*Withdraw\s*OTP", re.I)
        )
        self.otp_input = self.otp_modal.locator("input[placeholder*='Enter OTP' i]")
        self.otp_confirm_button = self.otp_modal.locator("button").filter(
            has_text=re.compile(r"Confirm\s*Withdraw", re.I)
        )
        self.otp_close_button = self.otp_modal.locator("button[title='Close']")
        self.otp_sent_toast = page.locator("div").filter(
            has_text=re.compile(r"Successfully\s*OTP\s*sent", re.I)
        )

        # =====================================================================
        # Withdraw History Transaction Ledger
        # =====================================================================
        self.history_heading = page.locator("main h3").filter(has_text=re.compile(r"Withdraw\s*History", re.I))
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

    def navigate(self) -> None:
        """Navigate to Withdraw view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_withdraw()
        expect(self.header.title_heading.first).to_have_text("Withdraw", timeout=15000)
        expect(self.main_heading.first).to_be_visible(timeout=10000)
        expect(self.request_payout_heading.first).to_be_visible(timeout=10000)
        expect(self.payment_method_select.locator("option").first).to_be_attached(timeout=15000)

    def is_withdraw_displayed(self) -> bool:
        """Verify presence of withdraw headings and payout form."""
        return (
            self.main_heading.first.is_visible()
            and self.request_payout_heading.first.is_visible()
            and self.bank_payout_heading.first.is_visible()
        )

    def fill_bank_details(
        self,
        bank_name: str | None = None,
        account_number: str | None = None,
        ifsc_code: str | None = None,
        swift_code: str | None = None,
        branch: str | None = None,
        location: str | None = None,
    ) -> None:
        """Fill editable bank details fields."""
        if bank_name is not None:
            self.bank_name_input.fill(bank_name)
        if account_number is not None:
            self.account_number_input.fill(account_number)
        if ifsc_code is not None:
            self.ifsc_code_input.fill(ifsc_code)
        if swift_code is not None:
            self.swift_code_input.fill(swift_code)
        if branch is not None:
            self.branch_input.fill(branch)
        if location is not None:
            self.location_input.fill(location)
        self.page.wait_for_timeout(200)

    def fill_crypto_addresses(
        self,
        usdt_trc20: str | None = None,
        usdt_bep: str | None = None,
        upi: str | None = None,
        ss_payment: str | None = None,
    ) -> None:
        """Fill crypto / alternative payout addresses."""
        if usdt_trc20 is not None:
            self.usdt_trc20_input.fill(usdt_trc20)
        if usdt_bep is not None:
            self.usdt_bep_input.fill(usdt_bep)
        if upi is not None:
            self.upi_input.fill(upi)
        if ss_payment is not None:
            self.ss_payment_input.fill(ss_payment)
        self.page.wait_for_timeout(200)

    def save_details(self) -> None:
        """Click 'SAVE DETAILS' button and wait for confirmation."""
        expect(self.save_details_button).to_be_visible()
        self.save_details_button.click()
        self.page.wait_for_timeout(1000)

    def select_withdraw_source(self, identifier: str) -> None:
        """Select account or wallet from 'WITHDRAW FROM' dropdown."""
        expect(self.withdraw_from_select.locator("option").first).to_be_attached(timeout=10000)
        options = self.withdraw_from_select.locator("option").all()
        matched_val = None
        for opt in options:
            if identifier.lower() in opt.inner_text().lower():
                matched_val = opt.get_attribute("value")
                break
        if matched_val:
            self.withdraw_from_select.select_option(matched_val)
        else:
            self.withdraw_from_select.select_option(index=1)
        self.page.wait_for_timeout(300)

    def select_payment_method(self, method_name: str) -> None:
        """Select payment method from 'MODE OF PAYMENT' dropdown."""
        expect(self.payment_method_select.locator("option").first).to_be_attached(timeout=10000)
        options = self.payment_method_select.locator("option").all()
        matched_val = None
        for opt in options:
            if method_name.lower().strip() in opt.inner_text().lower().strip():
                matched_val = opt.get_attribute("value")
                break
        if matched_val:
            self.payment_method_select.select_option(matched_val)
        self.page.wait_for_timeout(300)

    def enter_withdraw_amount(self, amount: str) -> None:
        """Fill in withdraw amount input field."""
        self.amount_input.fill(amount)
        self.page.wait_for_timeout(200)

    def is_request_withdraw_enabled(self) -> bool:
        """Check if REQUEST WITHDRAW button is enabled."""
        return self.request_withdraw_button.is_enabled()

    def click_request_withdraw(self) -> None:
        """Click REQUEST WITHDRAW button."""
        expect(self.request_withdraw_button).to_be_enabled(timeout=5000)
        self.request_withdraw_button.click()
        self.page.wait_for_timeout(1000)

    def close_otp_modal(self) -> None:
        """Close the Enter Withdraw OTP modal dialog."""
        if self.otp_modal.is_visible():
            expect(self.otp_close_button).to_be_visible(timeout=5000)
            self.otp_close_button.click()
            self.page.wait_for_timeout(500)

    def get_table_headers(self) -> List[str]:
        """Return list of table header names."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def get_history_row_count(self) -> int:
        """Return count of history records in the table."""
        return self.table_rows.count()

    def get_first_history_row_data(self) -> Dict[str, str]:
        """Extract data from first withdrawal history row."""
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

    def get_source_options(self) -> List[str]:
        """Return available source account/wallet options."""
        expect(self.withdraw_from_select.locator("option").first).to_be_attached(timeout=10000)
        return [opt.inner_text().strip() for opt in self.withdraw_from_select.locator("option").all()]

    def get_payment_method_options(self) -> List[str]:
        """Return available withdrawal mode of payment options."""
        expect(self.payment_method_select.locator("option").first).to_be_attached(timeout=10000)
        return [opt.inner_text().strip() for opt in self.payment_method_select.locator("option").all()]

    def click_copy_button(self, method: str) -> None:
        """Click the copy button for a given withdraw address."""
        btn_map = {
            "usdt_trc20": self.usdt_trc20_copy_button,
            "usdt_bep": self.usdt_bep_copy_button,
            "upi": self.upi_copy_button,
            "ss_payment": self.ss_payment_copy_button,
        }
        key = method.lower().replace(" ", "_").replace("-", "_")
        target_btn = None
        for k, btn in btn_map.items():
            if k in key:
                target_btn = btn
                break
        if not target_btn:
            raise ValueError(f"Unknown address copy method: {method}")
        expect(target_btn).to_be_visible(timeout=5000)
        target_btn.click()
        self.page.wait_for_timeout(300)



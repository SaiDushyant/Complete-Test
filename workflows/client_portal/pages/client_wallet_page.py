"""
Client Portal Wallet Management Page Object.
Comprehensive encapsulation of all minute controls:
- Universal header integration and page title ('Wallet')
- Top Action buttons ('Export Report', 'ACCOUNT TO WALLET')
- Wallet Summary Cards:
  * Client Wallet (Account ID, Available Balance, Status)
  * IB Wallet (Account ID, Available Balance, Status)
  * Consolidated Funds summary (Trading Accounts vs Wallets)
- Wallet Accounts Table (WALLET, BALANCE, STATUS, UPDATED, SHARE)
- Wallet Transfer History Table:
  * 6 columns (DATE, MOVEMENT, WALLET, REFERENCE, AMOUNT, REMARKS / ADDRESS)
  * Rows per page dropdown (10, 25, 50, 100)
  * Pagination navigation (Previous / Next)
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


class ClientWalletPage(BasePage):
    """Page object for Client Portal Wallet Management workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Headings & Subtitle
        self.main_heading = page.locator("main h1").filter(has_text=re.compile(r"Wallet\s*Management", re.I))
        self.subtitle = page.locator("main p").filter(has_text=re.compile(r"Client\s*wallet,\s*IB\s*wallet", re.I))

        # Top Action Buttons
        self.export_report_button = page.locator("main button").filter(has_text=re.compile(r"Export\s*Report", re.I)).first
        self.account_to_wallet_button = page.locator("main button").filter(has_text=re.compile(r"ACCOUNT\s*TO\s*WALLET", re.I)).first

        # Wallet Summary Cards
        self.client_wallet_card = page.locator("main").locator("div").filter(has=page.locator("h2", has_text="Client Wallet")).first
        self.ib_wallet_card = page.locator("main").locator("div").filter(has=page.locator("h2", has_text="IB Wallet")).first
        self.consolidated_funds_card = page.locator("main").locator("div").filter(has_text="CONSOLIDATED FUNDS").last

        # Wallet Accounts Table
        self.accounts_heading = page.locator("main h3").filter(has_text=re.compile(r"Wallet\s*Accounts", re.I))
        self.accounts_table = page.locator("main table").first
        self.accounts_headers = self.accounts_table.locator("th")
        self.accounts_rows = self.accounts_table.locator("tbody tr")

        # Wallet Transfer History Table
        self.history_heading = page.locator("main h3").filter(has_text=re.compile(r"Wallet\s*Transfer\s*History", re.I))
        self.history_rows_select = page.locator("main select").first
        self.history_table = page.locator("main table").nth(1)
        self.history_headers = self.history_table.locator("th")
        self.history_rows = self.history_table.locator("tbody tr")
        self.prev_page_button = page.locator("main button").filter(has_text="Previous").first
        self.next_page_button = page.locator("main button").filter(has_text="Next").first
        self.pagination_summary = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Showing\s+\d+-\d+\s+of\s+\d+\s+records", re.I)
        ).first
        self.page_indicator = page.locator("main").locator("p, div, span").filter(
            has_text=re.compile(r"Page\s+\d+\s+/\s+\d+", re.I)
        ).first
        self.internal_transfer_heading = page.locator("main h1").filter(has_text=re.compile(r"Internal\s*Transfer", re.I))
        self.internal_transfer_select = page.locator("main select")


    def navigate(self) -> None:
        """Navigate to Wallet view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_wallet()
        expect(self.header.title_heading.first).to_have_text("Wallet", timeout=15000)
        expect(self.main_heading.first).to_be_visible(timeout=10000)
        expect(self.accounts_heading.first).to_be_visible(timeout=10000)
        expect(self.history_heading.first).to_be_visible(timeout=10000)

    def is_wallet_displayed(self) -> bool:
        """Verify presence of wallet cards and headings."""
        return (
            self.main_heading.first.is_visible()
            and self.client_wallet_card.first.is_visible()
            and self.ib_wallet_card.first.is_visible()
        )

    def get_accounts_table_headers(self) -> List[str]:
        """Return column headers of the Wallet Accounts table."""
        return [th.inner_text().strip() for th in self.accounts_headers.all()]

    def get_history_table_headers(self) -> List[str]:
        """Return column headers of the Wallet Transfer History table."""
        return [th.inner_text().strip() for th in self.history_headers.all()]

    def get_accounts_row_count(self) -> int:
        """Return row count of Wallet Accounts table."""
        return self.accounts_rows.count()

    def get_history_row_count(self) -> int:
        """Return row count of Wallet Transfer History table."""
        return self.history_rows.count()

    def select_history_rows_per_page(self, rows: str) -> None:
        """Select rows count per page (10, 25, 50, 100)."""
        self.history_rows_select.select_option(rows)
        self.page.wait_for_timeout(300)

    def click_account_to_wallet(self) -> None:
        """Click 'ACCOUNT TO WALLET' button which navigates to internal transfer."""
        expect(self.account_to_wallet_button).to_be_visible(timeout=5000)
        self.account_to_wallet_button.click()
        self.page.wait_for_timeout(500)

    def trigger_export_report_download(self):
        """Click 'Export Report' and wait for browser CSV download event."""
        expect(self.export_report_button).to_be_visible(timeout=5000)
        with self.page.expect_download(timeout=10000) as download_info:
            self.export_report_button.click()
        return download_info.value

    def go_to_next_history_page(self) -> None:
        """Click Next page button on history table."""
        expect(self.next_page_button).to_be_enabled(timeout=5000)
        self.next_page_button.click()
        self.page.wait_for_timeout(600)

    def go_to_prev_history_page(self) -> None:
        """Click Previous page button on history table."""
        expect(self.prev_page_button).to_be_enabled(timeout=5000)
        self.prev_page_button.click()
        self.page.wait_for_timeout(600)


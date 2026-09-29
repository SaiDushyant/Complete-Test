"""
Client Portal Refer & Earn Page Object.
Comprehensive encapsulation of all minute controls:
- Referral metrics (Total Earnings, Successful Referrals)
- Unique referral link & dynamic 'Copied!' button feedback
- How It Works 3-step guide
- Interactive Referral Tree View with expand/collapse (+ / -)
- Referred Clients Table (Columns: Client, Account, Ref ID, Mobile, Balance, Activity, IB Earned)
- Rows per page dropdown (10, 25, 50, 100) & Refresh button
- Pagination status and navigation controls
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Any, Dict, List
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage


class ClientReferEarnPage(BasePage):
    """Page object for Client Portal Refer & Earn program."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Page Heading
        self.heading = page.locator("h1, h2, h3").filter(has_text="Referral Program")

        # Metric Summary Cards
        self.total_earnings_card = page.locator("div").filter(has_text="TOTAL EARNINGS").first
        self.successful_referrals_card = page.locator("div").filter(has_text="SUCCESSFUL REFERRALS").first

        # Referral Link Section
        self.unique_link_container = page.locator("div").filter(has_text="Your Unique Link").first
        self.unique_link_input = page.locator("main input[type='text']")
        self.copy_link_button = page.locator("main").get_by_role("button", name="Copy", exact=True)
        self.copied_feedback_button = page.locator("main button").filter(has_text="Copied")

        # How It Works
        self.how_it_works_container = page.locator("div").filter(has_text="How It Works").first

        # =====================================================================
        # Referral Tree View (Hierarchy)
        # =====================================================================
        self.tree_view_heading = page.locator("h2, h3").filter(has_text="Referral Tree View")
        self.direct_referrals_badge = page.locator("span, div").filter(has_text="Direct").first
        self.tree_expand_buttons = page.locator("main button[title='Show referrals'], main button:has-text('+')")
        self.tree_collapse_buttons = page.locator("main button[title='Hide referrals'], main button:has-text('-')")

        # =====================================================================
        # Referred Clients Table & Controls
        # =====================================================================
        self.referred_clients_heading = page.locator("h2, h3").filter(has_text="Referred Clients")
        self.rows_per_page_select = page.locator("main select")
        self.refresh_button = page.locator(
            "main button[title='Refresh referrals'], main button:has-text('Refresh')"
        )
        self.table = page.locator("main table")
        self.table_headers = page.locator("main table th")
        self.table_rows = page.locator("main table tbody tr")

        # Pagination Controls
        self.pagination_summary = page.locator("main div, main p").filter(has_text="Showing").first
        self.prev_page_button = page.locator("main button").filter(has_text="Previous").first
        self.next_page_button = page.locator("main button").filter(has_text="Next").first
        self.page_number_indicator = page.locator("main div, main span").filter(has_text="Page 1").first

    def navigate(self) -> None:
        """Navigate to Refer & Earn view via sidebar."""
        if "/client-portal" not in self.page.url:
            self.goto(settings.client_portal.base_url)
        self.sidebar.navigate_to_refer_earn()
        expect(self.header.title_heading.first).to_have_text("Refer & Earn", timeout=10000)

    def is_refer_earn_displayed(self) -> bool:
        """Verify presence of Refer & Earn workspace."""
        return self.heading.first.is_visible() and self.unique_link_input.first.is_visible()

    def get_referral_link(self) -> str:
        """Read and return generated unique referral URL from input."""
        return self.unique_link_input.first.input_value()

    def click_copy_link_and_verify_feedback(self) -> None:
        """Click the Copy button and verify button text changes to 'Copied!'."""
        self.copy_link_button.first.click()
        expect(self.copied_feedback_button.first).to_be_visible(timeout=3000)

    def select_rows_per_page(self, rows: str) -> None:
        """Select row count per page (10, 25, 50, 100)."""
        self.rows_per_page_select.first.select_option(rows)

    def get_table_header_titles(self) -> List[str]:
        """Return list of column header titles."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def get_referred_clients_count(self) -> int:
        """Return number of displayed rows in the referred clients table."""
        return self.table_rows.count()

    def get_first_client_row_data(self) -> Dict[str, str]:
        """Extract data from first referral row."""
        if self.table_rows.count() == 0:
            return {}
        cells = self.table_rows.first.locator("td").all()
        return {
            "client": cells[0].inner_text().strip() if len(cells) > 0 else "",
            "account": cells[1].inner_text().strip() if len(cells) > 1 else "",
            "ref_id": cells[2].inner_text().strip() if len(cells) > 2 else "",
            "mobile": cells[3].inner_text().strip() if len(cells) > 3 else "",
            "balance": cells[4].inner_text().strip() if len(cells) > 4 else "",
            "activity": cells[5].inner_text().strip() if len(cells) > 5 else "",
            "ib_earned": cells[6].inner_text().strip() if len(cells) > 6 else "",
        }

    def click_refresh_referrals(self) -> None:
        """Click the refresh referrals button."""
        self.refresh_button.first.click()

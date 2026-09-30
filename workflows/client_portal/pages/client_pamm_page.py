"""
Client Portal PAMM (Percentage Allocation Management Module) Page Object.
Comprehensive encapsulation of all minute controls:
- Universal header integration and page title ('PAMM')
- 4 Summary Cards (MANAGERS, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS)
- View Switching ('PAMM MANAGER', 'MY FOLLOWERS' with Active/History tabs)
- Dropdown Filters (Range: 30D/90D/1Y/All Time, Risk, Fund, Rows: 10/25/50)
- Refresh action button ('Refresh')
- Search bar filter ('Search...')
- PAMM Managers Table:
  * 9 columns (NAME, RANK, GROWTH, WIN RATE, TRADES, DRAWDOWN, MANAGED, RISK, ACTION)
  * Dynamic rows per PAMM manager
  * Inline 'Statistics' icon button on each row
  * Inline 'Follow' action button on each row
  * Pagination navigation ('Prev', 'Next')
- Statistics Modal Dialog:
  * Modal title ('PAMM STATISTICS')
  * Metric cards (NET PROFIT, GROWTH, WIN RATE, PROFIT FACTOR, CLOSED TRADES, TOTAL LOTS, DRAWDOWN, MANAGED)
  * Equity Curve chart
  * Close action
- Follow PAMM Manager Modal Dialog:
  * Manager name in modal title ('Follow Manager <Name>')
  * Investment amount input field ('INVESTMENT AMOUNT')
  * Debit notice
  * 'Cancel' and 'CONFIRM FOLLOW' action buttons
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


class ClientPAMMPage(BasePage):
    """Page object for Client Portal PAMM workflow."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Headings
        self.main_heading = page.locator("main h1").filter(has_text=re.compile(r"^PAMM$", re.I))

        # 4 Summary Cards
        self.managers_card = page.locator("main .grid > div").filter(has_text=re.compile(r"^MANAGERS", re.I)).first
        self.managed_capital_card = page.locator("main .grid > div").filter(has_text=re.compile(r"^MANAGED\s*CAPITAL", re.I)).first
        self.closed_trades_card = page.locator("main .grid > div").filter(has_text=re.compile(r"^CLOSED\s*TRADES", re.I)).first
        self.followers_card = page.locator("main .grid > div").filter(has_text=re.compile(r"^FOLLOWERS", re.I)).first

        # Top Action Buttons (View Switching)
        self.pamm_manager_btn = page.locator("main button").filter(has_text=re.compile(r"PAMM\s*MANAGER", re.I)).first
        self.my_followers_btn = page.locator("main button").filter(has_text=re.compile(r"MY\s*FOLLOWERS", re.I)).first
        self.followers_active_btn = page.locator("main button").filter(has_text=re.compile(r"^Active$", re.I)).first
        self.followers_history_btn = page.locator("main button").filter(has_text=re.compile(r"^History$", re.I)).first

        # Dropdowns
        self.range_select = page.locator("main select").nth(0)
        self.risk_select = page.locator("main select").nth(1)
        self.fund_select = page.locator("main select").nth(2)
        self.rows_select = page.locator("main select").nth(3)

        # Refresh & Search
        self.refresh_button = page.locator("main button[title='Refresh']").first
        self.search_input = page.locator("main input[placeholder*='Search' i]").first

        # Table & Pagination
        self.table = page.locator("main table").first
        self.table_headers = self.table.locator("th")
        self.table_rows = self.table.locator("tbody tr")
        self.prev_btn = page.locator("main button").filter(has_text="Prev").first
        self.next_btn = page.locator("main button").filter(has_text="Next").first

        # Statistics Modal Dialog
        self.statistics_modal = page.locator("div.fixed.inset-0.z-50").filter(
            has_text=re.compile(r"STATISTICS", re.I)
        )
        self.statistics_modal_close_btn = self.statistics_modal.locator("button").first

        # Follow PAMM Modal Dialog
        self.follow_modal = page.locator("div.fixed.inset-0.z-50").filter(
            has_text=re.compile(r"Follow\s*Manager", re.I)
        )
        self.investment_amount_input = self.follow_modal.locator("input").first
        self.modal_cancel_btn = self.follow_modal.locator("button").filter(has_text="Cancel").first
        self.modal_confirm_btn = self.follow_modal.locator("button").filter(has_text=re.compile(r"CONFIRM\s*FOLLOW", re.I)).first

        # Unfollow PAMM Modal Dialog
        self.unfollow_modal = page.locator("div.fixed.inset-0.z-50").filter(
            has_text=re.compile(r"Unfollow\s*Manager", re.I)
        )
        self.unfollow_cancel_btn = self.unfollow_modal.locator("button").filter(has_text="Cancel").first
        self.unfollow_confirm_btn = self.unfollow_modal.locator("button").filter(has_text=re.compile(r"CONFIRM\s*UNFOLLOW", re.I)).first

    def navigate(self) -> None:
        """Navigate to PAMM view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_pamm()
        expect(self.header.title_heading.first).to_have_text("PAMM", timeout=15000)
        expect(self.main_heading.first).to_be_visible(timeout=10000)
        expect(self.table).to_be_visible(timeout=10000)

    def is_pamm_displayed(self) -> bool:
        """Verify presence of PAMM elements."""
        return self.main_heading.first.is_visible() and self.table.is_visible()

    def get_summary_card_values(self) -> Dict[str, str]:
        """Extract numerical metrics from the 4 summary cards."""
        return {
            "managers": self.managers_card.inner_text().strip().replace("\n", " "),
            "managed_capital": self.managed_capital_card.inner_text().strip().replace("\n", " "),
            "closed_trades": self.closed_trades_card.inner_text().strip().replace("\n", " "),
            "followers": self.followers_card.inner_text().strip().replace("\n", " "),
        }

    def switch_to_my_followers(self) -> None:
        """Switch to My Followers view."""
        expect(self.my_followers_btn).to_be_visible(timeout=5000)
        self.my_followers_btn.click()
        expect(self.followers_active_btn).to_be_visible(timeout=5000)

    def switch_to_pamm_manager(self) -> None:
        """Switch back to PAMM Manager view."""
        expect(self.pamm_manager_btn).to_be_visible(timeout=5000)
        self.pamm_manager_btn.click()
        expect(self.table).to_be_visible(timeout=5000)

    def get_followers_table_headers(self) -> List[str]:
        """Return column headers of followers table."""
        return [th.inner_text().strip() for th in self.page.locator("main table th").all()]

    def get_followers_count(self) -> int:
        """Return row count of followers table."""
        return self.page.locator("main table tbody tr").count()

    def click_refresh(self) -> None:
        """Click the Refresh action button."""
        expect(self.refresh_button).to_be_visible(timeout=5000)
        self.refresh_button.click()
        self.page.wait_for_timeout(500)

    def get_table_headers(self) -> List[str]:
        """Return column headers of PAMM table."""
        return [th.inner_text().strip() for th in self.table_headers.all()]

    def get_manager_count(self) -> int:
        """Return count of PAMM managers."""
        return self.table_rows.count()

    def filter_by_search(self, query: str) -> None:
        """Filter table by manager name."""
        self.search_input.fill(query)
        self.page.wait_for_timeout(1000)

    def clear_search(self) -> None:
        """Clear search filter."""
        self.search_input.fill("")
        self.page.wait_for_timeout(1000)

    def open_statistics_modal(self, row_index: int = 0) -> None:
        """Click Statistics button on a PAMM row and verify modal opens."""
        row = self.table_rows.nth(row_index)
        stats_btn = row.locator("button[title='Statistics']").first
        expect(stats_btn).to_be_visible(timeout=5000)
        stats_btn.click()
        expect(self.statistics_modal.first).to_be_visible(timeout=5000)
        loading = self.statistics_modal.first.get_by_text("Loading statistics...")
        if loading.is_visible():
            expect(loading).not_to_be_visible(timeout=10000)
        self.page.wait_for_timeout(500)

    def close_statistics_modal(self) -> None:
        """Close Statistics modal via dismiss button."""
        if self.statistics_modal.is_visible():
            expect(self.statistics_modal_close_btn).to_be_visible(timeout=5000)
            self.statistics_modal_close_btn.click()
            expect(self.statistics_modal.first).not_to_be_visible(timeout=5000)

    def open_follow_modal(self, row_index: int = 0) -> str:
        """Click Follow on a PAMM row and verify modal."""
        row = self.table_rows.nth(row_index)
        manager_name = row.locator("td").first.inner_text().strip().split("\n")[0]
        follow_btn = row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first
        expect(follow_btn).to_be_visible(timeout=5000)
        follow_btn.click()
        expect(self.follow_modal.first).to_be_visible(timeout=5000)
        return manager_name

    def close_follow_modal(self) -> None:
        """Dismiss follow modal via Cancel button."""
        if self.follow_modal.is_visible():
            expect(self.modal_cancel_btn).to_be_visible(timeout=5000)
            self.modal_cancel_btn.click()
            expect(self.follow_modal.first).not_to_be_visible(timeout=5000)

    def find_manager_row(self, identifier: str) -> Locator:
        """
        Locate PAMM manager row by account ID or manager name.
        Uses search bar to isolate manager row.
        """
        query = "Me" if str(identifier) in ("10026", "Me") else str(identifier)
        self.search_input.fill(query)
        self.page.wait_for_timeout(1000)

        row = self.table_rows.filter(has_text=identifier).first
        expect(row).to_be_visible(timeout=10000)
        return row

    def follow_manager(self, identifier: str = "10026", investment_amount: str = "100") -> str:
        """
        Follow specified PAMM manager with investment amount.
        Returns:
            'followed': newly followed (transitioned to Unfollow)
            'already_following': was already followed
            'pending_settlement': follow request submitted, backend reported pending settlement
        """
        row = self.find_manager_row(identifier)
        follow_btn = row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first
        unfollow_btn = row.locator("button").filter(has_text=re.compile(r"^Unfollow$", re.I)).first

        if not follow_btn.is_visible() and unfollow_btn.is_visible():
            return "already_following"

        expect(follow_btn).to_be_visible(timeout=5000)
        follow_btn.click()
        expect(self.follow_modal.first).to_be_visible(timeout=5000)

        # Fill investment amount
        if investment_amount and self.investment_amount_input.is_visible():
            self.investment_amount_input.fill(str(investment_amount))

        expect(self.modal_confirm_btn).to_be_visible(timeout=5000)
        self.modal_confirm_btn.click()
        self.page.wait_for_timeout(2000)

        # Check if modal remains with settlement message
        if self.follow_modal.first.is_visible():
            modal_text = self.follow_modal.first.inner_text()
            if "pending broker settlement" in modal_text or "waits for outstanding orders" in modal_text:
                if self.modal_cancel_btn.is_visible():
                    self.modal_cancel_btn.click()
                    expect(self.follow_modal.first).not_to_be_visible(timeout=5000)
                return "pending_settlement"
            expect(self.follow_modal.first).not_to_be_visible(timeout=10000)

        self.page.wait_for_timeout(1000)
        return "followed"

    def unfollow_manager(self, identifier: str = "10026") -> str:
        """
        Unfollow specified PAMM manager.
        Returns:
            'unfollowed': newly unfollowed
            'already_unfollowed': was not following
        """
        row = self.find_manager_row(identifier)
        unfollow_btn = row.locator("button").filter(has_text=re.compile(r"^Unfollow$", re.I)).first
        follow_btn = row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first

        if not unfollow_btn.is_visible() and follow_btn.is_visible():
            return "already_unfollowed"

        expect(unfollow_btn).to_be_visible(timeout=5000)
        unfollow_btn.click()
        expect(self.unfollow_modal.first).to_be_visible(timeout=5000)
        expect(self.unfollow_confirm_btn).to_be_visible(timeout=5000)
        self.unfollow_confirm_btn.click()
        expect(self.unfollow_modal.first).not_to_be_visible(timeout=10000)
        expect(row.locator("button").filter(has_text=re.compile(r"^Follow$", re.I)).first).to_be_visible(timeout=10000)
        self.page.wait_for_timeout(1000)
        return "unfollowed"

    def get_followers_table_records(self) -> List[Dict[str, str]]:
        """
        Extract structured follower records from PAMM MY FOLLOWERS table.
        Columns: ['NAME', 'INVESTMENT', 'MANAGER SHARE (ELIGIBLE ORDERS)', 'ACTION']
        """
        expect(self.table.locator("th").first).to_be_visible(timeout=10000)
        self.page.wait_for_timeout(1500)
        records = []
        rows = self.page.locator("main table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            tds = row.locator("td").all()
            if len(tds) >= 3:
                name = tds[0].inner_text().strip().replace("\n", " ")
                investment = tds[1].inner_text().strip()
                manager_share = tds[2].inner_text().strip()
                if name or investment:
                    records.append({
                        "name": name,
                        "investment": investment,
                        "manager_share": manager_share,
                    })
        return records

"""
Admin Portal Active Users Page Object.
Handles the Active Users datatable (#au-datatable).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List
from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage


class AdminActiveUsersPage(BasePage):
    """Page object for the Admin Active Users table and controls."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Datatable & Main Layout Locators
        self.table = page.locator("#au-datatable")
        self.table_wrapper = page.locator("#au-datatable_wrapper")
        self.headers = page.locator("#au-datatable thead tr th")
        self.rows = page.locator("#au-datatable tbody tr")
        
        # Datatable Controls
        self.entries_select = page.locator("select[name='au-datatable_length']")
        self.search_input = page.locator("#au-datatable_filter input")
        self.info_status = page.locator("#au-datatable_info")
        self.pagination = page.locator("#au-datatable_paginate")
        self.previous_button = page.locator("#au-datatable_previous")
        self.next_button = page.locator("#au-datatable_next")
        
        # Row Indicators
        self.online_indicators = page.locator("#au-datatable tbody .led-green")
        self.empty_message = page.locator("#au-datatable tbody td.dataTables_empty")

    def navigate(self, url: str = "https://stage.xtremenext.com/admin/Controlbase/activeUsers") -> None:
        """Navigate to the Active Users page."""
        self.goto(url)

    def is_table_displayed(self) -> bool:
        """Check whether the active users table and controls are visible."""
        return self.table.is_visible() and self.search_input.is_visible()

    def search_user(self, query: str) -> None:
        """Search active users table by name, account number, or token."""
        self.clear_and_fill("#au-datatable_filter input", query)

    def clear_search(self) -> None:
        """Clear search input field."""
        self.search_input.clear()

    def get_header_titles(self) -> List[str]:
        """Return list of header column titles."""
        return [header.inner_text().strip() for header in self.headers.all()]

    def get_row_count(self) -> int:
        """Return the count of rows currently displayed in the table."""
        return self.rows.count()

    def select_page_length(self, value: str) -> None:
        """Select page length option (10, 25, 50, 100)."""
        self.select_option("select[name='au-datatable_length']", value=value)

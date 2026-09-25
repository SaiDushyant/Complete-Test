"""
Admin Portal User Management Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List

from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class UserManagementPage(BasePage):
    """Page object for Admin User Management table and actions."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.locator("input[type='search'], #userSearch, input[name='search']")
        self.status_filter_dropdown = page.locator("select[name='status'], #statusFilter")
        self.users_table = page.locator(".users-table, table.dataTable, #usersTable")
        self.user_rows = page.locator("table tbody tr")
        self.create_user_button = page.locator("button:has-text('Create User'), a:has-text('New User'), .btn-create")

    def search_user(self, query: str) -> None:
        """Search users by name or email."""
        # TODO (Developer 2): Implement search filtering interaction
        if self.search_input.first.is_visible():
            self.search_input.first.fill(query)
            self.search_input.first.press("Enter")

    def get_user_count(self) -> int:
        """Return count of users displayed in table."""
        return self.user_rows.count()

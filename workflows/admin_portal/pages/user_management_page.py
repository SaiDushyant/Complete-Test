"""
Admin Portal User Management Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class UserManagementPage(BasePage):
    """Page object for Admin User Management table and actions."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.search_input = page.locator(
            "input[type='search'], #userSearch, input[name='search']"
        )
        self.status_filter_dropdown = page.locator(
            "select[name='status'], #statusFilter"
        )
        self.users_table = page.locator(
            ".users-table, table.dataTable, #usersTable"
        )
        self.user_rows = page.locator("table tbody tr")
        self.create_user_button = page.locator(
    "button:has-text('Add User'), "
    "a:has-text('Add User'), "
    "button:has-text('Create Account'), "
    "a:has-text('Create Account'), "
    "button:has-text('Create User'), "
    "a:has-text('New User'), "
    ".btn-create"
)

    def navigate(self) -> None:
        """Navigate to the Admin User Management page."""
        user_management_url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/user"
        )
        self.goto(user_management_url)

    def search_user(self, query: str) -> None:
        """Search users by name or email."""
        if self.search_input.first.is_visible():
            self.search_input.first.fill(query)
            self.search_input.first.press("Enter")

    def get_user_count(self) -> int:
        """Return the number of users displayed in the table."""
        return self.user_rows.count()
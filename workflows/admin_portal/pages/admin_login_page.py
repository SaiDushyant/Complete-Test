"""
Admin Portal Login Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class AdminLoginPage(BasePage):
    """Page object for Admin Console login interface."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.locator("#username, input[name='username']")
        self.password_input = page.locator("#password, input[name='password']")
        self.submit_button = page.locator('button.btn-login-primary, button[type="submit"], input[type="submit"]')

    def navigate(self, url: str = None) -> None:
        """Navigate to Admin Console login page."""
        target_url = url or settings.admin_portal.login_url or settings.admin_portal.base_url
        self.goto(target_url)

    def is_login_page_displayed(self) -> bool:
        """Check if admin login input elements are visible."""
        return self.username_input.first.is_visible() and self.password_input.first.is_visible()

    def login(self, username: str = None, password: str = None) -> None:
        """Execute admin authentication action."""
        user = username or settings.admin_portal.username
        pwd = password or settings.admin_portal.password

        if not user or not pwd:
            raise ValueError("Admin Portal credentials missing from configuration/.env")

        self.username_input.first.fill(user)
        self.password_input.first.fill(pwd)
        self.submit_button.first.click()

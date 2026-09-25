"""
Client Portal Login Page Object.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class ClientLoginPage(BasePage):
    """Page object for Client Portal login interface."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.locator("#email, input[name='email'], input[type='email']")
        self.password_input = page.locator("#password, input[name='password'], input[type='password']")
        self.remember_me_checkbox = page.locator("#inputCheckbox, input[type='checkbox']")
        self.login_button = page.locator('button.xn-btn-login[type="submit"], button[type="submit"]')

    def navigate(self, url: str = None) -> None:
        """Navigate to Client Portal login page."""
        target_url = url or settings.client_portal.login_url or settings.client_portal.base_url
        self.goto(target_url)

    def is_login_page_displayed(self) -> bool:
        """Check if login input elements are visible."""
        return self.email_input.first.is_visible() and self.password_input.first.is_visible()

    def login(self, email: str = None, password: str = None, remember_me: bool = True) -> None:
        """Perform client login action."""
        user = email or settings.client_portal.username
        pwd = password or settings.client_portal.password

        if not user or not pwd:
            raise ValueError("Client Portal credentials missing from configuration/.env")

        self.email_input.first.fill(user)
        self.password_input.first.fill(pwd)

        if remember_me and self.remember_me_checkbox.first.is_visible():
            if not self.remember_me_checkbox.first.is_checked():
                self.remember_me_checkbox.first.check()

        self.login_button.first.click()

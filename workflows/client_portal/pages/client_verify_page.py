"""
Client Portal Verification Page Object.
Encapsulates:
1. Pending verification screen (/verify/)
2. Verified confirmation landing page (/verify/verify_user.php)
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Optional
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_verify_page")


class ClientVerifyPage(BasePage):
    """
    Page Object Model representing the email verification screen and verified landing state.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Pending Verification Screen (/verify/)
        self.verify_heading: Locator = page.locator("h2, h3, h4, h5, .card-title").first
        self.verify_message: Locator = page.locator("body")
        self.login_to_account_btn: Locator = page.locator("a:has-text('Login to Your Account'), a:has-text('Login'), button:has-text('Login')").first
        self.resend_verify_link: Locator = page.locator("a:has-text('Resend verify link'), a:has-text('Resend')").first
        self.logout_link: Locator = page.locator("a:has-text('Logout')").first

        # Verified Confirmation Page (/verify/verify_user.php)
        self.success_container: Locator = page.locator(".card, .container, body")
        self.login_after_verify_btn: Locator = page.locator("a:has-text('Login to Your Account')").first

    def navigate(self, url: Optional[str] = None) -> None:
        """Navigate directly to the verify endpoint."""
        target_url = url or f"{settings.client_portal.base_url.rstrip('/')}/verify/"
        logger.info(f"Navigating to Verification page: {target_url}")
        self.goto(target_url)

    def is_verification_pending_displayed(self) -> bool:
        """Check if 'Email Verification Required' message is displayed on /verify/."""
        text = self.verify_message.inner_text().lower()
        return "verification" in text and "email" in text

    def is_verification_success_displayed(self) -> bool:
        """Check if 'successfully verified' confirmation message is displayed."""
        text = self.verify_message.inner_text().lower()
        return "successfully verified" in text or "welcome to wavex one" in text

    def click_login_to_account(self) -> None:
        """Click 'Login to Your Account' button."""
        logger.info("Clicking 'Login to Your Account' button...")
        expect(self.login_to_account_btn).to_be_visible(timeout=10000)
        self.login_to_account_btn.click()
        self.page.wait_for_timeout(1000)

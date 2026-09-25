"""
Trade Terminal Login Page Object.
Encapsulates login form interactions, element validations, and authentication persistence.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("trade_login_page")


class TradeLoginPage(BasePage):
    """
    Page Object Model representing the Trade Terminal Login page.
    Encapsulates HTML form (#register.xn-login-form) and post-login transitions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Form Container
        self.login_form: Locator = page.locator("form#register.xn-login-form, form.xn-login-form")

        # Credentials Fields & Labels
        self.email_input: Locator = page.locator("#email")
        self.email_label: Locator = page.locator("label[for='email']")
        self.password_input: Locator = page.locator("#password")
        self.password_label: Locator = page.locator("label[for='password']")
        self.password_toggle: Locator = page.locator("span.toggle-password")

        # Checkbox & Options
        self.remember_me_checkbox: Locator = page.locator("#inputCheckbox")
        self.remember_me_label: Locator = page.locator("label[for='inputCheckbox']")
        self.forgot_password_link: Locator = page.locator("a.xn-forgot")

        # Submission & Hidden Elements
        self.login_button: Locator = page.locator("button.xn-btn-login, button.savebut[type='submit']")
        self.profile_data_hidden: Locator = page.locator("#profile_data")

    def navigate(self, url: Optional[str] = None) -> None:
        """
        Navigate to Trade Terminal login endpoint and wait for form readiness.
        Defaults to settings.trade_terminal.login_url or https://stage.xtremenext.com/login/.
        """
        target_url = (
            url
            or settings.trade_terminal.login_url
            or f"{settings.trade_terminal.base_url.rstrip('/')}/login/"
        )
        logger.info(f"Navigating to Trade Terminal login: {target_url}")
        self.goto(target_url)
        self.email_input.wait_for(state="visible", timeout=settings.browser.timeout)

    def is_login_page_displayed(self) -> bool:
        """
        Verify that core login form elements are present and visible on screen.
        """
        return (
            self.email_input.first.is_visible()
            and self.password_input.first.is_visible()
            and self.login_button.first.is_visible()
        )

    def fill_credentials(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
    ) -> None:
        """
        Populate username/email and password fields with credential handling.
        """
        user = username or settings.trade_terminal.username
        pwd = password or settings.trade_terminal.password

        if not user or not pwd:
            raise ValueError(
                "Trade Terminal credentials missing from configuration or .env. "
                "Ensure TRADE_USERNAME and TRADE_PASSWORD (or BASELINE_TEST_USER_EMAIL / "
                "BASELINE_TEST_USER_PASSWORD) are set."
            )

        logger.info(f"Filling credentials for Trade Terminal account: {user}")
        self.email_input.first.fill(user)
        self.password_input.first.fill(pwd)

        if self.remember_me_checkbox.first.is_visible():
            if remember_me and not self.remember_me_checkbox.first.is_checked():
                self.remember_me_checkbox.first.check()
            elif not remember_me and self.remember_me_checkbox.first.is_checked():
                self.remember_me_checkbox.first.uncheck()

    def click_login(self) -> None:
        """Click the login submit button."""
        logger.info("Submitting login form via .xn-btn-login")
        self.login_button.first.click()

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
    ) -> None:
        """
        Execute full login sequence: populate inputs, toggle remember-me, and submit.
        """
        self.fill_credentials(username=username, password=password, remember_me=remember_me)
        self.click_login()

    def login_and_wait_for_dashboard(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
        timeout: int = 30000,
    ) -> str:
        """
        Execute login and wait for URL redirection to the dashboard workspace.
        Returns the resolved dashboard URL.
        """
        self.login(username=username, password=password, remember_me=remember_me)
        post_login_pattern = settings.trade_terminal.post_login_url_pattern or "**/dashboard**"
        logger.info(f"Waiting for dashboard redirection matching: {post_login_pattern}")
        self.page.wait_for_url(post_login_pattern, timeout=timeout)
        return self.current_url

    def save_auth_state(self, path: Optional[Path | str] = None) -> Path:
        """
        Persist current browser context storage state (session cookies, local storage)
        to the designated auth state JSON path.
        """
        target_path = Path(path) if path else settings.trade_terminal.auth_state_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.context.storage_state(path=str(target_path))
        logger.info(f"Saved Trade Terminal auth state to: {target_path}")
        return target_path

    def toggle_password_visibility(self) -> None:
        """Toggle visibility of the password field using the eye icon."""
        if self.password_toggle.first.is_visible():
            self.password_toggle.first.click()

    def click_forgot_password(self) -> None:
        """Click the 'Forgot password?' anchor link."""
        self.forgot_password_link.first.click()

    def is_remember_me_checked(self) -> bool:
        """Check whether the remember me checkbox is currently checked."""
        return self.remember_me_checkbox.first.is_checked()

"""
Client Portal Login Page Object.
Encapsulates login form interactions, element validations, and authentication persistence.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_login_page")


class ClientLoginPage(BasePage):
    """
    Page Object Model representing the Client Portal Login page.
    Encapsulates HTML form (#register.xn-login-form) and post-login transitions.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Form Container
        self.login_form: Locator = page.locator("form#register.xn-login-form, form.xn-login-form, form")

        # Credentials Fields & Labels
        self.email_input: Locator = page.locator("#email, input[name='email'], input[type='email']").first
        self.email_label: Locator = page.locator("label[for='email'], label:has-text('Email')").first
        self.password_input: Locator = page.locator("#password, input[name='password'], input[type='password']").first
        self.password_label: Locator = page.locator("label[for='password'], label:has-text('Password')").first
        self.password_toggle: Locator = page.locator("span.toggle-password, .toggle-password, button:has(svg)").first

        # Checkbox & Options
        self.remember_me_checkbox: Locator = page.locator("#inputCheckbox, input[type='checkbox']").first
        self.remember_me_label: Locator = page.locator("label[for='inputCheckbox'], label:has-text('Remember')").first
        self.forgot_password_link: Locator = page.locator("a.xn-forgot, a:has-text('Forgot')").first

        # Submission & Hidden Elements
        self.login_button: Locator = page.locator("button.xn-btn-login, button.savebut[type='submit'], button[type='submit']").first
        self.profile_data_hidden: Locator = page.locator("#profile_data").first

    def navigate(self, url: Optional[str] = None) -> None:
        """
        Navigate to Client Portal login endpoint and wait for form readiness.
        Defaults to settings.client_portal.login_url or base URL.
        """
        target_url = (
            url
            or settings.client_portal.login_url
            or f"{settings.client_portal.base_url.rstrip('/')}/login/"
        )
        logger.info(f"Navigating to Client Portal login: {target_url}")
        self.goto(target_url)
        self.email_input.wait_for(state="visible", timeout=settings.browser.timeout)

    def is_login_page_displayed(self) -> bool:
        """
        Verify that core login form elements are present and visible on screen.
        """
        return (
            self.email_input.is_visible()
            and self.password_input.is_visible()
            and self.login_button.is_visible()
        )

    def fill_credentials(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
        email: Optional[str] = None,
    ) -> None:
        """
        Populate username/email and password fields with credential handling.
        Supports both 'username' and 'email' parameter names.
        """
        user = username or email or settings.client_portal.username
        pwd = password or settings.client_portal.password

        if not user or not pwd:
            raise ValueError(
                "Client Portal credentials missing from configuration or .env. "
                "Ensure CLIENT_USERNAME and CLIENT_PASSWORD (or BASELINE_TEST_USER_EMAIL / "
                "BASELINE_TEST_USER_PASSWORD) are set."
            )

        logger.info(f"Filling credentials for Client Portal account: {user}")
        self.email_input.fill(user)
        self.password_input.fill(pwd)

        if self.remember_me_checkbox.is_visible():
            if remember_me and not self.remember_me_checkbox.is_checked():
                self.remember_me_checkbox.check()
            elif not remember_me and self.remember_me_checkbox.is_checked():
                self.remember_me_checkbox.uncheck()

    def click_login(self) -> None:
        """Click the login submit button."""
        logger.info("Submitting login form via .xn-btn-login")
        self.login_button.click()

    def login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
        email: Optional[str] = None,
    ) -> None:
        """
        Execute full login sequence: populate inputs, toggle remember-me, and submit.
        """
        self.fill_credentials(username=username, password=password, remember_me=remember_me, email=email)
        self.click_login()

    def login_and_wait_for_dashboard(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remember_me: bool = True,
        timeout: int = 30000,
        email: Optional[str] = None,
    ) -> str:
        """
        Execute login and wait for URL redirection to the dashboard workspace.
        Returns the resolved dashboard URL.
        """
        self.login(username=username, password=password, remember_me=remember_me, email=email)
        post_login_pattern = settings.client_portal.post_login_url_pattern or "**/dashboard**"
        logger.info(f"Waiting for dashboard redirection matching: {post_login_pattern}")
        self.page.wait_for_url(post_login_pattern, timeout=timeout, wait_until="domcontentloaded")
        return self.current_url

    def navigate_to_client_portal(self, timeout: int = 15000) -> str:
        """
        Navigate to the Client Portal endpoint (/client-portal) after authentication.
        """
        portal_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        logger.info(f"Navigating to Client Portal: {portal_url}")
        self.goto(portal_url)
        self.page.wait_for_load_state("domcontentloaded")
        return self.current_url

    def save_auth_state(self, path: Optional[Path | str] = None) -> Path:
        """
        Persist current browser context storage state (session cookies, local storage)
        to the designated auth state JSON path.
        """
        target_path = Path(path) if path else settings.client_portal.auth_state_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.context.storage_state(path=str(target_path))
        logger.info(f"Saved Client Portal auth state to: {target_path}")
        return target_path

    def toggle_password_visibility(self) -> None:
        """Toggle visibility of the password field using the eye icon."""
        if self.password_toggle.is_visible():
            self.password_toggle.click()

    def click_forgot_password(self) -> None:
        """Click the 'Forgot password?' anchor link."""
        self.forgot_password_link.click()

    def is_remember_me_checked(self) -> bool:
        """Check whether the remember me checkbox is currently checked."""
        return self.remember_me_checkbox.is_checked()

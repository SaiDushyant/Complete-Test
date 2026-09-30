"""
Client Portal Registration / Signup Page Object.
Encapsulates two-step signup form:
- Step 1: Full Name, Email Address, Phone Number, Country Code
- Step 2: Password, Confirm Password, Account Type, Leverage/Subgroup, Referral Code, Terms & Conditions
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from typing import Dict, List, Optional
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("client_register_page")


class ClientRegisterPage(BasePage):
    """
    Page Object Model representing the Client Portal Registration page at /register/.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Form Container
        self.register_form: Locator = page.locator("form#register")

        # Step 1 Locators
        self.step_1_container: Locator = page.locator("#step-1")
        self.name_input: Locator = page.locator("#name")
        self.name_label: Locator = page.locator("label[for='name']")
        self.email_input: Locator = page.locator("#email")
        self.email_label: Locator = page.locator("label[for='email']")
        self.phone_input: Locator = page.locator("#number")
        self.phone_label: Locator = page.locator("label[for='number']")
        self.country_code_btn: Locator = page.locator(".iti__selected-dial-code, .iti__flag-container")
        self.next_button: Locator = page.locator("button.next-btn")
        self.signin_link: Locator = page.locator("a:has-text('Sign in')")

        # Step 2 Locators
        self.step_2_container: Locator = page.locator("#step-2")
        self.password_input: Locator = page.locator("#pass1")
        self.confirm_password_input: Locator = page.locator("#pass2")
        self.group_select: Locator = page.locator("#group_id")
        self.subgroup_select: Locator = page.locator("#subgroup_value")
        self.referral_input: Locator = page.locator("#referral")
        self.terms_checkbox: Locator = page.locator("#inputCheckbox")
        self.terms_label: Locator = page.locator("label[for='inputCheckbox']")
        self.prev_button: Locator = page.locator("button.prev-btn")
        self.signup_submit_button: Locator = page.locator("button.savebut, button[type='submit']:has-text('Sign up')")

    def navigate(self, url: Optional[str] = None) -> None:
        """Navigate to Client Portal registration endpoint."""
        target_url = url or f"{settings.client_portal.base_url.rstrip('/')}/register/"
        logger.info(f"Navigating to Client Registration page: {target_url}")
        self.goto(target_url)
        self.name_input.wait_for(state="visible", timeout=settings.browser.timeout)

    def is_step_1_displayed(self) -> bool:
        """Check if Step 1 form fields are visible."""
        return (
            self.name_input.is_visible()
            and self.email_input.is_visible()
            and self.phone_input.is_visible()
            and self.next_button.is_visible()
        )

    def is_step_2_displayed(self) -> bool:
        """Check if Step 2 form fields are visible."""
        return (
            self.password_input.is_visible()
            and self.confirm_password_input.is_visible()
            and self.signup_submit_button.is_visible()
        )

    def fill_step_1(self, name: str, email: str, phone: str = "9876543210") -> None:
        """Fill Step 1 registration fields."""
        logger.info(f"Filling Step 1 with Name: '{name}', Email: '{email}', Phone: '{phone}'")
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)

    def click_next(self) -> None:
        """Click Next button to advance to Step 2."""
        logger.info("Clicking Next button...")
        expect(self.next_button).to_be_visible()
        self.next_button.click()
        self.page.wait_for_timeout(1000)
        expect(self.password_input).to_be_visible(timeout=10000)

    def fill_step_2(
        self,
        password: str = "TestPassword@123",
        group_id: Optional[str] = None,
        subgroup_value: Optional[str] = None,
        agree_terms: bool = True,
        referral_code: Optional[str] = None,
    ) -> None:
        """Fill Step 2 password, account type, leverage, and terms."""
        logger.info("Filling Step 2 registration fields...")
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)

        if referral_code and self.referral_input.is_visible():
            self.referral_input.fill(referral_code)

        # Select Account Type / Group
        if group_id:
            self.group_select.select_option(group_id)
        else:
            # Dynamically select first non-empty option
            options = self.group_select.locator("option").all()
            for opt in options:
                val = opt.get_attribute("value")
                if val and val != "0" and val != "":
                    self.group_select.select_option(val)
                    break

        # Wait for dynamic subgroup AJAX request
        self.page.wait_for_timeout(1500)

        # Select Leverage / Subgroup
        if subgroup_value:
            self.subgroup_select.select_option(subgroup_value)
        else:
            sub_options = self.subgroup_select.locator("option").all()
            for opt in sub_options:
                val = opt.get_attribute("value")
                if val and val != "0" and val != "":
                    self.subgroup_select.select_option(val)
                    break

        # Accept terms & conditions
        if agree_terms and not self.terms_checkbox.is_checked():
            self.terms_checkbox.check()

    def click_signup(self) -> None:
        """Submit the registration form."""
        logger.info("Submitting registration form via Sign up button...")
        expect(self.signup_submit_button).to_be_visible()
        self.signup_submit_button.click()

    def register_account(
        self,
        name: str,
        email: str,
        password: str = "TestPassword@123",
        phone: str = "9876543210",
        group_id: Optional[str] = None,
        subgroup_value: Optional[str] = None,
    ) -> None:
        """Execute complete two-step registration sequence."""
        self.fill_step_1(name=name, email=email, phone=phone)
        self.click_next()
        self.fill_step_2(
            password=password,
            group_id=group_id,
            subgroup_value=subgroup_value,
            agree_terms=True,
        )
        self.click_signup()

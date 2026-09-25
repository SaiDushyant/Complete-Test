"""
Client Portal Profile Page Object.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from workflows.client_portal.test_data.client_data import ClientProfileData
from workflows.shared.pages.base_page import BasePage


class ClientProfilePage(BasePage):
    """Page object for Client Portal user profile management."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.profile_container = page.locator(".profile-container, #profile, form.profile-form")
        self.first_name_input = page.locator("input[name='first_name'], #firstName")
        self.last_name_input = page.locator("input[name='last_name'], #lastName")
        self.phone_input = page.locator("input[name='phone'], input[name='mobile'], #phone")
        self.save_button = page.locator("button:has-text('Save'), button:has-text('Update'), button[type='submit']")
        self.success_toast = page.locator(".toast-success, .alert-success, .success-message")

    def is_profile_displayed(self) -> bool:
        """Check if profile container or form is visible."""
        return self.profile_container.first.is_visible()

    def update_profile_information(self, data: ClientProfileData) -> None:
        """Update client profile contact details."""
        # TODO (Developer 3): Implement field updates when profile inputs are mapped
        if self.phone_input.first.is_visible():
            self.phone_input.first.fill(data.phone_number)
        if self.save_button.first.is_visible():
            self.save_button.first.click()

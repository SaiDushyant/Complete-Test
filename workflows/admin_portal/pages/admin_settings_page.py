"""
Admin Portal Settings Page Object.
Handles the "Customize Admin Panel" configuration form.
"""

from __future__ import annotations

from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage


class AdminSettingsPage(BasePage):
    """Page object for the admin settings form."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.form = page.locator("form#settingsForm")
        self.card_title = page.locator("h4.card-title")
        self.submit_button = page.locator("#submitSettingsForm")
        self.lp_execution_config_link = page.get_by_role("link", name="LP Execution Config")

        self.project_name_input = page.locator("#projectName")
        self.color_code_input = page.locator("#colorCode")
        self.project_logo_input = page.locator("#projectLogo")
        self.user_limit_input = page.locator("#user_limit")
        self.maintenance_message_input = page.locator("#maintenance_message")
        self.maintenance_publish_button = page.locator("#publishMaintenance")

        self.terminal_maintenance_checkbox = page.locator("#maintenance_terminal")
        self.admin_maintenance_checkbox = page.locator("#maintenance_admin")
        self.client_portal_maintenance_checkbox = page.locator("#maintenance_client_portal")

        self.user_contact_toggle = page.locator("#show_user_contact")
        self.cent_switch_toggle = page.locator("#cent_switch_enabled")

    def navigate(self, url: str = "https://stage.xtremenext.com/admin/Controlbase/settings") -> None:
        """Navigate to the Admin settings form."""
        self.goto(url)

    def is_settings_form_visible(self) -> bool:
        """Check whether the Customize Admin Panel form is visible."""
        return self.form.is_visible() and self.submit_button.is_visible()

    def set_project_name(self, value: str) -> None:
        """Set the project name field."""
        self.project_name_input.fill(value)

    def set_color_code(self, value: str) -> None:
        """Set the color code field."""
        self.color_code_input.fill(value)

    def set_user_limit(self, value: str) -> None:
        """Set the maximum user limit value."""
        self.user_limit_input.fill(value)

    def set_maintenance_message(self, value: str) -> None:
        """Set maintenance message content."""
        self.maintenance_message_input.fill(value)

    def upload_logo(self, file_path: str) -> None:
        """Upload a project logo file."""
        self.project_logo_input.set_input_files(file_path)

    def enable_user_contact_visibility(self) -> None:
        """Enable the user email/mobile/password visibility toggle."""
        if not self.user_contact_toggle.is_checked():
            self.user_contact_toggle.click(force=True)

    def disable_user_contact_visibility(self) -> None:
        """Disable the user email/mobile/password visibility toggle."""
        if self.user_contact_toggle.is_checked():
            self.user_contact_toggle.click(force=True)

    def enable_cent_switch(self) -> None:
        """Enable the cent account switch toggle."""
        if not self.cent_switch_toggle.is_checked():
            self.cent_switch_toggle.click(force=True)

    def disable_cent_switch(self) -> None:
        """Disable the cent account switch toggle."""
        if self.cent_switch_toggle.is_checked():
            self.cent_switch_toggle.click(force=True)


    def publish_maintenance(self) -> None:
        """Click the Publish Maintenance button."""
        self.maintenance_publish_button.click()

    def click_submit(self) -> None:
        """Submit the settings form."""
        self.submit_button.click()

    def submit_settings(self) -> None:
        """Submit settings form after filling out the inputs."""
        self.click_submit()

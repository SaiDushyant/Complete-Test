"""
Admin Portal LP Execution Config Page Object.
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import settings
from workflows.shared.pages.base_page import BasePage


class LpExecutionConfigPage(BasePage):
    """Page object for Admin LP Execution Config topbar, form, and controls."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Topbar elements (.navbar-header)
        self.page_title = page.locator(".topbar-page-title")
        self.brand_logo = page.locator(".navbar-brand-box a.logo.admin-brand-logo")
        self.brand_logo_images = page.locator(".navbar-brand-box img")
        self.logo_small = page.locator(".navbar-brand-box img.mainLogoSmall")
        self.logo_large = page.locator(".navbar-brand-box img.mainLogoLarge")
        self.menu_button = page.locator("#vertical-menu-btn")
        self.theme_toggle = page.locator("#admin-theme-toggle")
        self.theme_dark_icon = page.locator("#admin-theme-toggle svg.theme-dark-icon")
        self.theme_light_icon = page.locator("#admin-theme-toggle svg.theme-light-icon")
        self.notification_button = page.locator("#page-header-notifications-dropdown")
        self.notification_count = page.locator("#notification-count")
        self.notification_menu = page.locator(".notification-menu")
        self.mark_all_read = page.locator("#markAllRead")
        self.notification_empty_text = page.locator(".notification-list p")
        self.profile_button = page.locator("#page-header-user-dropdown")
        self.profile_initials = page.locator("#page-header-user-dropdown .header-profile-initials")
        self.profile_topbar_name = page.locator("#page-header-user-dropdown span.fw-medium")
        self.profile_menu = page.locator(".profile-menu")
        self.profile_name = page.locator(".profile-menu .fw-bold")
        self.profile_role = page.locator(".profile-menu small")
        self.logout_link = page.locator(".profile-menu .logout-item")

        # Form Card & Container
        self.form_card = page.locator(".card").filter(has=page.locator("#lpExecutionConfigForm"))
        self.form = page.locator("#lpExecutionConfigForm")

        # Toggle switch: LP enabled for A-book execution
        self.enabled_switch = page.locator("#lp_enabled")
        self.enabled_switch_label = page.locator("label[for='lp_enabled']")

        # Provider dropdown
        self.provider_select = page.locator("#provider")
        self.provider_label = page.locator("label[for='provider']")

        # Owner selects
        self.order_open_owner_select = page.locator("#order_open_owner")
        self.order_open_owner_label = page.locator("label[for='order_open_owner']")

        self.pending_trigger_owner_select = page.locator("#pending_trigger_owner")
        self.pending_trigger_owner_label = page.locator("label[for='pending_trigger_owner']")

        self.sltp_execution_owner_select = page.locator("#sltp_execution_owner")
        self.sltp_execution_owner_label = page.locator("label[for='sltp_execution_owner']")

        self.pending_cancel_owner_select = page.locator("#pending_cancel_owner")
        self.pending_cancel_owner_label = page.locator("label[for='pending_cancel_owner']")

        self.owner_selects = page.locator(".owner-select")

        # URL inputs
        self.rest_base_url_input = page.locator("#rest_base_url")
        self.rest_base_url_label = page.locator("label[for='rest_base_url']")

        self.ws_primary_url_input = page.locator("#ws_primary_url")
        self.ws_primary_url_label = page.locator("label[for='ws_primary_url']")

        self.ws_fallback_url_input = page.locator("#ws_fallback_url")
        self.ws_fallback_url_label = page.locator("label[for='ws_fallback_url']")

        self.bridge_api_url_input = page.locator("#bridge_api_url")
        self.bridge_api_url_label = page.locator("label[for='bridge_api_url']")

        # Action Button & Status
        self.save_button = page.locator("#saveLpExecutionConfig")
        self.status_message = page.locator("#lpExecutionConfigStatus")

        # Loading indicator
        self.loader = page.locator("#loader")

    def navigate(self) -> None:
        """Navigate to the Admin LP Execution Config page and wait for loading."""
        url = (
            settings.admin_portal.base_url.rsplit("/", 1)[0]
            + "/lpExecutionConfig"
        )
        self.goto(url)
        self.wait_for_page_loaded()

    def wait_for_page_loaded(self, timeout: int = 15000) -> None:
        """Wait for the loader to disappear and page title to be visible."""
        try:
            self.loader.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass
        self.page_title.wait_for(state="visible", timeout=timeout)
        self.form.wait_for(state="visible", timeout=timeout)
        self.page.wait_for_timeout(500)

    def open_notifications(self) -> None:
        """Open the notifications dropdown."""
        self.notification_button.click()

    def open_profile_menu(self) -> None:
        """Open the admin user profile menu."""
        self.profile_button.click()

    def toggle_theme(self) -> None:
        """Click the theme switch button."""
        self.theme_toggle.click()

    def get_theme_mode(self) -> str | None:
        """Return the current data-layout-mode attribute of the body tag."""
        return self.page.locator("body").get_attribute("data-layout-mode")

    def is_lp_enabled(self) -> bool:
        """Check whether the LP execution toggle is checked."""
        return self.enabled_switch.is_checked()

    def toggle_lp_enabled(self) -> None:
        """Toggle the LP execution enabled checkbox."""
        self.enabled_switch.click()

    def get_provider_value(self) -> str:
        """Get the currently selected provider value."""
        return self.provider_select.input_value()

    def set_provider(self, value: str) -> None:
        """Select a provider option by value."""
        self.provider_select.select_option(value)

    def get_owner_values(self) -> dict[str, str]:
        """Get current values of all 4 owner selects."""
        return {
            "order_open_owner": self.order_open_owner_select.input_value(),
            "pending_trigger_owner": self.pending_trigger_owner_select.input_value(),
            "sltp_execution_owner": self.sltp_execution_owner_select.input_value(),
            "pending_cancel_owner": self.pending_cancel_owner_select.input_value(),
        }

    def get_url_values(self) -> dict[str, str]:
        """Get current values of all 4 URL inputs."""
        return {
            "rest_base_url": self.rest_base_url_input.input_value(),
            "ws_primary_url": self.ws_primary_url_input.input_value(),
            "ws_fallback_url": self.ws_fallback_url_input.input_value(),
            "bridge_api_url": self.bridge_api_url_input.input_value(),
        }

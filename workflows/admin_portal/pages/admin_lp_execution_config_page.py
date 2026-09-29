from __future__ import annotations

from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class AdminLpExecutionConfigPage(BasePage):
    """Page object for Admin LP Execution Config."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = page.locator(".page-title-box h4")
        self.form = page.locator("#lpExecutionConfigForm")
        self.enabled = page.locator("#lp_enabled")
        self.provider = page.locator("#provider")
        self.order_open_owner = page.locator("#order_open_owner")
        self.pending_trigger_owner = page.locator("#pending_trigger_owner")
        self.sltp_execution_owner = page.locator("#sltp_execution_owner")
        self.pending_cancel_owner = page.locator("#pending_cancel_owner")
        self.rest_base_url = page.locator("#rest_base_url")
        self.ws_primary_url = page.locator("#ws_primary_url")
        self.ws_fallback_url = page.locator("#ws_fallback_url")
        self.bridge_api_url = page.locator("#bridge_api_url")
        self.save_button = page.locator("#saveLpExecutionConfig")
        self.status = page.locator("#lpExecutionConfigStatus")

    def navigate(
        self,
        url: str = (
            "https://stage.xtremenext.com/"
            "admin/Controlbase/lpExecutionConfig"
        ),
    ) -> None:
        """Open the LP Execution Config page."""
        self.goto(url)
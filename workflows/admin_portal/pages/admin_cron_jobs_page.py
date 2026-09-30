"""
Admin Portal Cron Jobs Page Object.
Handles the Cron Jobs listing and edit modal.
"""

from __future__ import annotations

from playwright.sync_api import Page



from workflows.shared.pages.base_page import BasePage


class AdminCronJobsPage(BasePage):
    """Page object for the admin Cron Jobs page."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.page_title = page.locator(".page-title-box h4")
        self.table = page.locator("#datatable")
        self.table_rows = page.locator("#datatable tbody tr")
        self.search_input = page.locator("#datatable_filter input")
        self.edit_buttons = page.locator("a.btnEdit")

        self.modal = page.locator("#cronModal")
        self.modal_title = page.locator("#cronModal .modal-title")
        self.form = page.locator("#cronForm")
        self.close_button = page.locator("#cronModal .modal-header .btn-close")
        self.save_button = page.locator("#saveCronJob")

        self.hidden_id = page.locator("#cron_id")
        self.job_key = page.locator("#job_key")
        self.job_name = page.locator("#job_name")
        self.enabled_select = page.locator("#enabled")
        self.schedule_type_select = page.locator("#schedule_type")
        self.run_time_input = page.locator("#run_time")
        self.interval_input = page.locator("#interval_seconds")
        self.timezone_input = page.locator("#timezone")
        self.send_mail_select = page.locator("#send_mail")
        self.bbook_enabled_select = page.locator("#bbook_enabled")
        self.swap_enabled_select = page.locator("#swap_enabled")
        self.from_email_input = page.locator("#from_email")
        self.from_name_input = page.locator("#from_name")
        self.trigger_mode_select = page.locator("#is_trigger")

    def navigate(self, url: str = "https://stage.xtremenext.com/admin/Controlbase/cronJobs") -> None:
        """Navigate to the Cron Jobs page."""
        self.goto(url)

    def is_table_visible(self) -> bool:
        """Check whether the Cron Jobs table is visible."""
        return self.table.is_visible() and self.table_rows.count() > 0

    def open_first_cron_job(self) -> None:
        """Open the first edit modal for a cron job."""
        self.edit_buttons.first.click()

    def is_modal_visible(self) -> bool:
        """Check whether the edit modal is visible."""
        return self.modal.is_visible() and self.form.is_visible()

    def select_schedule_type(self, value: str) -> None:
        """Select a schedule type: daily or interval."""
        self.schedule_type_select.select_option(value=value)

    def click_save(self) -> None:
        """Click the Save button in the cron modal."""
        self.save_button.click()
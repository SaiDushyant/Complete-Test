from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class AdminOxapayPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.table = page.locator("#datatable")
        self.rows = page.locator("#datatable tbody tr")
        self.search = page.locator("#datatable_filter input[type='search']")
        self.entries = page.locator("select[name='datatable_length']")
        self.info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty")

    def navigate(self) -> None:
        self.goto(
            "https://stage.xtremenext.com/admin/Controlbase/oxapayPaymentTrack"
        )
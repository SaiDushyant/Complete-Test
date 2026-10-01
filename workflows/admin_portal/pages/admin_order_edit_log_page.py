from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class AdminOrderEditLogPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.table = page.locator("#datatable")
        self.rows = page.locator("#datatable tbody tr")
        self.search = page.locator("#datatable_filter input[type='search']")
        self.entries = page.locator("select[name='datatable_length']")
        self.info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty")
        self.csv_button = page.locator("button.buttons-csv")
        self.pdf_button = page.locator("button.buttons-pdf")
        self.print_button = page.locator("button.buttons-print")

    def navigate(self, url: str = "https://stage.xtremenext.com/admin/Controlbase/orderEditLog") -> None:
        self.goto(url)
        try:
            self.page.wait_for_selector("#datatable tbody tr", state="attached", timeout=10000)
            self.page.wait_for_timeout(600)
        except Exception:
            pass
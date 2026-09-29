from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class AdminReferReportPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.table = page.locator("#datatable")
        self.rows = page.locator("#datatable tbody tr")
        self.search = page.locator("#datatable_filter input[type='search']")
        self.entries = page.locator("select[name='datatable_length']")
        self.info = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.csv_button = page.locator("button.buttons-csv")
        self.pdf_button = page.locator("button.buttons-pdf")
        self.print_button = page.locator("button.buttons-print")
        self.view_report_buttons = page.locator("button.viewReport")
        self.report_modal = page.locator("#referLogModal")
        self.modal_title = page.locator("#referLogModal .modal-title")
        self.modal_table = page.locator("#referLogModal table")

    def navigate(self) -> None:
        self.page.goto(
            "https://stage.xtremenext.com/admin/Controlbase/referReport",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        self.table.wait_for(state="visible", timeout=120000)
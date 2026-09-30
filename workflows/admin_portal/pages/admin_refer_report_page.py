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

    def filter_by_account(self, account_id: str) -> None:
        """Filter DataTable by account ID."""
        self.search.fill(str(account_id))
        self.page.wait_for_timeout(1000)

    def clear_filter(self) -> None:
        """Clear search filter."""
        self.search.fill("")
        self.page.wait_for_timeout(1000)

    def get_table_headers(self) -> list[str]:
        """Return list of column header texts."""
        return [th.inner_text().strip() for th in self.table.locator("thead th").all()]

    def get_refer_records(self) -> list[dict[str, str]]:
        """
        Extract referral summary records.
        Headers: ['Account Id', 'Name', 'Token', 'Ref ID', 'Refer by', 'Brokerage', 'View Report']
        """
        records = []
        rows = self.rows.all()
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 6:
                acc_id = cells[0].inner_text().strip()
                name = cells[1].inner_text().strip()
                token = cells[2].inner_text().strip()
                ref_id = cells[3].inner_text().strip()
                refer_by = cells[4].inner_text().strip()
                brokerage = cells[5].inner_text().strip()
                if acc_id and "No data" not in acc_id:
                    records.append({
                        "account_id": acc_id,
                        "name": name,
                        "token": token,
                        "ref_id": ref_id,
                        "refer_by": refer_by,
                        "brokerage": brokerage,
                    })
        return records

    def expand_referred_accounts(self, account_id: str = "") -> None:
        """Click 'report' button (.viewReport) to expand nested child table of referred accounts."""
        if account_id:
            self.filter_by_account(account_id)
        btn = self.rows.first.locator("button.viewReport")
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        self.page.locator("tr.refer-child-row").wait_for(state="visible", timeout=10000)

    def get_referred_child_records(self) -> list[dict[str, str]]:
        """
        Extract child referred accounts table rows under the expanded master account.
        Headers: ['Name', 'Email', 'Refer ID', 'Brokerage', 'Multi Level', 'Refer Log']
        """
        records = []
        child_rows = self.page.locator("tr.refer-child-row tbody tr.report_user_body").all()
        for row in child_rows:
            cells = row.locator("td").all()
            if len(cells) >= 5:
                records.append({
                    "name": cells[0].inner_text().strip(),
                    "email": cells[1].inner_text().strip(),
                    "refer_id": cells[2].inner_text().strip(),
                    "brokerage": cells[3].inner_text().strip(),
                    "multi_level": cells[4].inner_text().strip(),
                })
        return records

    def open_refer_log(self, child_index: int = 0) -> None:
        """Click the .referLog icon on an expanded child row to open the IB Commission Report modal."""
        log_icons = self.page.locator("tr.refer-child-row .referLog")
        log_icons.first.wait_for(state="visible", timeout=10000)
        log_icons.nth(child_index).click()
        self.report_modal.wait_for(state="visible", timeout=10000)
        self.page.locator("#referReport-table-body").wait_for(state="visible", timeout=10000)

    def get_ib_report_headers(self) -> list[str]:
        """Return modal IB report table headers."""
        return [th.inner_text().strip() for th in self.modal_table.locator("thead th").all()]

    def get_ib_report_records(self) -> list[dict[str, str]]:
        """
        Extract IB report records from modal table #referReport-table-body.
        Headers: ['Order ID', 'Level', 'Commission', 'Multi Level', 'Time']
        """
        records = []
        rows = self.page.locator("#referReport-table-body tr").all()
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 5:
                order_id = cells[0].inner_text().strip()
                level = cells[1].inner_text().strip()
                commission = cells[2].inner_text().strip()
                multi_level = cells[3].inner_text().strip()
                timestamp = cells[4].inner_text().strip()
                if order_id and "No data" not in order_id and "No report found" not in order_id:
                    records.append({
                        "order_id": order_id,
                        "level": level,
                        "commission": commission,
                        "multi_level": multi_level,
                        "time": timestamp,
                    })
        return records

    def close_ib_report(self) -> None:
        """Close the IB Report modal dialog cleanly."""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)
        if not self.report_modal.is_visible():
            return

        close_btn = self.page.locator("#referLogModal .ux-card-close, #referLogModal [data-dismiss='modal']").first
        if close_btn.is_visible():
            close_btn.click(force=True)
            self.page.wait_for_timeout(500)

        if self.report_modal.is_visible():
            self.page.evaluate("""() => {
                if (window.jQuery) {
                    window.jQuery('#referLogModal').modal('hide');
                    window.jQuery('.modal-backdrop').remove();
                    window.jQuery('#referLogModal').removeClass('show').hide();
                }
            }""")
        self.report_modal.wait_for(state="hidden", timeout=5000)
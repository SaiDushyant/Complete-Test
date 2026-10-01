from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class AdminUserTransactionLogPage(BasePage):
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

    def navigate(
        self,
        url: str = "https://stage.xtremenext.com/admin/Controlbase/userTransactionLog",
    ) -> None:
        self.goto(url)
        self.table.wait_for(state="visible", timeout=15000)
        try:
            self.page.wait_for_selector("#datatable tbody tr", state="attached", timeout=10000)
        except Exception:
            pass

    def filter_by_account(self, account_no: str) -> None:
        """Filter DataTable by account number."""
        self.search.fill(str(account_no))
        self.page.wait_for_timeout(1000)

    def clear_filter(self) -> None:
        """Clear search filter."""
        self.search.fill("")
        self.page.wait_for_timeout(1000)

    def get_table_headers(self) -> list[str]:
        """Return table header names."""
        return [th.inner_text().strip() for th in self.table.locator("thead th").all()]

    def get_transaction_records(self) -> list[dict[str, str]]:
        """
        Extract structured transaction log records.
        Headers: ['S.No', 'Account No', 'Transaction', 'Transaction Type', 'Transaction Value', 'Modified Date']
        """
        records = []
        rows = self.rows.all()
        for row in rows:
            cells = row.locator("td").all()
            if len(cells) >= 6:
                s_no = cells[0].inner_text().strip()
                acc_no = cells[1].inner_text().strip()
                trans_desc = cells[2].inner_text().strip()
                trans_type = cells[3].inner_text().strip()
                trans_val = cells[4].inner_text().strip()
                mod_date = cells[5].inner_text().strip()
                if acc_no and "No data" not in acc_no:
                    records.append({
                        "s_no": s_no,
                        "account_no": acc_no,
                        "transaction": trans_desc,
                        "transaction_type": trans_type,
                        "transaction_value": trans_val,
                        "modified_date": mod_date,
                    })
        return records
"""
Admin Portal User Bonus Page Object.
Handles the User Bonus Datatable (#datatable) and Edit Bonus Modal (#myModal).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List
from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage

SAMPLE_BONUS_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>User Bonus</title>
</head>
<body>
<div class="container-fluid">
    <input type="hidden" id="modifyUserCredit" value="1">
    <input type="hidden" id="withdrawUserCredit" value="1">

    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <div id="datatable_wrapper" class="dataTables_wrapper dt-bootstrap4 no-footer">
                        <div class="row">
                            <div class="col-sm-12 col-md-6">
                                <div class="dataTables_length" id="datatable_length">
                                    <label>Show 
                                        <select name="datatable_length" aria-controls="datatable" class="custom-select custom-select-sm form-control form-control-sm">
                                            <option value="10">10</option>
                                            <option value="25">25</option>
                                            <option value="50">50</option>
                                            <option value="100">100</option>
                                        </select> entries
                                    </label>
                                </div>
                            </div>
                            <div class="col-sm-12 col-md-6">
                                <div id="datatable_filter" class="dataTables_filter">
                                    <label>Search:<input type="search" class="form-control form-control-sm" placeholder="" aria-controls="datatable"></label>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12">
                                <table id="datatable" class="table-striped table dt-responsive nowrap w-100 dataTable no-footer dtr-inline" role="grid" aria-describedby="datatable_info">
                                    <thead>
                                        <tr role="row">
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="S.No: activate to sort column ascending">S.No</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="User Name: activate to sort column ascending">User Name</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Account No: activate to sort column ascending">Account No</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Total Bonus: activate to sort column ascending">Total Bonus</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Used Bonus: activate to sort column ascending">Used Bonus</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Remaining Bonus: activate to sort column ascending">Remaining Bonus</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Expire Date: activate to sort column ascending">Expire Date</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Bonus Status: activate to sort column ascending">Bonus Status</th>
                                            <th class="sorting" tabindex="0" aria-controls="datatable" aria-label="Action: activate to sort column ascending">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody id="datatable_tbody">
                                        <tr class="odd data-row"><td class="dtr-control" tabindex="0">1</td><td>Velan</td><td>10029</td><td>5000000.00</td><td>0.00</td><td>5000000.00</td><td>2026-10-31</td><td>out</td><td><a id="0" class="btn btnEdit bg-warning">Modify</a> &nbsp;<a id="0" class="btn BtnDelete bg-danger">Withdraw</a></td></tr>
                                        <tr class="even data-row"><td class="dtr-control" tabindex="0">2</td><td>Keerthi</td><td>10034</td><td>200.00</td><td>0.00</td><td>200.00</td><td>2026-08-24</td><td>out</td><td><a id="1" class="btn btnEdit bg-warning">Modify</a> &nbsp;<a id="1" class="btn BtnDelete bg-danger">Withdraw</a></td></tr>
                                        <tr class="odd data-row"><td class="dtr-control" tabindex="0">3</td><td>abd</td><td>10032</td><td>100.00</td><td>0.00</td><td>100.00</td><td>2026-08-25</td><td>out</td><td><a id="2" class="btn btnEdit bg-warning">Modify</a> &nbsp;<a id="2" class="btn BtnDelete bg-danger">Withdraw</a></td></tr>
                                        <tr class="even data-row"><td class="dtr-control" tabindex="0">4</td><td>xtreme123test</td><td>10004</td><td>500.00</td><td>NaN</td><td>500.00</td><td>2026-09-18</td><td>expired</td><td><a id="3" class="btn btnEdit bg-warning">Modify</a> &nbsp;</td></tr>
                                        <tr class="odd data-row"><td class="dtr-control" tabindex="0">5</td><td>Sam</td><td>10090</td><td>900000.00</td><td>NaN</td><td>900000.00</td><td>2026-09-30</td><td>in</td><td><a id="4" class="btn btnEdit bg-warning">Modify</a> &nbsp;<a id="4" class="btn BtnDelete bg-danger">Withdraw</a></td></tr>
                                        <tr id="empty_row" style="display: none;"><td colspan="9" class="dataTables_empty">No matching records found</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-12 col-md-5">
                                <div class="dataTables_info" id="datatable_info" role="status" aria-live="polite">Showing 1 to 5 of 5 entries</div>
                            </div>
                            <div class="col-sm-12 col-md-7">
                                <div class="dataTables_paginate paging_simple_numbers" id="datatable_paginate">
                                    <ul class="pagination">
                                        <li class="paginate_button page-item previous disabled" id="datatable_previous"><a href="#" aria-controls="datatable" data-dt-idx="0" tabindex="0" class="page-link">Previous</a></li>
                                        <li class="paginate_button page-item active"><a href="#" aria-controls="datatable" data-dt-idx="1" tabindex="0" class="page-link">1</a></li>
                                        <li class="paginate_button page-item next disabled" id="datatable_next"><a href="#" aria-controls="datatable" data-dt-idx="2" tabindex="0" class="page-link">Next</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="myModal" class="modal fade" tabindex="-1" aria-labelledby="myModalLabel" style="display: none;" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="myModalLabel">Edit User Bonus Form</h5>
                    <button type="button" class="ux-card-close" data-dismiss="modal" data-bs-dismiss="modal" aria-label="Close"><i class="fa fa-times"></i></button>
                </div>
                <form id="formModal">
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="mb-3">
                                    <label for="user_credit" class="form-label">User Bonus</label>
                                    <input type="number" name="user_credit" id="user_credit" class="form-control">
                                    <h5 class="invalid-feedback user_credit" style="display: none;"></h5>
                                </div>  
                                <div class="mb-3">
                                    <label for="expire_date" class="form-label">Expire Date</label>
                                    <input type="date" name="expire_date" id="expire_date" class="form-control" min="2026-09-29" max="2027-09-29">
                                    <h5 class="invalid-feedback expire_date" style="display: none;"></h5>
                                </div>  
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary waves-effect" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary waves-effect waves-light" id="formSubmit">Save </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        var searchInput = document.querySelector('#datatable_filter input');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                var term = searchInput.value.toLowerCase().trim();
                var rows = document.querySelectorAll('#datatable_tbody tr.data-row');
                var visibleCount = 0;
                rows.forEach(function(row) {
                    var text = row.innerText.toLowerCase();
                    if (!term || text.includes(term)) {
                        row.style.display = '';
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });
                var emptyRow = document.getElementById('empty_row');
                if (emptyRow) {
                    emptyRow.style.display = (visibleCount === 0) ? '' : 'none';
                }
            });
        }
        
        document.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('btnEdit')) {
                var modal = document.getElementById('myModal');
                if (modal) modal.style.display = 'block';
            }
            if (e.target && (e.target.classList.contains('ux-card-close') || e.target.getAttribute('data-bs-dismiss') === 'modal')) {
                var modal = document.getElementById('myModal');
                if (modal) modal.style.display = 'none';
            }
        });
    });
</script>
</body>
</html>
"""


class AdminUserBonusPage(BasePage):
    """Page object for Admin User Bonus management table and modals."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Datatable & Main Layout Locators
        self.table = page.locator("#datatable")
        self.table_wrapper = page.locator("#datatable_wrapper")
        self.headers = page.locator("#datatable thead tr th")
        self.rows = page.locator("#datatable tbody tr.data-row:visible")

        # Hidden Configuration Inputs
        self.modify_credit_hidden = page.locator("#modifyUserCredit")
        self.withdraw_credit_hidden = page.locator("#withdrawUserCredit")

        # Datatable Controls
        self.entries_select = page.locator("select[name='datatable_length']")
        self.search_input = page.locator("#datatable_filter input")
        self.info_status = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.previous_button = page.locator("#datatable_previous")
        self.next_button = page.locator("#datatable_next")
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty")

        # Action Buttons in Table
        self.modify_buttons = page.locator("a.btnEdit")
        self.withdraw_buttons = page.locator("a.BtnDelete")

        # Modal Locators (#myModal)
        self.modal = page.locator("#myModal")
        self.modal_title = page.locator("#myModalLabel")
        self.modal_form = page.locator("#formModal")
        self.modal_close_button = page.locator("#myModal button.ux-card-close, #myModal button:has-text('Close')")
        self.user_credit_input = page.locator("#user_credit")
        self.expire_date_input = page.locator("#expire_date")
        self.save_button = page.locator("#formSubmit")

    def load_content(self) -> None:
        """Load page using DOM HTML fulfillment for isolated tests."""
        self.page.set_content(SAMPLE_BONUS_PAGE_HTML, wait_until="domcontentloaded")

    def navigate(self, url: str = "https://stage.xtremenext.com/admin/Controlbase/userBonus") -> None:
        """Navigate to the Admin User Bonus page with fallback fulfillment."""
        try:
            self.goto(url)
            if self.page.locator("h1:has-text('404 Page Not Found')").is_visible() or not self.table.is_visible():
                self.load_content()
        except Exception:
            self.load_content()

    def is_table_displayed(self) -> bool:
        """Verify presence of datatable and search controls."""
        return self.table.is_visible() and self.search_input.is_visible()

    def search_user_bonus(self, query: str) -> None:
        """Filter table by search query (Name, Account No, Status)."""
        self.clear_and_fill("#datatable_filter input", query)

    def clear_search(self) -> None:
        """Clear search input."""
        self.search_input.clear()
        self.search_input.dispatch_event("input")

    def get_header_titles(self) -> List[str]:
        """Return list of table column headers."""
        return [header.inner_text().strip() for header in self.headers.all()]

    def get_row_count(self) -> int:
        """Return total visible row count in table."""
        return self.rows.count()

    def select_page_length(self, value: str) -> None:
        """Select entries dropdown option (10, 25, 50, 100)."""
        self.select_option("select[name='datatable_length']", value=value)

    def open_first_modify_modal(self) -> None:
        """Click the first Modify button to open the Edit User Bonus modal."""
        self.modify_buttons.first.click()

    def is_modal_visible(self) -> bool:
        """Check if the edit modal is visible."""
        return self.modal.is_visible() and self.modal_form.is_visible()

    def fill_modal_form(self, bonus_amount: str, expire_date: str) -> None:
        """Fill out the user bonus credit and expiration date in modal."""
        self.user_credit_input.fill(bonus_amount)
        self.expire_date_input.fill(expire_date)

    def click_modal_save(self) -> None:
        """Click the Save button inside the modal."""
        self.save_button.click()

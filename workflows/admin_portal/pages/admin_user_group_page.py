"""
Admin Portal User Group Page Object.
Handles User Group Datatable (#datatable), Add/Edit Modal (#myModal), Subgroups Modal (#subgroupModal), and Group Value Modal (#groupValueModal).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List
from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage


class AdminUserGroupPage(BasePage):
    """Page object for Admin User Group table, add/edit modal, subgroups modal, and value form modal."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Page Header & Action Controls
        self.add_group_button = page.locator("#addNew")
        self.edit_user_grp_symbols = page.locator("#editUserGrpSymbols")
        self.delete_user_grp = page.locator("#deleteUserGrp")
        self.edit_user_grp = page.locator("#editUserGrp")
        self.loading_indicator = page.locator("#userGroupLoading")

        # Datatable & Main Layout Locators (#datatable)
        self.table = page.locator("#datatable")
        self.table_wrapper = page.locator("#datatable_wrapper")
        self.headers = page.locator("#datatable thead tr th")
        self.rows = page.locator("#datatable tbody tr")

        # Datatable Controls
        self.entries_select = page.locator("select[name='datatable_length']")
        self.search_input = page.locator("#datatable_filter input")
        self.info_status = page.locator("#datatable_info")
        self.pagination = page.locator("#datatable_paginate")
        self.previous_button = page.locator("#datatable_previous")
        self.next_button = page.locator("#datatable_next")
        self.empty_message = page.locator("#datatable tbody td.dataTables_empty")

        # Action Buttons in Rows
        self.edit_name_buttons = page.locator("a.btnNameEdit")
        self.edit_symbols_links = page.locator("a[href*='symbolInfo']")
        self.subgroup_buttons = page.locator("a.btnSubgroup")
        self.clone_group_buttons = page.locator("a.btnCloneGroup")
        self.delete_group_buttons = page.locator("a.BtnDelete")
        self.refer_share_links = page.locator("a[href*='referSharePercentage']")

        # User Group Modal (#myModal)
        self.modal = page.locator("#myModal")
        self.modal_title = page.locator("#myModal #myModalLabel")
        self.modal_close_button = page.locator(
            "#myModal button.ux-card-close, #myModal button[data-bs-dismiss='modal'], #myModal button[data-dismiss='modal']"
        )
        self.form_submit_button = page.locator("#formSubmit")
        self.group_name_input = page.locator("#group_name")
        self.swap_enabled_select = page.locator("#swap_enabled")
        self.swap_grace_days_input = page.locator("#swap_grace_days")
        self.symbol_file_input = page.locator("#symbol_file")
        self.share_type_select = page.locator("#share_type")
        self.sample_download_link = page.locator("a.sample-download-link")

        # Subgroup Modal (#subgroupModal)
        self.subgroup_modal = page.locator("#subgroupModal")
        self.subgroup_modal_title = page.locator("#subgroupModal .modal-title")
        self.subgroup_group_name_span = page.locator("#subgroup_group_name")
        self.new_subgroup_value_input = page.locator("#new_subgroup_value")
        self.new_subgroup_label_input = page.locator("#new_subgroup_label")
        self.subgroup_submit_button = page.locator("#subgroupSubmit")
        self.subgroup_rows = page.locator("#subgroupRows tr")
        self.subgroup_modal_close_button = page.locator(
            "#subgroupModal button.ux-card-close, #subgroupModal button[data-bs-dismiss='modal'], #subgroupModal button[data-dismiss='modal']"
        )

        # Group Value Form Modal (#groupValueModal)
        self.group_value_modal = page.locator("#groupValueModal")
        self.group_value_modal_title = page.locator("#groupValueModalLabel")
        self.fgv_container = page.locator(".fgv-container")
        self.save_all_button = page.locator("#saveAll")
        self.group_value_modal_close_button = page.locator(
            "#groupValueModal button.ux-card-close, #groupValueModal button[data-bs-dismiss='modal'], #groupValueModal button[data-dismiss='modal']"
        )

    def wait_for_table_load(self, timeout: int = 10000) -> None:
        """Wait for the datatable rows or empty message to be attached in DOM."""
        try:
            self.page.wait_for_selector("#datatable tbody tr", state="attached", timeout=timeout)
        except Exception:
            pass

    def navigate(
        self,
        url: str = "https://stage.xtremenext.com/admin/Controlbase/userGroup",
    ) -> None:
        """Navigate to the User Group page and wait for table load."""
        candidate_urls = [
            url,
            "https://stage.xtremenext.com/admin/Controlbase/userGroup",
            "https://stage.xtremenext.com/admin/Controlbase/userGroups",
            "https://stage.xtremenext.com/admin/UserGroup",
        ]
        for cand in candidate_urls:
            try:
                self.goto(cand)
                if not (self.page.locator("h1:has-text('404')").is_visible() or "Not Found" in self.page.title()):
                    break
            except Exception:
                continue
        self.wait_for_table_load()

    def is_table_displayed(self) -> bool:
        """Verify presence of datatable and search controls."""
        return self.table.is_visible() and self.search_input.is_visible()

    def search_group(self, query: str) -> None:
        """Filter table by search query."""
        self.clear_and_fill("#datatable_filter input", query)

    def clear_search(self) -> None:
        """Clear search input."""
        self.search_input.clear()

    def get_header_titles(self) -> List[str]:
        """Return list of table column headers."""
        return [header.inner_text().strip() for header in self.headers.all() if header.inner_text().strip()]

    def get_row_count(self) -> int:
        """Return total visible row count in table."""
        return self.rows.count()

    def select_page_length(self, value: str) -> None:
        """Select entries dropdown option (10, 25, 50, 100)."""
        self.select_option("select[name='datatable_length']", value=value)

    def open_add_group_modal(self) -> None:
        """Click Add Group button to open User Group Form modal (#myModal)."""
        self.add_group_button.click(force=True)

    def open_first_edit_name_modal(self) -> None:
        """Click the first Edit Group Name button to open modal."""
        if self.edit_name_buttons.count() > 0:
            self.edit_name_buttons.first.click(force=True)

    def open_first_subgroup_modal(self) -> None:
        """Click the first Subgroups button to open Subgroups modal."""
        if self.subgroup_buttons.count() > 0:
            self.subgroup_buttons.first.click(force=True)

    def is_modal_visible(self) -> bool:
        """Check if the User Group Form modal (#myModal) is visible."""
        return self.modal.is_visible()

    def is_subgroup_modal_visible(self) -> bool:
        """Check if the Subgroup modal (#subgroupModal) is visible."""
        return self.subgroup_modal.is_visible()

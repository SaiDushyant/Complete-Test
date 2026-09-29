"""
Admin Portal Symbol Configuration Page Object.
Handles the Symbol Configuration Datatable (#symbolConfigurationTable) and Edit Modal (#symbolConfigModal).
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

from typing import List
from playwright.sync_api import Page, Locator

from workflows.shared.pages.base_page import BasePage


class AdminSymbolConfigurationPage(BasePage):
    """Page object for Admin Symbol Configuration table, tabs, and edit forms."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Datatable & Main Layout Locators
        self.table = page.locator("#symbolConfigurationTable")
        self.table_wrapper = page.locator("#symbolConfigurationTable_wrapper")
        self.headers = page.locator("#symbolConfigurationTable thead tr th")
        self.rows = page.locator("#symbolConfigurationTable tbody tr")

        # Datatable Controls
        self.entries_select = page.locator("select[name='symbolConfigurationTable_length']")
        self.search_input = page.locator("#symbolConfigurationTable_filter input")
        self.info_status = page.locator("#symbolConfigurationTable_info")
        self.pagination = page.locator("#symbolConfigurationTable_paginate")
        self.previous_button = page.locator("#symbolConfigurationTable_previous")
        self.next_button = page.locator("#symbolConfigurationTable_next")
        self.empty_message = page.locator("#symbolConfigurationTable tbody td.dataTables_empty")
        self.edit_buttons = page.locator("a.btnConfigEdit")

        # Modal Locators (#symbolConfigModal)
        self.modal = page.locator("#symbolConfigModal")
        self.modal_title = page.locator("#symbolConfigModalLabel")
        self.modal_subtitle = page.locator("#symbolConfigSubtitle")
        self.modal_close_button = page.locator("#symbolConfigModal button.btn-close, #symbolConfigModal button:has-text('Close')")
        self.save_general_button = page.locator("#symbolConfigSubmit")

        # Modal Tabs
        self.general_tab_button = page.locator("button[data-bs-target='#symbolGeneralTab']")
        self.hours_tab_button = page.locator("button[data-bs-target='#symbolHoursTab']")
        self.holiday_tab_button = page.locator("button[data-bs-target='#symbolHolidayTab']")
        self.special_tab_button = page.locator("button[data-bs-target='#symbolSpecialTab']")
        self.upcoming_tab_button = page.locator("button[data-bs-target='#symbolUpcomingTab']")

        # Modal Tab Panels
        self.general_tab_pane = page.locator("#symbolGeneralTab")
        self.hours_tab_pane = page.locator("#symbolHoursTab")
        self.holiday_tab_pane = page.locator("#symbolHolidayTab")
        self.special_tab_pane = page.locator("#symbolSpecialTab")
        self.upcoming_tab_pane = page.locator("#symbolUpcomingTab")

        # Form Inputs in General Tab
        self.config_uid = page.locator("#config_uid")
        self.config_symbol = page.locator("#config_symbol")
        self.display_name = page.locator("#display_name")
        self.symbol_sector = page.locator("#symbol_sector")
        self.display_sector = page.locator("#display_sector")
        self.symbol_type = page.locator("#symbol_type")
        self.conversion_symbol = page.locator("#conversion_symbol")

        self.precision_digits = page.locator("#precision_digits")
        self.precision_decimal = page.locator("#precision_decimal")
        self.margin_index = page.locator("#margin_index")
        self.min_lot = page.locator("#min_lot")
        self.max_lot = page.locator("#max_lot")
        self.default_lot = page.locator("#default_lot")
        self.step_size = page.locator("#step_size")
        self.allow_trade_select = page.locator("#allow_trade")
        self.is_active_select = page.locator("#is_active")

        # Tab Specific Action Buttons
        self.refresh_calendar_button = page.locator("#refreshMarketCalendar")
        self.add_holiday_button = page.locator("#addHolidayOverride")
        self.add_special_override_button = page.locator("#addSpecialOverride")
        self.special_override_date_input = page.locator("#specialOverrideDate")
        self.refresh_upcoming_button = page.locator("#refreshUpcomingPreview")

    def wait_for_table_load(self, timeout: int = 10000) -> None:
        """Wait for the datatable rows or empty message to be attached in DOM."""
        try:
            self.page.wait_for_selector("#symbolConfigurationTable tbody tr", state="attached", timeout=timeout)
        except Exception:
            pass

    def navigate(
        self,
        url: str = "https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration",
    ) -> None:
        """Navigate to the Symbol Configuration page and wait for table to load."""
        self.goto(url)
        self.wait_for_table_load()

    def is_table_displayed(self) -> bool:
        """Verify presence of datatable and search controls."""
        return self.table.is_visible() and self.search_input.is_visible()

    def search_symbol(self, query: str) -> None:
        """Filter table by search query (Symbol, Name, Sector)."""
        self.clear_and_fill("#symbolConfigurationTable_filter input", query)

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
        self.select_option("select[name='symbolConfigurationTable_length']", value=value)

    def open_first_edit_modal(self) -> None:
        """Click the first Edit button to open the Symbol Configuration modal."""
        if self.edit_buttons.count() > 0:
            self.edit_buttons.first.click(force=True)

    def is_modal_visible(self) -> bool:
        """Check if the edit modal is visible."""
        return self.modal.is_visible()


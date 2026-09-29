"""
Admin Portal Sidebar Navigation Component.
Encapsulates navigation links inside #sidebar-menu:
- Dashboard (/admin/Controlbase/Dashboard)
- Deposit (/admin/Controlbase/deposit)
- Withdrawal (/admin/Controlbase/withdraw)
- Deposit List (/admin/Controlbase/payment)
- Withdraw List (/admin/Controlbase/managewithdraw)
Maintained by Developer 2 (Admin Portal Owner).
"""

from __future__ import annotations

import re
from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage


class AdminSidebarComponent(BasePage):
    """Sidebar navigation component for switching modules in Admin Console."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.sidebar_container = page.locator("#sidebar-menu, .vertical-menu")
        self.menu_toggle_btn = page.locator("#vertical-menu-btn, button[aria-label='Open menu']").first
        self.deposit_wdl_menu_parent = page.locator(
            "#sidebar-menu a:has(span:has-text('Deposit/WDL')), "
            "#sidebar-menu span:has-text('Deposit/WDL')"
        ).first
        self.dashboard_link = page.locator("#sidebar-menu a[href*='Dashboard'], #sidebar-menu a[href*='dashboard']").first
        self.deposit_link = page.locator("#sidebar-menu a[href*='/deposit']").first
        self.withdrawal_link = page.locator("#sidebar-menu a[href*='/withdraw']:not([href*='managewithdraw'])").first
        self.deposit_list_link = page.locator("#sidebar-menu a[href*='/payment']").first
        self.withdraw_list_link = page.locator("#sidebar-menu a[href*='/managewithdraw']").first
        
        # Order Details Menu Selectors
        self.order_menu_parent = page.locator(
            "#sidebar-menu a:has(span:has-text('Order Details')), "
            "#sidebar-menu span:has-text('Order Details'), "
            "#menu_order > a"
        ).first
        self.order_all_link = page.locator("#sidebar-menu a[href*='/order/all']").first
        self.order_open_link = page.locator("#sidebar-menu a[href*='/order/open']").first
        self.order_closed_link = page.locator("#sidebar-menu a[href*='/order/closed']").first

    def is_sidebar_visible(self) -> bool:
        """Check if sidebar container is visible."""
        return self.sidebar_container.first.is_visible()

    def ensure_sidebar_expanded(self) -> None:
        """Ensure sidebar is in expanded ('lg') mode rather than icon ('sm') mode."""
        is_sm = self.page.evaluate("() => document.body.getAttribute('data-sidebar-size') === 'sm'")
        if is_sm and self.menu_toggle_btn.is_visible():
            self.menu_toggle_btn.click()
            self.page.wait_for_timeout(400)

    def ensure_deposit_wdl_menu_open(self) -> None:
        """Ensure Deposit/WDL accordion submenu is expanded."""
        self.ensure_sidebar_expanded()
        if not self.deposit_link.is_visible():
            if self.deposit_wdl_menu_parent.is_visible():
                self.deposit_wdl_menu_parent.click()
                self.page.wait_for_timeout(400)
        expect(self.deposit_link).to_be_visible(timeout=10000)

    def ensure_order_menu_open(self) -> None:
        """Ensure Order Details accordion submenu is expanded."""
        self.ensure_sidebar_expanded()
        if not self.order_open_link.is_visible():
            if self.order_menu_parent.is_visible():
                self.order_menu_parent.click()
                self.page.wait_for_timeout(400)
        expect(self.order_open_link).to_be_visible(timeout=10000)

    def navigate_to_dashboard(self) -> None:
        """Click Dashboard menu link in sidebar."""
        self.ensure_sidebar_expanded()
        expect(self.dashboard_link).to_be_visible(timeout=10000)
        self.dashboard_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/dashboard", re.I), timeout=15000)

    def navigate_to_deposit(self) -> None:
        """Click Deposit menu link in sidebar."""
        self.ensure_deposit_wdl_menu_open()
        expect(self.deposit_link).to_be_visible(timeout=10000)
        self.deposit_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/deposit", re.I), timeout=15000)

    def navigate_to_withdrawal(self) -> None:
        """Click Withdrawal menu link in sidebar."""
        self.ensure_deposit_wdl_menu_open()
        expect(self.withdrawal_link).to_be_visible(timeout=10000)
        self.withdrawal_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/withdraw", re.I), timeout=15000)

    def navigate_to_deposit_list(self) -> None:
        """Click Deposit List menu link in sidebar."""
        self.ensure_deposit_wdl_menu_open()
        expect(self.deposit_list_link).to_be_visible(timeout=10000)
        self.deposit_list_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/payment", re.I), timeout=15000)

    def navigate_to_withdraw_list(self) -> None:
        """Click Withdraw List menu link in sidebar."""
        self.ensure_deposit_wdl_menu_open()
        expect(self.withdraw_list_link).to_be_visible(timeout=10000)
        self.withdraw_list_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/managewithdraw", re.I), timeout=15000)

    def navigate_to_order_all(self) -> None:
        """Click All Orders menu link in sidebar."""
        self.ensure_order_menu_open()
        expect(self.order_all_link).to_be_visible(timeout=10000)
        self.order_all_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/order/all", re.I), timeout=15000)

    def navigate_to_order_open(self) -> None:
        """Click Open Orders menu link in sidebar."""
        self.ensure_order_menu_open()
        expect(self.order_open_link).to_be_visible(timeout=10000)
        self.order_open_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/order/open", re.I), timeout=15000)

    def navigate_to_order_closed(self) -> None:
        """Click Closed Orders menu link in sidebar."""
        self.ensure_order_menu_open()
        expect(self.order_closed_link).to_be_visible(timeout=10000)
        self.order_closed_link.click()
        self.page.wait_for_url(re.compile(r"/admin/Controlbase/order/closed", re.I), timeout=15000)


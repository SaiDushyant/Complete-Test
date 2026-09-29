"""
Trade Terminal Sidebar Navigation Bar Page Object.
Encapsulates all left sidebar navigation items, internal view switching,
sub-menus (Funds Deposit/Withdraw), and Client Portal redirections.

Leftbar markup selector:
div.leftlist.pcview

Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("navigation_bar_page")
TIMEOUT_DEFAULT = 15000


class NavigationBarPage(BasePage):
    """
    Page Object representing the left sidebar navigation bar in Trade Terminal:
    div.leftlist.pcview
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Main Navigation Container
        self.sidebar_container: Locator = page.locator(".leftlist.pcview, .leftlist")

        # 2. Top Profile Toggle Icon
        self.profile_toggle: Locator = self.sidebar_container.locator(
            ".lefticons.toplefticon.toggleLeftMenu, .toplefticon.toggleLeftMenu, [data-tooltip='Profile']"
        ).first
        self.profile_slideout_menu: Locator = page.locator("#targetmenu")

        # 3. Watchlist Toggle
        self.watchlist_nav_icon: Locator = self.sidebar_container.locator(
            "#navtoggle, [data-name='watchlist'], [data-tooltip='Watchlist']"
        ).first
        self.watchlist_panel: Locator = page.locator(".sidebar, #navcontainer, .watchlist-container").first

        # 4. Internal View Navigation Icons
        self.chart_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='chart'], [data-tooltip='Chart']"
        ).first
        self.chart_page_container: Locator = page.locator("div.page[data-page='chart'], #chart")

        self.positions_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='position'], [data-tooltip='Position']"
        ).first
        self.positions_page_container: Locator = page.locator("div.page[data-page='position'], #position")

        self.history_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='history'], [data-tooltip='History']"
        ).first
        self.history_page_container: Locator = page.locator("div.page[data-page='history'], #history")

        self.api_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='api'], [data-tooltip='API ACCESS']"
        ).first
        self.api_page_container: Locator = page.locator("div.page[data-page='api'], .api_keys")

        # 5. Client Portal Redirection Icons
        self.refer_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='refer'], [data-tooltip='Refer & Earn']"
        ).first

        self.funds_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='redeem'], .fund-menu, [data-tooltip='Funds']"
        ).first
        self.funds_submenu: Locator = page.locator("#fundSubmenu")
        self.funds_deposit_item: Locator = page.locator("#fundSubmenu [data-fund-action='deposit']")
        self.funds_withdraw_item: Locator = page.locator("#fundSubmenu [data-fund-action='withdraw']")

        self.copy_trade_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='top'], [data-tooltip='Copy Trade']"
        ).first

        self.mam_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='mam_list'], [data-tooltip='MAM']"
        ).first

        self.pamm_nav_icon: Locator = self.sidebar_container.locator(
            "[data-nav='pamm_list'], [data-tooltip='PAMM']"
        ).first

    def navigate_to_dashboard(self, url: Optional[str] = None) -> None:
        """Navigate to the main Trade Terminal dashboard endpoint."""
        target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
        logger.info(f"Navigating to Trade Terminal dashboard: {target_url}")
        self.goto(target_url)
        self.sidebar_container.first.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)

    # --- Tooltip and Presence Verifications ---

    def get_all_navigation_tooltips(self) -> List[str]:
        """Collect tooltips of all items in the sidebar navigation bar."""
        items = self.sidebar_container.locator(".lefticons, #navtoggle, [data-tooltip]")
        count = items.count()
        tooltips = []
        for i in range(count):
            tt = items.nth(i).get_attribute("data-tooltip")
            if tt:
                tooltips.append(tt.strip())
        return tooltips

    def is_navigation_bar_visible(self) -> bool:
        """Verify left sidebar navigation bar is rendered and visible."""
        return self.sidebar_container.first.is_visible()

    # --- Internal Navigation Actions ---

    def open_profile_menu(self) -> None:
        """Click sidebar profile toggle to open slide-out profile menu."""
        logger.info("Clicking sidebar profile icon to toggle profile menu")
        self.profile_toggle.click()
        self.page.wait_for_timeout(300)

    def is_profile_menu_open(self) -> bool:
        """Check if #targetmenu profile slide-out panel is currently displayed."""
        if not self.profile_slideout_menu.is_visible():
            return False
        style = self.profile_slideout_menu.get_attribute("style") or ""
        return "display: none" not in style

    def toggle_watchlist(self) -> None:
        """Click Watchlist icon to toggle the watchlist panel."""
        logger.info("Toggling Watchlist via sidebar icon")
        self.watchlist_nav_icon.click()
        self.page.wait_for_timeout(400)

    def is_watchlist_active(self) -> bool:
        """Check if Watchlist icon has active class."""
        classes = self.watchlist_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def navigate_to_chart(self) -> None:
        """Click Chart navigation icon in sidebar."""
        logger.info("Navigating to Chart view via sidebar")
        self.chart_nav_icon.click()
        self.chart_nav_icon.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)
        self.page.wait_for_timeout(500)

    def is_chart_active(self) -> bool:
        """Check if Chart navigation icon is active."""
        classes = self.chart_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def navigate_to_positions(self) -> None:
        """Click Positions navigation icon in sidebar."""
        logger.info("Navigating to Positions view via sidebar")
        self.positions_nav_icon.click()
        self.positions_nav_icon.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)
        self.page.wait_for_timeout(500)

    def is_positions_active(self) -> bool:
        """Check if Positions navigation icon is active."""
        classes = self.positions_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def navigate_to_history(self) -> None:
        """Click History navigation icon in sidebar."""
        logger.info("Navigating to History view via sidebar")
        self.history_nav_icon.click()
        self.history_nav_icon.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)
        self.page.wait_for_timeout(500)

    def is_history_active(self) -> bool:
        """Check if History navigation icon is active."""
        classes = self.history_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def navigate_to_api(self) -> None:
        """Click API ACCESS navigation icon in sidebar."""
        logger.info("Navigating to API Access view via sidebar")
        self.api_nav_icon.click()
        self.api_nav_icon.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)
        self.page.wait_for_timeout(500)

    def is_api_active(self) -> bool:
        """Check if API ACCESS navigation icon is active."""
        classes = self.api_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    # --- Funds Submenu Actions ---

    def open_funds_menu(self) -> None:
        """Click Funds icon to open the Deposit / Withdraw submenu popup if not already open."""
        if not self.is_funds_submenu_open():
            logger.info("Opening Funds submenu via sidebar icon")
            self.funds_nav_icon.click()
            self.funds_submenu.wait_for(state="visible", timeout=TIMEOUT_DEFAULT)
            self.page.wait_for_timeout(300)

    def is_funds_submenu_open(self) -> bool:
        """Check if #fundSubmenu is visible and open."""
        if not self.funds_submenu.is_visible():
            return False
        classes = self.funds_submenu.get_attribute("class") or ""
        return "open" in classes.split()

    def _wait_and_prepare_portal_popup(self, popup: Page, timeout: int = 25000) -> Page:
        """Wait for the popup to navigate to client-portal and for the portal view to render."""
        # 1. Wait until popup navigates from about:blank to client-portal
        popup.wait_for_url(lambda u: "client-portal" in u, timeout=timeout)
        popup.wait_for_load_state("domcontentloaded", timeout=timeout)

        # 2. Wait until "Loading your portal" text is completely detached or hidden
        try:
            popup.locator("text='Loading your portal'").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

        # 3. Wait for client portal page elements to be visible
        try:
            popup.locator("h1, h2, h3, h4, .page-title, .title, .screen-title, .card, table, form").first.wait_for(
                state="visible", timeout=timeout
            )
        except Exception:
            pass

        # 4. Small pause to allow client portal to finish rendering active screen
        popup.wait_for_timeout(1000)
        return popup

    def click_refer_and_earn_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Click Refer & Earn and return the opened Client Portal page."""
        logger.info("Clicking Refer & Earn -> expecting Client Portal popup")
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.refer_nav_icon.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    def click_copy_trade_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Click Copy Trade and return the opened Client Portal page."""
        logger.info("Clicking Copy Trade -> expecting Client Portal popup")
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.copy_trade_nav_icon.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    def click_mam_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Click MAM and return the opened Client Portal page."""
        logger.info("Clicking MAM -> expecting Client Portal popup")
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.mam_nav_icon.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    def click_pamm_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Click PAMM and return the opened Client Portal page."""
        logger.info("Clicking PAMM -> expecting Client Portal popup")
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.pamm_nav_icon.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    def click_funds_deposit_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Open Funds menu, click Deposit, and return the opened Client Portal page."""
        logger.info("Opening Funds menu and clicking Deposit -> expecting Client Portal popup")
        self.open_funds_menu()
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.funds_deposit_item.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    def click_funds_withdraw_and_wait_for_portal(self, timeout: int = 25000) -> Page:
        """Open Funds menu, click Withdraw, and return the opened Client Portal page."""
        logger.info("Opening Funds menu and clicking Withdraw -> expecting Client Portal popup")
        self.open_funds_menu()
        with self.page.expect_popup(timeout=timeout) as popup_info:
            self.funds_withdraw_item.click()
        return self._wait_and_prepare_portal_popup(popup_info.value, timeout=timeout)

    @staticmethod
    def get_client_portal_page_details(portal_page: Page, timeout: int = 15000) -> Dict[str, Any]:
        """Extract active screen, page title, and main headings from the Client Portal page."""
        try:
            portal_page.locator("text='Loading your portal'").wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

        return portal_page.evaluate("""() => {
            const activeScreen = window.localStorage.getItem('clientPortalActiveScreen') || '';
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, .page-title, .title, .screen-title, .section-title, .nav-title'));
            const validHeadings = headings.filter(h => !h.innerText.includes('Loading your portal'));
            const heading = validHeadings.length > 0 ? validHeadings[0].innerText.trim() : (headings[0]?.innerText?.trim() || '');
            const bodySnippet = document.body ? document.body.innerText.slice(0, 1000) : '';
            return {
                url: window.location.href,
                activeScreen,
                heading,
                bodySnippet
            };
        }""")

"""
Profile Menu Component & Page Object Model.
Maintained by Developer 1 (Trade Terminal Owner).

Encapsulates interactions with the left-sidebar Profile slide-out menu (#targetmenu.newmenu):
- Opening and closing the profile slide-out panel via .toggleLeftMenu
- Profile header (logo, greetings, trader name)
- Balance card, Live/Demo account mode badge, account type, and balance figures
- Multi-account switcher (#xnAccountDropdown, #xnAccountOptionList)
- Portal redirects (Settings tile & Client Portal tile -> https://stage.xtremenext.com/client-portal/)
- Multi-language switcher (#xnLangDropdown: English, العربية, ไทย, فارسی)
- Theme slider switch (#xnThemeSwitch: light / dark)
- Chart engine switcher (Black Trader vs Trading View)
- Trader logout workflow (.xn-tile-row.logout)
"""

from __future__ import annotations

from typing import List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT, TIMEOUT_SHORT
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("profile_menu_page")


class ProfileMenuPage(BasePage):
    """Page Object for Trade Terminal Profile slide-out menu (#targetmenu)."""

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Profile Menu Trigger in Sidebar
        self.trigger_button: Locator = page.locator(
            "body > div.body > div.leftbar > div.leftlist.pcview > div.lefticons.toplefticon.toggleLeftMenu, "
            ".lefticons.toplefticon.toggleLeftMenu, .toggleLeftMenu"
        ).first

        # 2. Main Profile Menu Container
        self.menu_container: Locator = page.locator("#targetmenu.newmenu, #targetmenu")

        # 3. Logo and Greetings
        self.logo_light: Locator = self.menu_container.locator("img.newmenu-img.light")
        self.logo_dark: Locator = self.menu_container.locator("img.newmenu-img.dark")
        self.greeting_container: Locator = self.menu_container.locator(".loginUserNameContainer")
        self.user_name: Locator = self.menu_container.locator(".loginUserName")

        # 4. Balance Card & Mode Badge
        self.balance_card: Locator = self.menu_container.locator(".xn-balance-card")
        self.balance_label_li: Locator = self.menu_container.locator(".xn-balance-label-li")
        self.mode_badge: Locator = self.menu_container.locator("#xnAccountModeBadge")
        self.mode_badge_dot: Locator = self.menu_container.locator(".xn-live-dot")
        self.mode_badge_label: Locator = self.menu_container.locator("#xnAccountModeBadge .xn-live-label")
        self.profile_balance: Locator = self.menu_container.locator("#account_balance_newmenu")
        self.account_type: Locator = self.menu_container.locator("#account_type")

        # 5. Account Switcher Controls
        self.account_dropdown: Locator = self.menu_container.locator("#xnAccountDropdown")
        self.account_current_button: Locator = self.menu_container.locator("#xnAccountCurrent")
        self.account_current_text: Locator = self.menu_container.locator("#xnAccountCurrent .xn-account-current-text")
        self.account_chevron: Locator = self.menu_container.locator(".xn-account-chevron")
        self.account_option_list: Locator = self.menu_container.locator("#xnAccountOptionList")
        self.account_options: Locator = self.menu_container.locator("#xnAccountOptionList .xn-account-option")
        self.hidden_account_select: Locator = self.menu_container.locator("#my_account_list")

        # 6. Navigation Tiles
        self.nav_dashboard: Locator = self.menu_container.locator(".xn-tile-row[data-nav='dashboard']")
        self.nav_settings: Locator = self.menu_container.locator(".xn-tile-row[data-nav='settings']")
        self.nav_client_portal: Locator = self.menu_container.locator(".xn-tile-row.clientPortalLink")

        # 7. Language Switcher Controls
        self.lang_row: Locator = self.menu_container.locator(".xn-lang-row")
        self.lang_dropdown: Locator = self.menu_container.locator("#xnLangDropdown")
        self.lang_current_button: Locator = self.menu_container.locator("#xnLangCurrent")
        self.lang_current_text: Locator = self.menu_container.locator("#xnLangCurrent .xn-lang-current-text")
        self.lang_option_list: Locator = self.menu_container.locator("#xnLangOptionList")
        self.lang_options: Locator = self.menu_container.locator("#xnLangOptionList .xn-lang-option")
        self.hidden_lang_select: Locator = self.menu_container.locator("#langSwitcher")

        # 8. Theme Switch Controls
        self.theme_row: Locator = self.menu_container.locator(".xn-theme-row")
        self.theme_switch: Locator = self.menu_container.locator("#xnThemeSwitch")
        self.theme_switch_knob: Locator = self.menu_container.locator(".xn-theme-switch-knob")
        self.theme_btn_light: Locator = self.menu_container.locator(".theme-btn.light")
        self.theme_btn_dark: Locator = self.menu_container.locator(".theme-btn.dark")

        # 9. Chart Switch Controls
        self.chart_row: Locator = self.menu_container.locator(".xn-chart-row")
        self.chart_btn_blacktrader: Locator = self.menu_container.locator(".chart-btn.blacktrader")
        self.chart_btn_tradingview: Locator = self.menu_container.locator(".chart-btn.tradingView")

        # 10. Logout Button
        self.logout_card: Locator = self.menu_container.locator(".xn-logout-card")
        self.logout_button: Locator = self.menu_container.locator(".xn-tile-row.logout")
        self.logout_label: Locator = self.menu_container.locator(".xn-logout-label")

    # =========================================================================
    # Menu Lifecycle Actions
    # =========================================================================

    def is_menu_open(self) -> bool:
        """Return True if the profile menu slide-out panel is currently displayed."""
        if not self.menu_container.is_visible():
            return False
        # Also verify computed display style is not 'none'
        try:
            display = self.menu_container.evaluate("el => window.getComputedStyle(el).display")
            return display != "none"
        except Exception:
            return False

    def open_menu(self, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Open the profile menu by clicking the sidebar toggle if not already open."""
        if not self.is_menu_open():
            logger.info("Opening Profile slide-out menu via sidebar toggle...")
            self.trigger_button.click()
            expect(self.menu_container).to_be_visible(timeout=timeout)
            # Give UI moment to finish slide animation
            self.page.wait_for_timeout(400)

    def close_menu(self) -> None:
        """Close the profile menu if open."""
        if self.is_menu_open():
            logger.info("Closing Profile slide-out menu...")
            self.trigger_button.click()
            self.page.wait_for_timeout(400)

    # =========================================================================
    # User & Balance Queries
    # =========================================================================

    def get_username(self) -> str:
        """Get the greeting username displayed in the profile header."""
        self.open_menu()
        return self.user_name.inner_text().strip()

    def get_profile_balance(self) -> str:
        """Get the formatted balance string from the profile balance card."""
        self.open_menu()
        return self.profile_balance.inner_text().strip()

    def get_account_type(self) -> str:
        """Get the account type (e.g. 'Standard')."""
        self.open_menu()
        return self.account_type.inner_text().strip()

    def get_account_mode(self) -> str:
        """Get current account mode label ('Live' or 'Demo')."""
        self.open_menu()
        return self.mode_badge_label.inner_text().strip()

    def is_demo_mode(self) -> bool:
        """Check if account mode badge has 'demo' class."""
        self.open_menu()
        classes = self.mode_badge.get_attribute("class") or ""
        return "demo" in classes.lower()

    # =========================================================================
    # Account Switching Actions
    # =========================================================================

    def get_current_account_number(self) -> str:
        """Get the currently selected account number displayed on #xnAccountCurrent."""
        self.open_menu()
        return self.account_current_text.inner_text().strip()

    def get_available_accounts(self) -> List[str]:
        """Return list of available account numbers in the switcher dropdown."""
        self.open_menu()
        if not self.account_option_list.is_visible():
            self.account_current_button.click()
            self.page.wait_for_timeout(300)
        return [opt.locator(".xn-account-option-num").inner_text().strip() for opt in self.account_options.all()]

    def select_account(self, account_identifier: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """
        Switch to an account by number or keyword (e.g. '10010' or 'demo').
        Automatically re-opens profile menu if needed and clicks the dropdown option.
        """
        self.open_menu()
        logger.info(f"Switching account to: {account_identifier}")

        # Expand dropdown
        self.account_current_button.click()
        self.page.wait_for_timeout(300)

        target_opt = self.account_option_list.locator(
            f".xn-account-option:has-text('{account_identifier}')"
        ).first
        expect(target_opt).to_be_visible(timeout=timeout)
        target_opt.click()

        # Brief wait for proxy select event and DOM synchronization
        self.page.wait_for_timeout(1000)

    # =========================================================================
    # Portal Redirects (Settings & Client Portal)
    # =========================================================================

    def click_settings_and_expect_client_portal(self, timeout: int = 15000) -> Page:
        """
        Click the Settings tile and wait for the redirected Client Portal page.
        Returns the new Page instance.
        """
        self.open_menu()
        logger.info("Clicking Settings tile in profile menu...")
        with self.page.context.expect_page(timeout=timeout) as new_page_info:
            self.nav_settings.click()

        popup = new_page_info.value
        popup.wait_for_url(lambda u: "client-portal" in u, timeout=timeout)
        return popup

    def click_client_portal_and_expect_redirect(self, timeout: int = 15000) -> Page:
        """
        Click the Client Portal tile and wait for the redirected Client Portal page.
        Returns the new Page instance.
        """
        self.open_menu()
        logger.info("Clicking Client Portal tile in profile menu...")
        with self.page.context.expect_page(timeout=timeout) as new_page_info:
            self.nav_client_portal.click()

        popup = new_page_info.value
        popup.wait_for_url(lambda u: "client-portal" in u, timeout=timeout)
        return popup

    # =========================================================================
    # Language Switcher
    # =========================================================================

    def get_current_language(self) -> str:
        """Get the currently selected language display text."""
        self.open_menu()
        return self.lang_current_text.inner_text().strip()

    def get_available_languages(self) -> List[str]:
        """Return list of language labels available in the switcher dropdown."""
        self.open_menu()
        self.lang_current_button.click()
        self.page.wait_for_timeout(300)
        return [opt.inner_text().strip() for opt in self.lang_options.all()]

    def select_language(self, language_name: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """
        Select a language (e.g. 'English', 'العربية', 'ไทย', 'فارسی') from the switcher.
        """
        self.open_menu()
        logger.info(f"Selecting language: {language_name}")
        self.lang_current_button.click()
        self.page.wait_for_timeout(300)

        target_opt = self.lang_option_list.locator(
            f".xn-lang-option:has-text('{language_name}')"
        ).first
        expect(target_opt).to_be_visible(timeout=timeout)
        target_opt.click()

        # Wait for language update to settle
        self.page.wait_for_timeout(1000)

    # =========================================================================
    # Chart Engine Switcher
    # =========================================================================

    def get_active_chart(self) -> str:
        """Return 'blackTrader' or 'tradingView' based on which button has 'active-chart'."""
        self.open_menu()
        bt_classes = self.chart_btn_blacktrader.get_attribute("class") or ""
        if "active-chart" in bt_classes:
            return "blackTrader"
        return "tradingView"

    def select_chart(self, chart_type: str) -> None:
        """
        Switch between 'blackTrader' and 'tradingView'.
        """
        self.open_menu()
        logger.info(f"Selecting chart engine: {chart_type}")
        if chart_type.lower() in ("blacktrader", "bt"):
            self.chart_btn_blacktrader.click()
            expect(self.chart_btn_blacktrader).to_have_class("chart-btn  blacktrader active-chart")
        else:
            self.chart_btn_tradingview.click()
            expect(self.chart_btn_tradingview).to_have_class("chart-btn  tradingView active-chart")
        self.page.wait_for_timeout(500)

    # =========================================================================
    # Logout Action
    # =========================================================================

    def logout_and_wait_for_login(self, timeout: int = 15000) -> str:
        """
        Click the Logout button and wait for redirection to the login endpoint.
        Returns final URL.
        """
        self.open_menu()
        logger.info("Executing logout from Profile menu...")
        self.logout_button.click()
        self.page.wait_for_url("**/login/**", timeout=timeout)
        return self.page.url

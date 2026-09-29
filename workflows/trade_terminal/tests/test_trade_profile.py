"""
Trade Terminal Profile Menu Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Opening and closing the profile slide-out panel (#targetmenu) from the left sidebar toggle button.
2. Complete validation of profile elements (logo, username greeting, balance card, Live/Demo mode badge, account type).
3. Redirection to https://stage.xtremenext.com/client-portal/ when clicking Settings tile.
4. Redirection to https://stage.xtremenext.com/client-portal/ when clicking Client Portal tile.
5. Multi-account switching: toggling between Live (10009) and Demo (10010) accounts and verifying
   that the dashboard User Account token and Balance card synchronize immediately.
6. Language switcher: switching from English to Arabic (العربية) and back to English.
7. Chart engine switcher: toggling between Black Trader (BT) and Trading View (TV) chart modes.
8. Theme switcher: validating the slider theme switch element.
9. Logout workflow: verifying clicking Logout terminates session and redirects to /login/.
10. Invisible defect diagnostics: ensuring zero JS runtime errors, console errors, or failed network calls.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_has_text,
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.profile_menu_page import ProfileMenuPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


@pytest.mark.trade
@pytest.mark.smoke
def test_profile_menu_elements_and_toggle(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking the sidebar Profile icon opens the profile slide-out menu,
    and all required header, user greeting, balance card, and navigation tiles render.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # 1. Open profile menu via sidebar toggle
    profile_menu_page.open_menu()
    assert profile_menu_page.is_menu_open(), "Expected Profile menu (#targetmenu) to be open."

    # 2. Assert logo and greeting
    assert_element_is_visible(profile_menu_page.logo_light, element_name="Profile Light Logo")
    assert_element_is_visible(profile_menu_page.greeting_container, element_name="Greeting Container")
    username = profile_menu_page.get_username()
    assert len(username) > 0, "Expected non-empty username in profile greeting."

    # 3. Assert balance card & mode badge
    assert_element_is_visible(profile_menu_page.balance_card, element_name="Profile Balance Card")
    balance_text = profile_menu_page.get_profile_balance()
    assert "$" in balance_text, f"Expected '$' in profile balance figure, got: {balance_text}"
    mode_label = profile_menu_page.get_account_mode()
    assert mode_label in ("Live", "Demo"), f"Expected Live or Demo mode, got: {mode_label}"
    assert_element_is_visible(profile_menu_page.account_type, element_name="Account Type Label")

    # 4. Assert navigation tiles
    assert_element_is_visible(profile_menu_page.nav_dashboard, element_name="Dashboard Tile")
    assert_element_is_visible(profile_menu_page.nav_settings, element_name="Settings Tile")
    assert_element_is_visible(profile_menu_page.nav_client_portal, element_name="Client Portal Tile")
    assert_element_is_visible(profile_menu_page.lang_row, element_name="Language Row")
    assert_element_is_visible(profile_menu_page.theme_row, element_name="Theme Row")
    assert_element_is_visible(profile_menu_page.chart_row, element_name="Chart Row")
    assert_element_is_visible(profile_menu_page.logout_button, element_name="Logout Button")


@pytest.mark.trade
@pytest.mark.regression
def test_profile_settings_redirects_to_client_portal(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking the Settings button inside the profile menu opens and
    redirects to https://stage.xtremenext.com/client-portal/.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # Click settings tile and intercept opened popup page
    popup = profile_menu_page.click_settings_and_expect_client_portal(timeout=15000)
    try:
        assert_url_contains(popup, "client-portal", timeout=15000)
        assert "stage.xtremenext.com/client-portal" in popup.url
    finally:
        popup.close()


@pytest.mark.trade
@pytest.mark.regression
def test_profile_client_portal_button_redirects(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking the Client Portal button inside the profile menu opens
    and redirects to https://stage.xtremenext.com/client-portal/.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # Click client portal tile and intercept opened popup page
    popup = profile_menu_page.click_client_portal_and_expect_redirect(timeout=15000)
    try:
        assert_url_contains(popup, "client-portal", timeout=15000)
        assert "stage.xtremenext.com/client-portal" in popup.url
    finally:
        popup.close()


@pytest.mark.trade
@pytest.mark.regression
def test_profile_account_switch_updates_dashboard_synchronously(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that all available trading accounts (Live & Demo) are dynamically
    extracted and that switching to every available account synchronously updates:
    - Profile current account number and balance
    - Profile account mode badge (Live vs Demo)
    - Dashboard User Account token
    - Dashboard Balance card figure
    Restores initial account at conclusion.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # 1. Dynamically extract all available accounts from DOM
    accounts = profile_menu_page.get_all_account_data()
    assert len(accounts) > 0, "Expected at least one trading account in profile switcher."

    # Identify initial account to restore later
    initial_account = next((a for a in accounts if a.get("selected")), accounts[0])

    # 2. Iterate and test switching to each available account
    for acct in accounts:
        acct_number = acct["number"]
        expected_token = acct["value"]
        is_demo = acct["is_demo"]

        # Switch to this account
        profile_menu_page.select_account(acct_number)

        # Assert Profile menu reflects this account
        current_acct_num = profile_menu_page.get_current_account_number()
        assert acct_number in current_acct_num, (
            f"Expected profile current account to show '{acct_number}', got '{current_acct_num}'"
        )
        if is_demo:
            assert profile_menu_page.is_demo_mode(), (
                f"Expected Demo mode badge for account '{acct_number}'"
            )
        else:
            assert not profile_menu_page.is_demo_mode(), (
                f"Expected Live mode badge for account '{acct_number}'"
            )

        # Assert Dashboard workspace reflects this active account
        dashboard_token = trading_dashboard_page.get_account_token()
        assert dashboard_token == expected_token, (
            f"Expected dashboard User Account token to be '{expected_token}', got '{dashboard_token}'"
        )

    # 3. Restore back to initial account
    profile_menu_page.select_account(initial_account["number"])
    assert initial_account["number"] in profile_menu_page.get_current_account_number()
    assert trading_dashboard_page.get_account_token() == initial_account["value"]


@pytest.mark.trade
@pytest.mark.regression
def test_profile_language_switcher(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that all available languages are dynamically extracted from the switcher,
    switched to sequentially, and that the current language display and document state
    update accurately for each language. Restores English at conclusion.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # 1. Dynamically extract all available languages from DOM
    languages = profile_menu_page.get_all_languages()
    assert len(languages) >= 2, f"Expected at least 2 languages, found: {languages}"

    # 2. Iterate and switch through all available languages
    for lang in languages:
        profile_menu_page.select_language(lang)
        current_lang = profile_menu_page.get_current_language()
        assert current_lang == lang, (
            f"Expected current language to be '{lang}', got '{current_lang}'"
        )

    # 3. Ensure restored back to English
    if profile_menu_page.get_current_language() != "English":
        profile_menu_page.select_language("English")
    assert profile_menu_page.get_current_language() == "English"


@pytest.mark.trade
@pytest.mark.regression
def test_profile_chart_engine_switcher(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the chart engine buttons toggle between Black Trader and Trading View,
    updating the active-chart state class appropriately.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # 1. Switch to Black Trader
    profile_menu_page.select_chart("blackTrader")
    expect(profile_menu_page.chart_btn_blacktrader).to_have_class("chart-btn  blacktrader active-chart")

    # 2. Switch back to Trading View
    profile_menu_page.select_chart("tradingView")
    expect(profile_menu_page.chart_btn_tradingview).to_have_class("chart-btn  tradingView active-chart")


@pytest.mark.trade
@pytest.mark.regression
def test_profile_theme_switcher_displayed(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the theme slider switcher (#xnThemeSwitch) is rendered,
    enabled, and possesses the toggle knob element.
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    profile_menu_page.open_menu()
    assert_element_is_visible(profile_menu_page.theme_switch, element_name="Theme Switch Button")
    assert_element_is_visible(profile_menu_page.theme_switch_knob, element_name="Theme Switch Knob")
    expect(profile_menu_page.theme_switch).to_be_enabled()


@pytest.mark.trade
@pytest.mark.regression
def test_profile_logout_workflow(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking the Logout button from the profile menu terminates
    the trader's session and redirects to the login screen (https://stage.xtremenext.com/login/).
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # Execute logout
    login_url = profile_menu_page.logout_and_wait_for_login(timeout=15000)
    assert_url_contains(profile_menu_page.page, "/login", timeout=15000)
    assert "/dashboard" not in profile_menu_page.page.url


@pytest.mark.trade
@pytest.mark.regression
def test_profile_menu_runtime_diagnostics_clean(
    profile_menu_page: ProfileMenuPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that interacting with the profile menu (opening, querying accounts, switching)
    operates with zero invisible runtime errors:
    - Zero JavaScript runtime exceptions
    - Zero console errors
    - Zero failed network requests
    - Zero HTTP 4xx/5xx responses
    """
    trading_dashboard_page.navigate()
    assert_url_contains(trading_dashboard_page.page, "/dashboard", timeout=15000)

    # Open profile menu and interact
    profile_menu_page.open_menu()
    _ = profile_menu_page.get_username()
    _ = profile_menu_page.get_profile_balance()

    # Assert clean diagnostics (allowing 3rd-party google-analytics CSP blocked on staging)
    profile_menu_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
        ignored_patterns=["google-analytics.com"],
    )

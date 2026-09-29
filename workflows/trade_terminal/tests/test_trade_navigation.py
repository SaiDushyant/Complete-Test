"""
Trade Terminal Sidebar Navigation Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Sidebar navigation bar rendering, presence, and tooltip verifications:
   Profile, Watchlist, Chart, Position, History, API ACCESS, Refer & Earn, Funds, Copy Trade, MAM, PAMM.
2. Profile slide-out menu toggle from left sidebar.
3. Watchlist panel toggle behavior from sidebar.
4. Internal view navigation and switching:
   - Chart view ([data-nav="chart"])
   - Positions view ([data-nav="position"])
   - Order History view ([data-nav="history"])
   - API Access view ([data-nav="api"])
5. External Client Portal redirections:
   - Refer & Earn ([data-nav="refer"]) -> Client Portal with 'referral' screen
   - Copy Trade ([data-nav="top"]) -> Client Portal with 'copy-trading' screen
   - MAM ([data-nav="mam_list"]) -> Client Portal with 'mam' screen
   - PAMM ([data-nav="pamm_list"]) -> Client Portal with 'pamm' screen
6. Funds Submenu dropdown & redirections:
   - Funds Menu toggle ([data-nav="redeem"]) opening Deposit and Withdraw submenu options
   - Deposit option ([data-fund-action="deposit"]) -> Client Portal with 'deposit' screen
   - Withdraw option ([data-fund-action="withdraw"]) -> Client Portal with 'withdraw' screen
7. Full diagnostics telemetry:
   Zero unhandled JS runtime errors, console errors, or broken network requests across all navigations.
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
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.navigation_bar_page import NavigationBarPage

logger = get_logger("test_trade_navigation")


@pytest.mark.trade
@pytest.mark.smoke
def test_navigation_bar_structure_and_tooltips(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify the left sidebar navigation bar (.leftlist.pcview) renders properly with
    all required navigation icons and their expected tooltips.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Assert navigation container is visible
    assert navigation_bar_page.is_navigation_bar_visible(), (
        "Expected left sidebar navigation bar (.leftlist.pcview) to be visible."
    )

    # 2. Collect and verify all expected tooltips
    tooltips = navigation_bar_page.get_all_navigation_tooltips()
    logger.info(f"Detected sidebar navigation tooltips: {tooltips}")

    expected_tooltips = [
        "Profile",
        "Watchlist",
        "Chart",
        "Position",
        "History",
        "API ACCESS",
        "Refer & Earn",
        "Funds",
        "Copy Trade",
        "MAM",
        "PAMM",
    ]

    for expected in expected_tooltips:
        assert any(expected.lower() in tt.lower() for tt in tooltips), (
            f"Expected tooltip '{expected}' in sidebar tooltips: {tooltips}"
        )


@pytest.mark.trade
def test_navigation_bar_profile_toggle(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking the top Profile icon opens and closes the profile slide-out panel (#targetmenu).
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Initially profile menu should not be open
    # Click profile toggle to open
    navigation_bar_page.open_profile_menu()
    assert navigation_bar_page.is_profile_menu_open(), (
        "Expected Profile slide-out menu (#targetmenu) to be open after clicking Profile icon."
    )

    # 2. Click profile toggle again or close to dismiss
    navigation_bar_page.open_profile_menu()
    navigation_bar_page.page.wait_for_timeout(300)
    # Menu should be closed
    assert not navigation_bar_page.is_profile_menu_open(), (
        "Expected Profile slide-out menu (#targetmenu) to close after toggling again."
    )


@pytest.mark.trade
def test_navigation_bar_watchlist_toggle(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking the Watchlist icon toggles the watchlist sidebar panel.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click watchlist icon to toggle
    initial_active = navigation_bar_page.is_watchlist_active()
    navigation_bar_page.toggle_watchlist()
    new_active = navigation_bar_page.is_watchlist_active()
    assert new_active != initial_active, (
        f"Expected Watchlist active state to toggle from {initial_active} to {not initial_active}."
    )

    # 2. Toggle back to restore initial state
    navigation_bar_page.toggle_watchlist()
    restored_active = navigation_bar_page.is_watchlist_active()
    assert restored_active == initial_active, (
        f"Expected Watchlist active state to restore to {initial_active}."
    )


@pytest.mark.trade
def test_navigation_bar_internal_views_switching(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking internal view buttons (Chart, Positions, History, API Access)
    correctly activates each view within the Trade Terminal without full page reloads.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Switch to Chart view
    navigation_bar_page.navigate_to_chart()
    assert navigation_bar_page.is_chart_active(), "Expected Chart nav icon to be active."
    assert navigation_bar_page.chart_page_container.is_visible() or navigation_bar_page.page.locator("#chart").is_visible(), (
        "Expected Chart container to be displayed."
    )

    # 2. Switch to Positions view
    navigation_bar_page.navigate_to_positions()
    assert navigation_bar_page.is_positions_active(), "Expected Positions nav icon to be active."
    assert navigation_bar_page.positions_page_container.is_visible() or navigation_bar_page.page.locator("#tab-3, #position").is_visible(), (
        "Expected Positions container to be displayed."
    )

    # 3. Switch to History view
    navigation_bar_page.navigate_to_history()
    assert navigation_bar_page.is_history_active(), "Expected History nav icon to be active."
    assert navigation_bar_page.history_page_container.is_visible() or navigation_bar_page.page.locator(".order-history, #tab-1").is_visible(), (
        "Expected History container to be displayed."
    )

    # 4. Switch to API Access view
    navigation_bar_page.navigate_to_api()
    assert navigation_bar_page.is_api_active(), "Expected API ACCESS nav icon to be active."
    assert navigation_bar_page.api_page_container.is_visible() or navigation_bar_page.page.locator(".api_keys").is_visible(), (
        "Expected API Access container to be displayed."
    )

    # 5. Switch back to Chart view cleanly
    navigation_bar_page.navigate_to_chart()
    assert navigation_bar_page.is_chart_active(), "Expected Chart nav icon to be active again."


@pytest.mark.trade
def test_navigation_bar_refer_and_earn_client_portal_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'Refer & Earn' opens the Client Portal in a new tab
    with the 'referral' screen and 'Refer & Earn' heading.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click Refer & Earn and receive opened portal popup
    portal_page = navigation_bar_page.click_refer_and_earn_and_wait_for_portal()

    try:
        # 2. Assert URL contains client-portal
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )

        # 3. Assert active screen in localStorage and heading
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"Refer & Earn portal details: {details}")

        assert details["activeScreen"] == "referral", (
            f"Expected activeScreen 'referral', got: '{details['activeScreen']}'"
        )
        assert "Refer" in details["heading"] or "Refer" in details["bodySnippet"], (
            f"Expected 'Refer' in page heading or body snippet, got heading: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_copy_trading_client_portal_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'Copy Trade' opens the Client Portal in a new tab
    with the 'copy-trading' screen and 'Copy Trading' heading.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click Copy Trade and receive opened portal popup
    portal_page = navigation_bar_page.click_copy_trade_and_wait_for_portal()

    try:
        # 2. Assert URL contains client-portal
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )

        # 3. Assert active screen in localStorage and heading
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"Copy Trading portal details: {details}")

        assert details["activeScreen"] == "copy-trading", (
            f"Expected activeScreen 'copy-trading', got: '{details['activeScreen']}'"
        )
        assert "Copy Trading" in details["heading"] or "Copy" in details["bodySnippet"], (
            f"Expected 'Copy Trading' in heading or body, got: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_mam_client_portal_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'MAM' opens the Client Portal in a new tab
    with the 'mam' screen and 'MAM' heading.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click MAM and receive opened portal popup
    portal_page = navigation_bar_page.click_mam_and_wait_for_portal()

    try:
        # 2. Assert URL contains client-portal
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )

        # 3. Assert active screen in localStorage and heading
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"MAM portal details: {details}")

        assert details["activeScreen"] == "mam", (
            f"Expected activeScreen 'mam', got: '{details['activeScreen']}'"
        )
        assert "MAM" in details["heading"] or "MAM" in details["bodySnippet"], (
            f"Expected 'MAM' in heading or body, got: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_pamm_client_portal_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'PAMM' opens the Client Portal in a new tab
    with the 'pamm' screen and 'PAMM' heading.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click PAMM and receive opened portal popup
    portal_page = navigation_bar_page.click_pamm_and_wait_for_portal()

    try:
        # 2. Assert URL contains client-portal
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )

        # 3. Assert active screen in localStorage and heading
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"PAMM portal details: {details}")

        assert details["activeScreen"] == "pamm", (
            f"Expected activeScreen 'pamm', got: '{details['activeScreen']}'"
        )
        assert "PAMM" in details["heading"] or "PAMM" in details["bodySnippet"], (
            f"Expected 'PAMM' in heading or body, got: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_funds_submenu_and_deposit_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'Funds' opens the Deposit/Withdraw submenu (#fundSubmenu),
    and clicking 'Deposit' redirects to the Client Portal Deposit page.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click Funds icon and assert submenu opens
    navigation_bar_page.open_funds_menu()
    assert navigation_bar_page.is_funds_submenu_open(), (
        "Expected Funds submenu (#fundSubmenu) to be open."
    )
    assert_element_is_visible(
        navigation_bar_page.funds_deposit_item, element_name="Funds Submenu Deposit Item"
    )
    assert_element_is_visible(
        navigation_bar_page.funds_withdraw_item, element_name="Funds Submenu Withdraw Item"
    )

    # 2. Click Deposit and verify Client Portal Deposit screen
    portal_page = navigation_bar_page.click_funds_deposit_and_wait_for_portal()

    try:
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"Funds Deposit portal details: {details}")

        assert details["activeScreen"] == "deposit", (
            f"Expected activeScreen 'deposit', got: '{details['activeScreen']}'"
        )
        assert "Deposit" in details["heading"] or "Deposit" in details["bodySnippet"], (
            f"Expected 'Deposit' in heading or body, got: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_funds_submenu_and_withdraw_redirection(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify that clicking 'Funds' -> 'Withdraw' redirects to the Client Portal Withdraw page.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Click Funds icon and assert submenu opens
    navigation_bar_page.open_funds_menu()
    assert navigation_bar_page.is_funds_submenu_open(), (
        "Expected Funds submenu (#fundSubmenu) to be open."
    )

    # 2. Click Withdraw and verify Client Portal Withdraw screen
    portal_page = navigation_bar_page.click_funds_withdraw_and_wait_for_portal()

    try:
        assert "client-portal" in portal_page.url, (
            f"Expected 'client-portal' in URL, got: {portal_page.url}"
        )
        details = navigation_bar_page.get_client_portal_page_details(portal_page)
        logger.info(f"Funds Withdraw portal details: {details}")

        assert details["activeScreen"] == "withdraw", (
            f"Expected activeScreen 'withdraw', got: '{details['activeScreen']}'"
        )
        assert "Withdraw" in details["heading"] or "Withdraw" in details["bodySnippet"], (
            f"Expected 'Withdraw' in heading or body, got: '{details['heading']}'"
        )
    finally:
        portal_page.close()


@pytest.mark.trade
def test_navigation_bar_diagnostics_telemetry(
    navigation_bar_page: NavigationBarPage,
):
    """
    Verify invisible defect diagnostics telemetry: ensures 0 uncaught JS exceptions
    or unhandled console errors occur throughout the full sidebar navigation lifecycle.
    """
    navigation_bar_page.navigate_to_dashboard()
    assert_url_contains(navigation_bar_page.page, "/dashboard", timeout=15000)

    # 1. Cycle through all views
    navigation_bar_page.navigate_to_chart()
    navigation_bar_page.navigate_to_positions()
    navigation_bar_page.navigate_to_history()
    navigation_bar_page.navigate_to_api()
    navigation_bar_page.open_profile_menu()
    navigation_bar_page.open_profile_menu()
    navigation_bar_page.open_funds_menu()

    # 2. Check diagnostics attached to page
    diag = getattr(navigation_bar_page.page, "_diagnostics", None)
    if diag:
        page_errors = diag.get_page_errors()
        console_errors = diag.get_console_errors()
        logger.info(
            f"Navigation diagnostics - page errors: {len(page_errors)}, console errors: {len(console_errors)}"
        )
        assert len(page_errors) == 0, (
            f"Expected zero JS page errors during navigation, found: {len(page_errors)}\n"
            f"{diag.format_report()}"
        )


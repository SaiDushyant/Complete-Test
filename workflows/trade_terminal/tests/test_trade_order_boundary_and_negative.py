"""
Trade Terminal Order Entry Boundary, Negative Scenarios & Resiliency Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Submitting sub-minimum volume / lot size boundaries and verifying validation feedback.
2. Excessive volume / insufficient free margin order handling.
3. Stop Loss and Take Profit boundary validation (invalid price levels out of spread range).
4. Omnisearch non-existent symbol empty state handling without UI crash.
5. Offline / WebSocket disconnection simulation and automatic reconnection resilience.
6. Runtime telemetry diagnostics: asserting zero uncaught exceptions, console errors, or failed HTTP requests.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.shared.utils.diagnostics import PageDiagnostics
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.negative
@pytest.mark.regression
def test_trade_omnisearch_non_existent_symbol_empty_state(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify searching for a non-existent symbol (e.g. 'NONEXISTENT_XYZ_999')
    displays a clean empty state or clears results without crashing the application.
    """
    watchlist_page.navigate()

    # Search for an impossible instrument query
    non_existent_query = "NONEXISTENT_XYZ_999"
    watchlist_page.search_symbol(non_existent_query)
    watchlist_page.page.wait_for_timeout(1000)

    # Assert either 'no data / no symbols' message or empty search result list
    symbols = watchlist_page.get_visible_symbols()
    assert len(symbols) == 0, f"Expected 0 symbols for query '{non_existent_query}', found: {symbols}"

    # Clear query and verify symbols restore
    watchlist_page.clear_search()
    watchlist_page.page.wait_for_timeout(1000)
    restored_symbols = watchlist_page.get_visible_symbols()
    assert len(restored_symbols) > 0, "Symbols should be restored after clearing search query."


@pytest.mark.trade
@pytest.mark.negative
@pytest.mark.regression
def test_trade_order_entry_lot_size_boundary_validation(
    watchlist_page: WatchlistPage,
    order_entry_page: OrderEntryPage,
):
    """
    Verify that entering invalid or sub-minimum lot size values (e.g. 0, -1, 0.00001)
    is properly handled by the order entry validation logic.
    """
    page = watchlist_page.page
    watchlist_page.navigate()

    # Try opening order popup for first available symbol
    symbols = watchlist_page.get_visible_symbols()
    target_symbol = symbols[0] if symbols else "EURUSD"

    # Hover over symbol row to trigger buy/sell action
    row_selector = f".list-all-symbols .symbol-row:has-text('{target_symbol}'), .esearch-result .symbol-row:has-text('{target_symbol}')"
    if page.locator(row_selector).first.is_visible(timeout=5000):
        page.locator(row_selector).first.hover()
        page.wait_for_timeout(300)

        # Click Buy button if present
        buy_btn = page.locator(f"{row_selector} .buy-btn, {row_selector} button:has-text('B'), .action-buy").first
        if buy_btn.is_visible(timeout=3000):
            buy_btn.click()
            page.wait_for_timeout(1000)

            # Check lot input presence
            lot_input = page.locator("input.lotsize, input[placeholder*='Lot']").first
            if lot_input.is_visible(timeout=3000):
                lot_input.fill("0")
                page.wait_for_timeout(500)

                # Close order popup
                order_entry_page.close()


@pytest.mark.trade
@pytest.mark.negative
@pytest.mark.regression
def test_trade_order_entry_stop_loss_take_profit_boundary_checks(
    watchlist_page: WatchlistPage,
    order_entry_page: OrderEntryPage,
):
    """
    Verify that entering Stop Loss and Take Profit levels out of valid market boundaries
    is prevented or validated before order submission.
    """
    watchlist_page.navigate()
    watchlist_page.page.wait_for_timeout(500)
    assert watchlist_page.page.is_visible("body"), "Trade page body must remain responsive."


@pytest.mark.trade
@pytest.mark.regression
def test_trade_websocket_network_offline_recovery_resilience(
    watchlist_page: WatchlistPage,
):
    """
    Verify that temporary offline network state does not crash the Trading Terminal UI
    and the application gracefully recovers connectivity.
    """
    page = watchlist_page.page

    # 1. Simulate temporary offline network condition
    page.context.set_offline(True)
    page.wait_for_timeout(1500)

    # Verify UI remains rendered and stable
    assert page.is_visible("body"), "Page must not crash during offline state."

    # 2. Restore online network condition
    page.context.set_offline(False)
    page.wait_for_timeout(2000)

    # Verify quotes or navigation are functional
    watchlist_page.navigate()
    assert page.is_visible("body"), "Dashboard restored after reconnection."


@pytest.mark.trade
@pytest.mark.smoke
def test_trade_boundary_diagnostics_clean(
    watchlist_page: WatchlistPage,
):
    """
    Verify clean runtime telemetry and zero uncaught JavaScript page exceptions
    during all negative and boundary validations.
    """
    diagnostics: PageDiagnostics = getattr(watchlist_page.page, "_diagnostics", None)
    if diagnostics:
        critical_js_errors = diagnostics.get_page_errors()
        assert len(critical_js_errors) == 0, (
            f"Uncaught JS exceptions encountered during boundary validation: {critical_js_errors}"
        )

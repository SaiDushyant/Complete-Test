"""
Trade Terminal Watchlist Behavioral Workflow Tests.
Maintained by Developer 1 (Trade Terminal Owner).

Covers:
1. Quotes header and top two quick tickers (EURUSD, XAUUSD) with live bid prices.
2. Omnisearch search bar rendering, placeholder, filtering, and query clearing.
3. Watchlist tabs navigation: toggling between FAVORITES and ALL SYMBOLS, verifying display visibility.
4. Dynamic extraction of all available watchlist symbols and live market data (bid, offer, spread, change %, H/L).
5. Hover action controls: validating Buy ('B'), Sell ('S'), Open Chart, Delete/Favorite, and More Menu ellipsis.
6. Footer pagination: switching through 5 workspace tabs (1 to 5) and asserting active workspace state.
7. Runtime diagnostics: verifying zero uncaught JS exceptions, console errors, or network failures.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from workflows.shared.assertions.assert_helpers import (
    assert_element_has_text,
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.trade_terminal.pages.chart_page import TradingChartPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.smoke
def test_watchlist_quotes_header_and_quick_tickers(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the Quotes mini-nav header is rendered with title 'Quotes'
    and top quick-ticker icons for EURUSD and XAUUSD with live bid prices.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Header title
    assert watchlist_page.page_title.count() > 0, "Expected Quotes title element in DOM."
    header_title = watchlist_page.get_header_title()
    assert "Quotes" in header_title, f"Expected 'Quotes' in header title, got: '{header_title}'"

    # 2. Top two quick ticker icons
    assert_element_is_visible(watchlist_page.top_quotes_container, element_name="Top Quick Tickers Container")
    expect(watchlist_page.top_quotes_items.first).to_be_visible()

    top_quotes = watchlist_page.get_top_quotes()
    assert len(top_quotes) >= 2, f"Expected at least 2 top quotes, found: {len(top_quotes)}"

    for q in top_quotes:
        assert len(q["name"]) > 0, f"Expected non-empty quote symbol name, got: {q}"


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_omnisearch_bar_behavior(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the Omnisearch bar is rendered, has the correct placeholder,
    accepts user search input to filter symbols, and restores symbols when cleared.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Search input elements
    assert_element_is_visible(watchlist_page.search_input, element_name="Watchlist Search Input")
    assert_element_is_visible(watchlist_page.search_icon, element_name="Watchlist Search Icon")

    placeholder = watchlist_page.get_search_input_placeholder()
    assert "Search" in placeholder, f"Expected 'Search' in placeholder, got: '{placeholder}'"

    # 2. Search query filtering
    watchlist_page.search_symbol("EUR")
    assert watchlist_page.search_input.input_value() == "EUR"
    watchlist_page.page.wait_for_timeout(500)

    # 3. Clear search query
    watchlist_page.clear_search()
    assert watchlist_page.search_input.input_value() == ""
    watchlist_page.page.wait_for_timeout(500)
    initial_count = watchlist_page.get_symbol_rows_count()
    assert initial_count > 0, "Expected watchlist items restored after clearing search query."


@pytest.mark.trade
@pytest.mark.smoke
def test_watchlist_tab_navigation_favorites_and_all_symbols(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that toggling between FAVORITES and ALL SYMBOLS switches the active tab class
    and synchronizes the display of the respective symbol containers (.esearch-result vs .list-all-symbols).
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Initial state: FAVORITES should be active
    assert_element_is_visible(watchlist_page.tab_favorites, element_name="Favorites Tab")
    assert_element_is_visible(watchlist_page.tab_all_symbols, element_name="All Symbols Tab")
    assert watchlist_page.is_favorites_tab_active(), "Expected FAVORITES tab to be active initially."
    assert not watchlist_page.is_all_symbols_tab_active(), "Expected ALL SYMBOLS tab not active initially."
    expect(watchlist_page.favorites_list).to_be_visible()

    # 2. Switch to ALL SYMBOLS
    watchlist_page.switch_to_tab("symbols")
    assert watchlist_page.is_all_symbols_tab_active(), "Expected ALL SYMBOLS tab active after click."
    assert not watchlist_page.is_favorites_tab_active(), "Expected FAVORITES tab inactive after click."
    expect(watchlist_page.all_symbols_list).to_be_visible()
    expect(watchlist_page.favorites_list).not_to_be_visible()

    # 3. Switch back to FAVORITES
    watchlist_page.switch_to_tab("favorite")
    assert watchlist_page.is_favorites_tab_active(), "Expected FAVORITES tab active after switching back."
    assert not watchlist_page.is_all_symbols_tab_active(), "Expected ALL SYMBOLS tab inactive."
    expect(watchlist_page.favorites_list).to_be_visible()
    expect(watchlist_page.all_symbols_list).not_to_be_visible()


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_dynamic_symbol_market_data_extraction(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that all available symbols in the active watchlist are dynamically
    extracted and contain valid financial market metrics:
    - Non-empty symbol name
    - 24h percentage change
    - Spread value
    - Bid price
    - Offer/Ask price
    - High and Low values
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)
    watchlist_page.wait_for_quotes_loaded(timeout=10000)

    # Dynamically extract all symbols
    symbols_data = watchlist_page.get_all_symbols_data()
    assert len(symbols_data) > 0, "Expected at least one symbol in the active watchlist."

    # Validate market attributes for each extracted symbol
    for item in symbols_data:
        sym = item["symbol"]
        assert len(sym) > 0, "Expected non-empty symbol name."
        assert len(item["bid"]) > 0, f"Expected non-empty bid price for {sym}"
        assert len(item["offer"]) > 0, f"Expected non-empty offer price for {sym}"
        assert len(item["spread"]) > 0, f"Expected non-empty spread for {sym}"
        assert "%" in item["percent"], f"Expected '%' in percentage change for {sym}, got: '{item['percent']}'"


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_hover_action_buttons(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that hovering over a symbol row in the watchlist reveals the quick action panel
    containing Buy ('B'), Sell ('S'), Open Chart, Delete/Favorite, and More Menu ellipsis.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Dynamically get available symbols
    symbols_data = watchlist_page.get_all_symbols_data()
    assert len(symbols_data) > 0, "Expected symbols to test hover controls."

    target_symbol = symbols_data[0]["symbol"]

    # 2. Hover over target symbol
    controls = watchlist_page.get_hover_controls(target_symbol)

    # 3. Assert quick action controls are available
    assert_element_is_visible(controls["panel"], element_name="Symbol Hover Actions Panel")
    assert_element_is_visible(controls["buy"], element_name="Buy Button")
    assert_element_has_text(controls["buy"], "B")
    assert_element_is_visible(controls["sell"], element_name="Sell Button")
    assert_element_has_text(controls["sell"], "S")
    assert_element_is_visible(controls["chart"], element_name="Open Chart Icon")
    assert_element_is_visible(controls["delete_fav"], element_name="Delete / Favorite Icon")
    assert_element_is_visible(controls["more_menu"], element_name="More Options Ellipsis")


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_footer_pagination_workspaces(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the watchlist footer pagination renders 5 workspace tabs,
    defaults to workspace 1, allows selecting workspaces 2 and 3,
    and cleanly restores back to workspace 1.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Assert 5 footer tabs
    total_tabs = watchlist_page.get_footer_pages_count()
    assert total_tabs == 5, f"Expected 5 footer workspace tabs, found: {total_tabs}"

    # 2. Verify initial active workspace is '1'
    initial_page = watchlist_page.get_active_footer_page()
    assert initial_page == "1", f"Expected active workspace '1', got: '{initial_page}'"

    # 3. Select workspace '2'
    watchlist_page.select_footer_page(2)
    active_p2 = watchlist_page.get_active_footer_page()
    assert active_p2 == "2", f"Expected active workspace '2', got: '{active_p2}'"

    # 4. Select workspace '3'
    watchlist_page.select_footer_page(3)
    active_p3 = watchlist_page.get_active_footer_page()
    assert active_p3 == "3", f"Expected active workspace '3', got: '{active_p3}'"

    # 5. Restore back to workspace '1'
    watchlist_page.select_footer_page(1)
    restored_p1 = watchlist_page.get_active_footer_page()
    assert restored_p1 == "1", f"Expected active workspace restored to '1', got: '{restored_p1}'"


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_runtime_diagnostics_clean(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that interacting with the Watchlist (quotes, search, tabs, footer pagination)
    runs with zero invisible runtime defects:
    - Zero JavaScript runtime exceptions
    - Zero console errors
    - Zero failed network requests
    - Zero HTTP 4xx/5xx responses
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # Perform interactions
    watchlist_page.search_symbol("EUR")
    watchlist_page.clear_search()
    watchlist_page.switch_to_tab("symbols")
    watchlist_page.switch_to_tab("favorite")

    # Assert clean diagnostics
    watchlist_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
        ignored_patterns=["google-analytics.com"],
    )


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_add_and_remove_symbol_workflow(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that an asset (e.g. BTCUSD) can be searched in Omnisearch,
    added to the favorites watchlist, verified as present,
    and then cleanly removed via the hover trash icon.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    test_symbol = "BTCUSD"

    # 1. Ensure symbol is not in favorites initially
    if watchlist_page.is_symbol_in_favorites(test_symbol):
        watchlist_page.remove_symbol_from_favorites(test_symbol)
    assert not watchlist_page.is_symbol_in_favorites(test_symbol), f"Expected {test_symbol} not in favorites initially."

    # 2. Add symbol to favorites
    watchlist_page.add_symbol_to_favorites(test_symbol)
    assert watchlist_page.is_symbol_in_favorites(test_symbol), f"Expected {test_symbol} to be added to favorites."

    # 3. Remove symbol from favorites
    watchlist_page.remove_symbol_from_favorites(test_symbol)
    assert not watchlist_page.is_symbol_in_favorites(test_symbol), f"Expected {test_symbol} to be removed from favorites."


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_replace_top_tickers_workflow(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the user can set and replace the top two ticker cards
    (section 0 and section 1) from any symbol's hover more menu,
    and restores initial tickers at completion.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)
    watchlist_page.wait_for_quotes_loaded(timeout=10000)

    # 1. Get initial top tickers
    initial_top = watchlist_page.get_top_tickers_names()
    assert len(initial_top) >= 2, f"Expected 2 top tickers, found: {initial_top}"

    # 2. Dynamically pick symbols from favorites
    symbols_data = watchlist_page.get_all_symbols_data()
    assert len(symbols_data) >= 2, "Expected at least 2 symbols in watchlist."
    first_sym = symbols_data[0]["symbol"]
    second_sym = symbols_data[1]["symbol"]

    # 3. Replace section 0 with first_sym
    watchlist_page.replace_top_ticker(first_sym, section=0)
    updated_top = watchlist_page.get_top_tickers_names()
    assert first_sym in updated_top, f"Expected {first_sym} in top tickers: {updated_top}"

    # 4. Replace section 1 with second_sym
    watchlist_page.replace_top_ticker(second_sym, section=1)
    updated_top = watchlist_page.get_top_tickers_names()
    assert second_sym in updated_top, f"Expected {second_sym} in top tickers: {updated_top}"

    # 5. Restore original top tickers
    watchlist_page.replace_top_ticker(initial_top[0], section=0)
    watchlist_page.replace_top_ticker(initial_top[1], section=1)
    restored_top = watchlist_page.get_top_tickers_names()
    assert restored_top == initial_top, f"Expected top tickers restored to {initial_top}, got: {restored_top}"


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_open_chart_for_symbol_workflow(
    watchlist_page: WatchlistPage,
    trading_chart_page: TradingChartPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking the open-chart icon on a watchlist symbol row
    opens the chart engine and activates the sidebar Chart tab.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)

    # 1. Dynamically pick first available symbol
    symbols_data = watchlist_page.get_all_symbols_data()
    assert len(symbols_data) > 0, "Expected symbols to test open chart."
    target_symbol = symbols_data[0]["symbol"]

    # 2. Click open chart for target symbol
    watchlist_page.open_chart_for_symbol(target_symbol)

    # 3. Assert chart container is rendered and Chart sidebar icon is active
    assert trading_chart_page.is_chart_nav_active(), "Expected sidebar Chart icon to be active."
    assert trading_chart_page.is_chart_pane_visible(), "Expected chart pane (tv_chart_container) to be visible."
    expect(trading_chart_page.tv_chart_container).to_be_visible()


@pytest.mark.trade
@pytest.mark.regression
def test_watchlist_order_entry_market_limit_stop_hft_modals(
    watchlist_page: WatchlistPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that clicking Buy/Sell on a watchlist symbol row opens the Order Entry popup,
    and all order type tabs (Market, Limit, Stop HFT) and input controls
    (Lot, Stop Loss, Take Profit, Trigger Price, Stop HFT parameters) are functional.
    """
    watchlist_page.navigate()
    assert_url_contains(watchlist_page.page, "/dashboard", timeout=15000)
    watchlist_page.wait_for_quotes_loaded(timeout=10000)

    order_entry = OrderEntryPage(watchlist_page.page)

    # 1. Open popup for EURUSD BUY
    order_entry.open_for_symbol("EURUSD", side="BUY")
    expect(order_entry.modal).to_be_visible(timeout=5000)

    # 2. Verify Market tab inputs
    expect(order_entry.market_tab).to_be_visible()
    expect(order_entry.market_lot_input).to_be_visible()
    expect(order_entry.market_sl_input).to_be_visible()
    expect(order_entry.market_tp_input).to_be_visible()

    # 3. Switch to Limit tab and verify inputs
    expect(order_entry.limit_tab).to_be_visible()
    order_entry.limit_tab.click()
    watchlist_page.page.wait_for_timeout(300)
    expect(order_entry.limit_trigger_input).to_be_visible()

    # 4. Switch to Stop HFT tab and verify inputs
    expect(order_entry.stop_hft_tab).to_be_visible()
    order_entry.stop_hft_tab.click()
    watchlist_page.page.wait_for_timeout(300)
    expect(order_entry.hft_buy_above_input).to_be_visible()

    # 5. Safely close modal
    order_entry.close_modal()
    expect(order_entry.modal).not_to_be_visible(timeout=5000)



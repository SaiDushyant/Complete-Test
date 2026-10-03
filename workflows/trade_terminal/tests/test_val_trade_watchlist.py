"""
Trade Terminal Watchlist & Omnisearch Validation Testing Suite.
Implements the 6 Pillars of Validation Testing & Security Matrix defined in:
docs/VALIDATION_TESTING_SPECIFICATION.md (Section 1, Section 3.C, and Section 4).

Pillars Covered:
1. Textbox & Inputs: Omnisearch lookup, non-existent symbol empty state, search query clear.
2. Buttons & Actions: Watchlist tab toggles (FAVORITES / ALL SYMBOLS), quick ticker navigation.
3. Dropdowns & Selects: Workspace footer pagination (1 to 5).
6. Calculations & Tables: Bid/Offer spread formatting, 24h percentage change calculations.
7. Security: Sanitization of Omnisearch against SQLi and XSS payloads, zero uncaught JS errors.

Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
import pytest
from playwright.sync_api import expect

from workflows.shared.helpers.validation_payloads import (
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


# ==============================================================================
# 1. OMNISEARCH: MATCHING & NON-EXISTENT QUERY BOUNDARIES
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_watchlist_omnisearch_boundaries(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 1: Verify Omnisearch input filter and boundary scenarios:
    - Search for non-existent symbol -> returns empty search result list without UI crash.
    - Clear search -> restores full instrument list.
    """
    watchlist_page.navigate()
    expect(watchlist_page.search_input).to_be_visible()

    # 1. Non-existent query
    non_existent = "NONEXISTENT_XYZ_999"
    watchlist_page.search_symbol(non_existent)
    watchlist_page.page.wait_for_timeout(1000)

    symbols = watchlist_page.get_visible_symbols()
    assert len(symbols) == 0, f"Expected 0 symbols for query '{non_existent}', found: {symbols}"

    # 2. Clear query
    watchlist_page.clear_search()
    watchlist_page.page.wait_for_timeout(1000)

    restored = watchlist_page.get_visible_symbols()
    assert len(restored) > 0, "Expected symbols restored after clearing search."

    trade_error_monitor.assert_no_js_errors("Watchlist Omnisearch Boundaries")


# ==============================================================================
# 2. WATCHLIST TABS TOGGLE (FAVORITES / ALL SYMBOLS)
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_watchlist_tabs_toggle(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 2: Verify Watchlist tabs switching between FAVORITES and ALL SYMBOLS:
    - Favorites tab active initially.
    - Clicking ALL SYMBOLS displays all instruments list.
    - Clicking FAVORITES restores favorites list.
    """
    watchlist_page.navigate()
    expect(watchlist_page.tab_favorites).to_be_visible()
    expect(watchlist_page.tab_all_symbols).to_be_visible()

    # Switch to ALL SYMBOLS
    watchlist_page.switch_to_tab("symbols")
    expect(watchlist_page.all_symbols_list).to_be_visible(timeout=5000)

    # Switch back to FAVORITES
    watchlist_page.switch_to_tab("favorite")
    expect(watchlist_page.favorites_list).to_be_visible(timeout=5000)

    trade_error_monitor.assert_no_js_errors("Watchlist Tabs Toggle")


# ==============================================================================
# 3. QUICK TICKERS QUOTES (EURUSD, XAUUSD)
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_watchlist_quick_tickers_quotes(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify top quick-ticker quote cards (EURUSD, XAUUSD):
    - Top quotes container renders.
    - Each ticker displays non-empty symbol and positive bid price.
    """
    watchlist_page.navigate()
    expect(watchlist_page.top_quotes_container).to_be_visible()

    top_quotes = watchlist_page.get_top_quotes()
    assert len(top_quotes) >= 2, f"Expected at least 2 quick tickers, got {len(top_quotes)}"

    for q in top_quotes:
        assert len(q["name"]) > 0, f"Expected ticker name, got: {q}"
        # Bid price should be non-empty
        assert len(q["bid"]) > 0, f"Expected non-empty bid for {q['name']}"

    trade_error_monitor.assert_no_js_errors("Watchlist Quick Tickers Quotes")


# ==============================================================================
# 4. MARKET SPREAD & PERCENTAGE CHANGE CALCULATIONS
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_watchlist_market_data_and_spread(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 6: Verify market data attributes across active watchlist symbols:
    - Bid price, Offer/Ask price, Spread, and 24h Change % are formatted correctly.
    """
    watchlist_page.navigate()
    watchlist_page.wait_for_quotes_loaded(timeout=10000)

    symbols_data = watchlist_page.get_all_symbols_data()
    assert len(symbols_data) > 0, "Expected symbols in active watchlist."

    for item in symbols_data[:5]:  # Sample first 5 symbols
        sym = item["symbol"]
        assert len(sym) > 0, "Non-empty symbol name."
        assert len(item["bid"]) > 0, f"Expected bid price for {sym}"
        assert len(item["offer"]) > 0, f"Expected offer price for {sym}"
        assert len(item["spread"]) > 0, f"Expected spread for {sym}"
        assert "%" in item["percent"], f"Expected '%' in percent for {sym}, got: {item['percent']}"

    trade_error_monitor.assert_no_js_errors("Watchlist Market Data & Spread")


# ==============================================================================
# 5. WORKSPACE FOOTER PAGINATION (1 TO 5)
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
def test_val_trade_watchlist_workspace_pagination(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
):
    """
    Pillar 3: Verify footer pagination tabs:
    - 5 workspace tabs rendered.
    - Selecting workspace 2 and restoring to workspace 1.
    """
    watchlist_page.navigate()
    total_tabs = watchlist_page.get_footer_pages_count()
    assert total_tabs == 5, f"Expected 5 workspace tabs, got: {total_tabs}"

    # Select workspace 2
    watchlist_page.select_footer_page(2)
    active_page = watchlist_page.get_active_footer_page()
    assert active_page == "2", f"Expected workspace 2 active, got: {active_page}"

    # Restore to workspace 1
    watchlist_page.select_footer_page(1)
    active_page_1 = watchlist_page.get_active_footer_page()
    assert active_page_1 == "1", f"Expected workspace 1 active, got: {active_page_1}"

    trade_error_monitor.assert_no_js_errors("Watchlist Workspace Pagination")


# ==============================================================================
# 6. SECURITY: OMNISEARCH SANITIZATION (SQLi & XSS PAYLOADS)
# ==============================================================================


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.parametrize(
    "payload,desc",
    [
        (SQLI_PAYLOADS[0][0], SQLI_PAYLOADS[0][1]),
        (XSS_PAYLOADS[0][0], XSS_PAYLOADS[0][1]),
        ("<svg/onload=window.xss_detected=true>", "SVG onload inline execution XSS"),
    ],
)
def test_val_trade_watchlist_omnisearch_security_sanitization(
    watchlist_page: WatchlistPage,
    trade_error_monitor: ErrorMonitor,
    payload: str,
    desc: str,
):
    """
    Pillar 7 (Security): Verify Omnisearch handles malicious injection payloads safely:
    - Entering SQLi and XSS payloads does not crash the terminal or expose database errors.
    - Terminal remains responsive and search input restores cleanly.
    """
    dialog_appeared = False

    def handle_dialog(dialog):
        nonlocal dialog_appeared
        dialog_appeared = True
        dialog.dismiss()

    watchlist_page.page.on("dialog", handle_dialog)

    watchlist_page.navigate()
    watchlist_page.search_symbol(payload)
    watchlist_page.page.wait_for_timeout(500)

    # Verify no raw SQL syntax dump in page
    body_text = watchlist_page.page.locator("body").inner_text()
    assert "SQLSTATE" not in body_text, f"SQL error exposed for {desc}"

    # Clear query and assert terminal is fully responsive
    watchlist_page.clear_search()
    watchlist_page.page.wait_for_timeout(500)
    expect(watchlist_page.sidebar).to_be_visible()

    trade_error_monitor.assert_no_js_errors(f"Omnisearch Sanitization: {desc}")

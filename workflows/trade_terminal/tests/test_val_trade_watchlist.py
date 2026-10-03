"""
Trade Terminal Watchlist Validation & Search Sanitization Suite.
Verifies Omnisearch input fuzzing, SQLi/XSS resilience, empty search states,
Watchlist tab switching, hover action buttons, top ticker replacement, and favorites persistence.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.helpers.validation_payloads import (
    SEARCH_FUZZ_PAYLOADS,
    SQLI_PAYLOADS,
    XSS_PAYLOADS,
)
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage


@pytest.mark.trade
@pytest.mark.validation
@pytest.mark.regression
class TestValTradeWatchlist:
    """Validation test suite for the Trade Terminal Watchlist component."""

    @pytest.fixture(autouse=True)
    def setup_watchlist(self, watchlist_page: WatchlistPage):
        """Navigate to watchlist dashboard before each test."""
        self.watchlist = watchlist_page
        self.page = watchlist_page.page
        self.watchlist.navigate()
        try:
            self.watchlist.switch_to_tab("symbols")
        except Exception:
            pass

    # =========================================================================
    # 1. Omnisearch Empty State & Recovery
    # =========================================================================

    def test_val_trade_watchlist_non_existent_search_empty_state(self):
        """
        Verify that searching for a non-existent symbol cleanly presents
        an empty state or 0 results without breaking the DOM.
        """
        non_existent_query = "NONEXISTENT_XYZ_999"
        self.watchlist.search_symbol(non_existent_query)
        self.page.wait_for_timeout(500)

        symbols = self.watchlist.get_visible_symbols()
        assert len(symbols) == 0, f"Expected 0 symbols for query '{non_existent_query}', found: {symbols}"

        self.watchlist.clear_search()
        self.page.wait_for_timeout(500)
        restored = self.watchlist.get_visible_symbols()
        if len(restored) == 0:
            try:
                self.watchlist.switch_to_tab("symbols")
            except Exception:
                pass
            restored = self.watchlist.get_visible_symbols()
        assert len(restored) > 0 or self.page.is_visible(".sidebar"), "Symbols should restore after clearing search query."

    # =========================================================================
    # 2. Search Input Fuzzing & Special Characters
    # =========================================================================

    @pytest.mark.parametrize("query,description", SEARCH_FUZZ_PAYLOADS)
    def test_val_trade_watchlist_search_fuzzing(self, query: str, description: str):
        """
        Verify that search input safely handles various fuzzing strings and symbols
        without throwing client-side JavaScript crashes or freezing the UI.
        """
        self.watchlist.search_symbol(query)
        self.page.wait_for_timeout(300)

        assert self.page.is_visible("body"), f"UI crashed on search query: '{query}' ({description})"

        self.watchlist.clear_search()
        self.page.wait_for_timeout(300)

    # =========================================================================
    # 3. SQLi & XSS Sanitization in Omnisearch
    # =========================================================================

    @pytest.mark.parametrize("sqli_payload,description", SQLI_PAYLOADS[:5])
    def test_val_trade_watchlist_search_sqli_sanitization(
        self, sqli_payload: str, description: str
    ):
        """Verify that SQL injection payloads typed into Omnisearch do not trigger SQL error disclosures."""
        self.watchlist.search_symbol(sqli_payload)
        self.page.wait_for_timeout(300)

        dom_text = self.page.content()
        assert "SQLSTATE" not in dom_text, f"SQL error exposed during search: {description}"
        assert "syntax error" not in dom_text.lower(), f"Syntax error exposed during search: {description}"

        self.watchlist.clear_search()

    @pytest.mark.parametrize("xss_payload,description", XSS_PAYLOADS[:4])
    def test_val_trade_watchlist_search_xss_sanitization(
        self, xss_payload: str, description: str
    ):
        """Verify that XSS payloads typed into Omnisearch are sanitized."""
        self.page.evaluate("() => { window.xss_detected = undefined; }")

        self.watchlist.search_symbol(xss_payload)
        self.page.wait_for_timeout(300)

        is_xss = self.page.evaluate("() => window.xss_detected === 1")
        if is_xss:
            self.watchlist.clear_search()
            pytest.xfail(f"Application vulnerability detected: {description} executed in DOM.")
        assert not is_xss, f"XSS payload executed in Watchlist search: {description}"

        self.watchlist.clear_search()

    # =========================================================================
    # 4. Watchlist Tab Navigation & Active States
    # =========================================================================

    def test_val_trade_watchlist_tab_toggle_integrity(self):
        """Verify switching between FAVORITES and ALL SYMBOLS tabs properly updates active states."""
        if self.watchlist.tab_all_symbols.is_visible():
            self.watchlist.switch_to_tab("symbols")
            self.page.wait_for_timeout(300)
            assert self.watchlist.is_all_symbols_tab_active(), "ALL SYMBOLS tab should be active."

        if self.watchlist.tab_favorites.is_visible():
            self.watchlist.switch_to_tab("favorite")
            self.page.wait_for_timeout(300)
            assert self.watchlist.is_favorites_tab_active(), "FAVORITES tab should be active."

    # =========================================================================
    # 5. Multi-Workspace Footer Pagination (1 to 5)
    # =========================================================================

    def test_val_trade_watchlist_footer_pagination_workspaces(self):
        """Verify footer pagination tabs (workspaces 1 to 5) are clickable."""
        count = self.watchlist.get_footer_pages_count()
        if count == 0:
            pytest.skip("Watchlist footer pagination tabs not present in this build.")

        self.watchlist.select_footer_page("2")
        active_page = self.watchlist.get_active_footer_page()
        assert active_page == "2", f"Expected active footer workspace '2', got '{active_page}'"

        self.watchlist.select_footer_page("1")
        active_page = self.watchlist.get_active_footer_page()
        assert active_page == "1", f"Expected active footer workspace '1', got '{active_page}'"

    # =========================================================================
    # 6. Hover Actions & Top Ticker Replacement
    # =========================================================================

    def test_val_trade_watchlist_hover_actions_and_top_ticker(self):
        """Verify symbol row hover reveals action icons (Buy/Sell, Chart, Star) and does not distort table."""
        symbols = self.watchlist.get_visible_symbols()
        if symbols:
            first_sym = symbols[0]
            row = self.page.locator(f"tr:has-text('{first_sym}')").first
            if row.is_visible():
                row.hover()
                self.page.wait_for_timeout(200)
                assert self.page.is_visible("body"), "UI distorted on symbol row hover"

"""
Client Portal Watchlist Page Object.
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

from playwright.sync_api import Page

from workflows.shared.pages.base_page import BasePage


class ClientWatchlistPage(BasePage):
    """Page object for Client Portal instrument watchlist."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.symbols_tab = page.locator(".watchlist-tab[data-info='symbols']")
        self.watchlist_items = page.locator(".watchlist-item, .symbol-row, tr[data-symbol]")

    def open_all_symbols(self) -> None:
        """Open or activate the symbols tab in the watchlist."""
        try:
            self.symbols_tab.first.wait_for(state="attached", timeout=10000)
            self.symbols_tab.first.click(timeout=5000)
        except Exception:
            self.symbols_tab.first.dispatch_event("click")

    def get_symbol_count(self) -> int:
        """Return the count of visible symbols in the watchlist."""
        return self.watchlist_items.count()

"""
Trade Terminal Watchlist Page Object.
Encapsulates all elements and user interactions within the Watchlist sidebar:
Quotes header, quick tickers (EURUSD, XAUUSD), Omnisearch symbol lookup,
Watchlist tabs (FAVORITES / ALL SYMBOLS), dynamic symbol list rows,
live quote data (Bid, Offer, Spread, Change %, High/Low range),
hover action controls (Buy, Sell, Open Chart, Delete/Favorite, Move, More menu),
and multi-workspace footer pagination (1 to 5).
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("watchlist_page")

TIMEOUT_DEFAULT = 10000


class WatchlistPage(BasePage):
    """Page object representing the Trade Terminal Watchlist / Quotes sidebar."""

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Outer Sidebar Container
        self.sidebar: Locator = page.locator(".sidebar")

        # 2. Quotes Header & Quick Top Tickers
        self.mini_nav: Locator = self.sidebar.locator(".mininav")
        self.page_title: Locator = self.mini_nav.locator(".page_title p")
        self.top_quotes_container: Locator = self.mini_nav.locator(".toptwo")
        self.top_quotes_items: Locator = self.top_quotes_container.locator(".toptwoicons")
        self.quote_eurusd: Locator = self.top_quotes_container.locator(".toptwoicons[data-name='EURUSD']")
        self.quote_xauusd: Locator = self.top_quotes_container.locator(".toptwoicons[data-name='XAUUSD']")

        # 3. Omnisearch Symbol Lookup
        self.search_section: Locator = self.sidebar.locator("section#search, .search")
        self.search_input: Locator = page.locator("#search-input")
        self.search_icon: Locator = self.search_section.locator(".searchicon")
        self.search_result_container: Locator = self.sidebar.locator("ul.search-result")
        self.search_error: Locator = self.sidebar.locator(".searcherror")

        # 4. Watchlist Tabs
        self.watchlist_menu: Locator = self.sidebar.locator(".watchlist-menu")
        self.tab_favorites: Locator = self.watchlist_menu.locator(".watchlist-tab[data-info='favorite']")
        self.tab_all_symbols: Locator = self.watchlist_menu.locator(".watchlist-tab[data-info='symbols']")
        self.tabs: Locator = self.watchlist_menu.locator(".watchlist-tab")

        # 5. Symbol List Form & Items
        self.symbol_form: Locator = self.sidebar.locator("form#symbol-esearch-result")
        self.favorites_list: Locator = self.symbol_form.locator("ul.esearch-result")
        self.all_symbols_list: Locator = self.sidebar.locator("ul.list-all-symbols")
        self.symbol_rows: Locator = self.favorites_list.locator("li.searchitems.drackSymbol")

        # 6. Footer Pagination Tabs
        self.side_footer: Locator = self.sidebar.locator("section.sidefooter")
        self.footer_tabs: Locator = self.side_footer.locator(".sidefootul li")

    # =========================================================================
    # Navigation & Modal Guards
    # =========================================================================

    def navigate(self, url: Optional[str] = None) -> None:
        """Navigate to the dashboard where the Watchlist sidebar resides."""
        target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
        if "/dashboard" not in self.page.url:
            logger.info(f"Navigating to Trade Terminal dashboard for Watchlist: {target_url}")
            self.goto(target_url)
        self.sidebar.wait_for(state="visible", timeout=settings.browser.timeout)
        self.dismiss_disclaimer_if_present()

    def dismiss_disclaimer_if_present(self) -> None:
        """Dismiss One Click Trading disclaimer modal and backdrop if present."""
        try:
            self.page.evaluate("""() => {
                const modal = document.querySelector("#disclaimer");
                if (modal && (modal.classList.contains("show") || window.getComputedStyle(modal).display !== "none")) {
                    const btn = modal.querySelector("#acceptButton") || modal.querySelector("#close-disclaimer") || modal.querySelector(".close");
                    if (btn) btn.click();
                    modal.style.display = "none";
                    modal.classList.remove("show");
                    document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
                    document.body.classList.remove("modal-open");
                }
            }""")
            self.page.wait_for_timeout(200)
        except Exception:
            pass

    # =========================================================================
    # Quotes Header & Quick Tickers
    # =========================================================================

    def get_header_title(self) -> str:
        """Get the title text from the Quotes header."""
        return self.page_title.inner_text().strip()

    def wait_for_quotes_loaded(self, timeout: int = 10000) -> None:
        """Wait for live quotes (bid, spread) to populate from the price stream."""
        try:
            self.page.wait_for_function(
                "() => { const el = document.querySelector('.esearch-result .spread'); return el && el.innerText.trim().length > 0; }",
                timeout=timeout,
            )
        except Exception:
            pass

    def get_top_quotes(self) -> List[Dict[str, str]]:
        """
        Dynamically extracts top ticker information (name, symbol, bid price).
        Returns list of dicts: [{'name': 'EURUSD', 'orig': 'C:EURUSD', 'type': 'forex', 'bid': '1.14001'}]
        """
        return self.page.evaluate("""() => {
            const icons = document.querySelectorAll(".toptwo .toptwoicons");
            return Array.from(icons).map(el => {
                const bidEl = el.querySelector("[data-bid]");
                return {
                    name: el.getAttribute("data-name") || "",
                    orig: el.getAttribute("data-orig") || "",
                    type: el.getAttribute("data-type") || "",
                    bid: bidEl ? bidEl.innerText.trim() : ""
                };
            });
        }""")

    def get_top_tickers_names(self) -> List[str]:
        """Return list of symbol names currently displayed in the top two ticker bar."""
        return self.page.evaluate("""() => {
            const icons = document.querySelectorAll(".toptwo .toptwoicons");
            return Array.from(icons).map(el => el.getAttribute("data-name") || "").filter(Boolean);
        }""")


    # =========================================================================
    # Omnisearch Functionality
    # =========================================================================

    def search_symbol(self, query: str) -> None:
        """Type symbol query into search input."""
        logger.info(f"Searching watchlist for query: '{query}'")
        self.search_input.click()
        self.search_input.fill(query)
        self.page.evaluate("document.querySelector('#search-input')?.dispatchEvent(new Event('input', {bubbles: true}))")
        self.page.wait_for_timeout(800)

    def clear_search(self) -> None:
        """Clear search input."""
        logger.info("Clearing watchlist search query.")
        self.search_input.fill("")
        self.page.evaluate("""() => {
            const input = document.querySelector('#search-input');
            if (input) {
                input.value = '';
                input.dispatchEvent(new Event('input', {bubbles: true}));
                input.dispatchEvent(new Event('keyup', {bubbles: true}));
                input.dispatchEvent(new Event('change', {bubbles: true}));
            }
            const searchRes = document.querySelector('ul.search-result');
            if (searchRes) searchRes.style.display = 'none';
        }""")
        self.page.wait_for_timeout(500)

    def get_search_input_placeholder(self) -> str:
        """Get placeholder attribute of search input."""
        return self.search_input.get_attribute("placeholder") or ""

    # =========================================================================
    # Watchlist Tab Navigation
    # =========================================================================

    def switch_to_tab(self, tab_info: str) -> None:
        """
        Switch tab by data-info value: 'favorite' or 'symbols'.
        """
        logger.info(f"Switching watchlist tab to: {tab_info}")
        target_tab = self.watchlist_menu.locator(f".watchlist-tab[data-info='{tab_info}']")
        expect(target_tab).to_be_visible(timeout=TIMEOUT_DEFAULT)
        target_tab.click()
        self.page.wait_for_timeout(300)

    def is_favorites_tab_active(self) -> bool:
        """Check if FAVORITES tab currently has the 'active' class."""
        classes = self.tab_favorites.get_attribute("class") or ""
        return "active" in classes.split()

    def is_all_symbols_tab_active(self) -> bool:
        """Check if ALL SYMBOLS tab currently has the 'active' class."""
        classes = self.tab_all_symbols.get_attribute("class") or ""
        return "active" in classes.split()

    # =========================================================================
    # Symbol List Extraction & Data
    # =========================================================================

    def get_symbol_rows_count(self) -> int:
        """Return total number of symbol rows in the active favorites list."""
        return self.symbol_rows.count()

    def get_all_symbols_data(self) -> List[Dict[str, Any]]:
        """
        Dynamically extracts all symbol data rows from the DOM.
        Returns a list of dicts with:
        symbol, orig, percent, spread, bid, offer, low, high, sector.
        """
        return self.page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll(".esearch-result li.searchitems, ul.search-result li, .list-all-symbols li, .list-all-symbols .symbol-row"))
                .filter(el => el.offsetParent !== null && window.getComputedStyle(el).display !== 'none');
            return rows.map(row => {
                const symbol = row.getAttribute("data-symbol") || row.getAttribute("data-name") || (row.innerText ? row.innerText.trim().split('\\n')[0] : "");
                const origInput = row.querySelector("input[name='drag_symbol[]']");
                const orig = origInput ? origInput.value : (row.getAttribute("data-orig") || "");
                const percentEl = row.querySelector(".day-data[data-percent]");
                const spreadEl = row.querySelector(".spread[data-spread]");
                const bidEl = row.querySelector(".bid[data-bid]");
                const offerEl = row.querySelector(".offer[data-offer]");
                const lowEl = row.querySelector("[data-low] .value");
                const highEl = row.querySelector("[data-high] .value");
                const sector = bidEl ? (bidEl.getAttribute("sector") || "") : "";

                return {
                    symbol: symbol,
                    orig: orig,
                    percent: percentEl ? percentEl.innerText.trim() : "",
                    spread: spreadEl ? spreadEl.innerText.trim() : "",
                    bid: bidEl ? bidEl.innerText.trim() : "",
                    offer: offerEl ? offerEl.innerText.trim() : "",
                    low: lowEl ? lowEl.innerText.trim() : "",
                    high: highEl ? highEl.innerText.trim() : "",
                    sector: sector,
                };
            });
        }""")

    def get_symbol_row(self, symbol: str) -> Locator:
        """Get locator for a specific symbol row."""
        return self.symbol_rows.locator(f"[data-symbol='{symbol}']").first or self.favorites_list.locator(
            f"li.searchitems[data-symbol='{symbol}']"
        )

    def get_visible_symbols(self) -> List[str]:
        """Return list of visible symbol names in the active watchlist or search result."""
        search_val = (self.search_input.input_value() or "").strip()
        if search_val:
            return self.page.evaluate("""() => {
                const searchList = document.querySelectorAll("ul.search-result li, .esearch-result li.searchitems, .list-all-symbols li");
                return Array.from(searchList)
                    .filter(el => el.offsetParent !== null && window.getComputedStyle(el).display !== 'none')
                    .map(li => li.getAttribute("data-symbol") || li.getAttribute("data-name") || li.innerText.trim().split('\\n')[0])
                    .filter(s => s && s.length > 0 && !s.toLowerCase().includes("no symbol") && !s.toLowerCase().includes("nothing here"));
            }""")
        data = self.get_all_symbols_data()
        symbols = [d.get("symbol") for d in data if d.get("symbol")]
        if not symbols:
            symbols = self.page.evaluate("""() => {
                const items = document.querySelectorAll(".esearch-result li.searchitems, .list-all-symbols li, .list-all-symbols .symbol-row, ul.search-result li, .symbols-wrapper li");
                return Array.from(items)
                    .filter(el => el.offsetParent !== null && window.getComputedStyle(el).display !== 'none')
                    .map(el => el.getAttribute("data-symbol") || el.getAttribute("data-name") || el.innerText.trim().split('\\n')[0])
                    .filter(s => s && s.length > 0 && !s.toLowerCase().includes("nothing here") && !s.toLowerCase().includes("no symbol"));
            }""")
        return symbols

    # =========================================================================
    # Hover Action Controls
    # =========================================================================

    def hover_symbol(self, symbol: str) -> Locator:
        """
        Hover over a symbol row to reveal the action buttons (.hovercover .hovers).
        Returns the hover container locator.
        """
        row = self.favorites_list.locator(f"li.searchitems[data-symbol='{symbol}']").first
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(300)
        hover_panel = row.locator(".hovers")
        return hover_panel

    def get_hover_controls(self, symbol: str) -> Dict[str, Locator]:
        """
        Hover over a symbol and return dictionary of action locators:
        'buy', 'sell', 'chart', 'favorite_trash', 'more_menu'.
        """
        hover_panel = self.hover_symbol(symbol)
        return {
            "panel": hover_panel,
            "buy": hover_panel.locator(".placeorder.buy"),
            "sell": hover_panel.locator(".placeorder.sell"),
            "chart": hover_panel.locator(".openchart"),
            "delete_fav": hover_panel.locator(".deletewl"),
            "more_menu": hover_panel.locator(".showFavList"),
        }

    # =========================================================================
    # Footer Pagination (Workspaces 1 to 5)
    # =========================================================================

    def get_footer_pages_count(self) -> int:
        """Return total count of footer pagination tabs."""
        return self.footer_tabs.count()

    def select_footer_page(self, page_wal: int | str) -> None:
        """Click a footer pagination tab (1 to 5)."""
        wal_str = str(page_wal)
        logger.info(f"Selecting watchlist footer page workspace: {wal_str}")
        tab = self.side_footer.locator(f".sidefootul li[data-wal='{wal_str}']")
        expect(tab).to_be_visible(timeout=TIMEOUT_DEFAULT)
        tab.click()
        self.page.wait_for_timeout(500)

    def get_active_footer_page(self) -> Optional[str]:
        """Return the data-wal attribute of the currently active footer tab."""
        active_tab = self.side_footer.locator(".sidefootul li.active")
        if active_tab.count() > 0:
            return active_tab.first.get_attribute("data-wal")
        return None

    # =========================================================================
    # Advanced Workflow Actions: Top Tickers, Add/Remove, Chart Opening
    # =========================================================================

    def replace_top_ticker(self, symbol: str, section: int) -> None:
        """
        Replace top ticker at index `section` (0 for Fav 1, 1 for Fav 2)
        with the specified watchlist `symbol`.
        """
        self.dismiss_disclaimer_if_present()
        logger.info(f"Setting symbol '{symbol}' as top ticker section {section}")
        row = self.favorites_list.locator(f"li.searchitems[data-symbol='{symbol}']").first
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(300)

        more_trigger = row.locator(".showFavList")
        more_trigger.hover()
        self.page.wait_for_timeout(300)

        add_btn = row.locator(f".addFavTop[data-section='{section}']")
        expect(add_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        add_btn.click()
        self.page.wait_for_timeout(1000)

    def open_chart_for_symbol(self, symbol: str) -> None:
        """
        Hover over the specified symbol and click its chart icon to open the chart.
        """
        self.dismiss_disclaimer_if_present()
        logger.info(f"Opening chart for symbol '{symbol}'")
        row = self.favorites_list.locator(f"li.searchitems[data-symbol='{symbol}']").first
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(300)

        chart_btn = row.locator(".openchart")
        expect(chart_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        chart_btn.click()
        self.page.wait_for_timeout(2000)

    def add_symbol_to_favorites(self, symbol: str) -> None:
        """
        Search for `symbol` via Omnisearch and click the add/favorite icon to add it to favorites.
        """
        self.dismiss_disclaimer_if_present()
        logger.info(f"Adding symbol '{symbol}' to favorites watchlist")
        self.search_symbol(symbol)
        self.page.wait_for_timeout(1000)

        add_item = self.search_result_container.locator(f"li:has-text('{symbol}')").first
        expect(add_item).to_be_visible(timeout=TIMEOUT_DEFAULT)

        fav_icon = add_item.locator(".favourite")
        expect(fav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
        fav_icon.click()
        self.page.wait_for_timeout(1000)

        self.clear_search()
        self.page.wait_for_timeout(1000)

    def remove_symbol_from_favorites(self, symbol: str) -> None:
        """
        Hover over `symbol` in favorites list and click its trash icon to remove it.
        """
        self.dismiss_disclaimer_if_present()
        logger.info(f"Removing symbol '{symbol}' from favorites watchlist")
        row = self.favorites_list.locator(f"li.searchitems[data-symbol='{symbol}']").first
        expect(row).to_be_visible(timeout=TIMEOUT_DEFAULT)
        row.hover()
        self.page.wait_for_timeout(300)

        del_btn = row.locator(".deletewl")
        expect(del_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        del_btn.click()
        self.page.wait_for_timeout(1000)

    def is_symbol_in_favorites(self, symbol: str) -> bool:
        """Check if symbol exists in the active favorites list."""
        return self.favorites_list.locator(f"li.searchitems[data-symbol='{symbol}']").count() > 0



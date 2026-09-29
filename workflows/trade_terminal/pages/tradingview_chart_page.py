"""
Trade Terminal TradingView Chart Page Object.
Dedicated Page Object model for the embedded TradingView Chart engine:
- Top bar: Symbol search, compare, timeframe intervals, chart styles, indicators, layouts, settings, fullscreen, snapshots
- Left drawing tools toolbar
- Bottom time scale & right price axis
- Interactive chart canvas and studies
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import FrameLocator, Locator, Page, expect

from config.settings import settings
from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT, TIMEOUT_SHORT
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("tradingview_chart_page")


class TradingViewChartPage(BasePage):
    """Page Object dedicated exclusively to the TradingView Chart engine and top bar."""

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Main Workspace Containers
        self.chart_page_container: Locator = page.locator(
            "body > div.body > div.main > div.rightbar > section > div:nth-child(3)"
        )
        self.chart_top_pane: Locator = page.locator(
            "#app > div > div > div.div1.initialHeight, .div1.initialHeight, .div1"
        )
        self.tv_container: Locator = page.locator("#tv_chart_container")
        self.tv_iframe_locator: Locator = page.locator("#tv_chart_container iframe")
        self.tv_iframe: FrameLocator = page.frame_locator("#tv_chart_container iframe")
        self.chart_nav_icon: Locator = page.locator(".lefticons[data-tooltip='Chart']")

        # 2. Profile Menu Chart Toggle Controls
        self.profile_icon: Locator = page.locator(
            "body > div.body > div.leftbar > div.leftlist.pcview > div.lefticons.toplefticon.toggleLeftMenu, "
            ".lefticons.toplefticon.toggleLeftMenu, .toggleLeftMenu"
        ).first
        self.profile_menu: Locator = page.locator("#targetmenu.newmenu, #targetmenu")
        self.profile_tv_btn: Locator = self.profile_menu.locator(".chart-btn.tradingView")

        # 3. TradingView Top Bar Elements
        self.top_bar: Locator = self.tv_iframe.locator("div.layout__area--top").first
        self.symbol_search_btn: Locator = self.tv_iframe.locator("div.layout__area--top #header-toolbar-symbol-search, div.layout__area--top button[aria-label='Symbol Search']").last
        self.compare_btn: Locator = self.tv_iframe.locator("div.layout__area--top #header-toolbar-compare, div.layout__area--top button[aria-label='Compare or Add Symbol']").last
        self.interval_menu_btn: Locator = self.tv_iframe.locator(
            "div.layout__area--top button.menu-S_1OCXUK, div.layout__area--top button[aria-label*='minute'], div.layout__area--top button[aria-label*='hour'], div.layout__area--top button[aria-label*='day']"
        ).last
        self.chart_style_btn: Locator = self.tv_iframe.locator(
            "div.layout__area--top button.menu-b3Cgff6l, div.layout__area--top button[aria-label*='Candles'], div.layout__area--top button[aria-label*='Bars'], div.layout__area--top button[aria-label*='Line']"
        ).last
        self.indicators_btn: Locator = self.tv_iframe.locator(
            "div.layout__area--top button[data-name='open-indicators-dialog'], div.layout__area--top button[aria-label='Indicators & Strategies']"
        ).last
        self.templates_btn: Locator = self.tv_iframe.locator("div.layout__area--top button[aria-label='Indicator Templates']").last
        self.save_load_btn: Locator = self.tv_iframe.locator("div.layout__area--top #header-toolbar-save-load").last
        self.save_load_menu_btn: Locator = self.tv_iframe.locator("div.layout__area--top button[data-name='save-load-menu']").last
        self.settings_btn: Locator = self.tv_iframe.locator("div.layout__area--top button[data-name='header-toolbar-properties'], div.layout__area--top button[aria-label='Chart settings']").last
        self.fullscreen_btn: Locator = self.tv_iframe.locator("div.layout__area--top button[data-name='header-toolbar-fullscreen'], div.layout__area--top button[aria-label='Fullscreen mode']").last
        self.snapshot_btn: Locator = self.tv_iframe.locator("div.layout__area--top button[aria-label='Take a snapshot'], div.layout__area--top #header-toolbar-screenshot").last

        # 4. Modals & Dialogs inside TradingView IFrame
        self.symbol_search_dialog: Locator = self.tv_iframe.locator("[data-name='symbol-search-dialog'], [data-dialog-name='Symbol Search']")
        self.symbol_search_input: Locator = self.tv_iframe.locator("[data-name='symbol-search-dialog'] input, input[data-role='search'], input[type='text']").first

        # 5. Drawing Sidebar Elements (JS Path: #drawing-toolbar > div > div > div)
        self.drawing_toolbar: Locator = self.tv_iframe.locator("#drawing-toolbar > div > div > div, #drawing-toolbar")
        self.cursor_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Cross'], button[aria-label*='Dot'], button[aria-label*='Arrow'], button[aria-label*='Eraser']").first
        self.trendline_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Trend Line'], button[aria-label*='Line']").first
        self.fib_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Fib Retracement'], button[aria-label*='Gann']").first
        self.brush_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Brush'], button[aria-label*='Rectangle'], button[aria-label*='Highlighter']").first
        self.text_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Text'], button[aria-label*='Note']").first
        self.pattern_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Pattern'], button[aria-label*='XABCD']").first
        self.forecast_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Position'], button[aria-label*='Forecast']").first
        self.icon_tool_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Icon']").first
        self.measure_tool_btn: Locator = self.drawing_toolbar.locator("button[data-name='measure'], button[aria-label='Measure']")
        self.zoom_tool_btn: Locator = self.drawing_toolbar.locator("button[data-name='zoom'], button[aria-label='Zoom In']")
        self.magnet_toggle_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Magnet Mode']")
        self.drawing_mode_toggle_btn: Locator = self.drawing_toolbar.locator("button[data-name='drawginmode'], button[aria-label*='Stay in Drawing Mode']")
        self.lock_tools_toggle_btn: Locator = self.drawing_toolbar.locator("button[data-name='lockAllDrawings'], button[aria-label*='Lock All Drawing Tools']")
        self.hide_drawings_toggle_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Hide all drawings']")
        self.remove_drawings_btn: Locator = self.drawing_toolbar.locator("button[aria-label*='Remove']")
        self.object_tree_btn: Locator = self.drawing_toolbar.locator("button[data-name='showObjectsTree'], button[aria-label*='Object Tree']")
        self.indicators_dialog: Locator = self.tv_iframe.locator("[data-name='indicators-dialog'], [data-dialog-name='Indicators & Strategies']")
        self.indicators_search_input: Locator = self.tv_iframe.locator("[data-name='indicators-dialog'] input, input[data-role='search']").first
        self.chart_properties_dialog: Locator = self.tv_iframe.locator("[data-name='chart-properties-dialog'], [data-dialog-name='Chart settings']")

        # 5. TradingView Bottom Toolbar Controls
        self.bottom_bar: Locator = self.tv_iframe.locator(
            "div.chart-toolbar.chart-controls-bar, .chart-controls-bar"
        ).first
        self.date_range_tabs: Locator = self.bottom_bar.locator("button[data-name*='date-range-tab']")
        self.goto_date_btn: Locator = self.bottom_bar.locator("button[data-name='go-to-date']")
        self.timezone_btn: Locator = self.bottom_bar.locator("button[data-name='time-zone-menu']")
        self.percentage_toggle_btn: Locator = self.bottom_bar.locator("button[data-name='percentage']")
        self.logarithm_toggle_btn: Locator = self.bottom_bar.locator("button[data-name='logarithm']")
        self.auto_scale_toggle_btn: Locator = self.bottom_bar.locator("button[data-name='auto']")

        # 6. Chart Canvas, Legend, Quick Trading & Control Bar
        self.chart_pane: Locator = self.tv_iframe.locator("td.chart-markup-table.pane")
        self.chart_legend: Locator = self.tv_iframe.locator("div[class*='legend-'], .legend-l31H9iuA").first
        self.quick_trade_buy_btn: Locator = self.tv_iframe.locator("td.chart-markup-table.pane button:has-text('BUY')").first
        self.quick_trade_sell_btn: Locator = self.tv_iframe.locator("td.chart-markup-table.pane button:has-text('SELL')").first
        self.quick_trade_lot_input: Locator = self.tv_iframe.locator("#trade-lot-size")
        self.control_bar_wrapper: Locator = self.tv_iframe.locator("div.control-bar-wrapper")
        self.reset_chart_view_btn: Locator = self.control_bar_wrapper.locator(".js-btn-reset, div[title*='Reset']")

    # =========================================================================
    # Navigation & Lifecycle
    # =========================================================================

    def navigate_to_chart(self, url: Optional[str] = None) -> None:
        """Navigate to dashboard and activate TradingView Chart workspace."""
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard for TradingView Chart: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()

        if not self.chart_page_container.is_visible() or not self.is_chart_nav_active():
            logger.info("Activating Chart workspace via left sidebar...")
            expect(self.chart_nav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.chart_nav_icon.click()
            self.page.wait_for_timeout(1000)

        self.ensure_tradingview_active()
        self.dismiss_disclaimer_if_present()

    def is_chart_nav_active(self) -> bool:
        """Return True if left sidebar Chart icon has 'active' class."""
        classes = self.chart_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

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

    def ensure_tradingview_active(self, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Ensure TradingView engine is the active chart engine."""
        if not self.tv_container.is_visible():
            logger.info("TradingView is not active. Switching to TradingView via profile menu...")
            self.profile_icon.click()
            self.page.wait_for_timeout(500)
            expect(self.profile_tv_btn).to_be_visible(timeout=timeout)
            self.profile_tv_btn.click()
            self.page.wait_for_timeout(1000)
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)

        expect(self.tv_container).to_be_visible(timeout=timeout)
        expect(self.tv_iframe_locator).to_be_visible(timeout=timeout)

    # =========================================================================
    # Top Bar: Symbol Search & Changing Symbols
    # =========================================================================

    def get_active_symbol(self) -> str:
        """Return the active symbol displayed in the TradingView top bar."""
        expect(self.symbol_search_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.symbol_search_btn.inner_text().strip()

    def open_symbol_search(self) -> None:
        """Open the Symbol Search dialog by clicking the symbol button in the top bar."""
        logger.info("Opening TradingView symbol search dialog...")
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const btn = body.querySelector("#header-toolbar-symbol-search");
            if (btn) btn.click();
        }""")
        self.page.wait_for_timeout(800)

    def close_dialog(self) -> None:
        """Close any open dialog inside the iframe or via Escape."""
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const closeBtn = body.querySelector("[data-name='close'], [data-role='button'][aria-label='Close'], button.close-BZKENkhT, button[class*='close-']");
            if (closeBtn) {
                closeBtn.click();
            } else {
                body.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true }));
            }
        }""")
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def search_and_change_symbol(self, symbol: str, timeout: int = TIMEOUT_DEFAULT) -> str:
        """
        Search for `symbol` in TradingView and select it.
        Returns the new active symbol text.
        """
        logger.info(f"Changing TradingView symbol to: {symbol}")
        self.open_symbol_search()

        search_input = self.tv_iframe.locator(
            "[data-name='symbol-search-dialog'] input, input[data-role='search'], input[type='text']"
        ).first
        expect(search_input).to_be_visible(timeout=timeout)
        search_input.fill("")
        search_input.fill(symbol)
        self.page.wait_for_timeout(800)

        # Click the first matching search result item
        item = self.tv_iframe.locator(
            f"[data-name='symbol-search-dialog'] [data-role='list-item']:has-text('{symbol}'), "
            f"[data-role='list-item']:has-text('{symbol}'), "
            f".item-jFqVJoPk:has-text('{symbol}')"
        ).first
        if item.count() > 0:
            item.click()
        else:
            self.page.keyboard.press("Enter")

        self.page.wait_for_timeout(1500)
        self.dismiss_disclaimer_if_present()
        return self.get_active_symbol()

    # =========================================================================
    # Top Bar: Timeframe / Interval Switching
    # =========================================================================

    def open_interval_dropdown(self) -> None:
        """Click timeframe dropdown button in top bar."""
        logger.info("Opening TradingView timeframe interval menu...")
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const topBar = body.querySelector("div.layout__area--top");
            const intervalBtn = topBar.querySelector("button.menu-S_1OCXUK, button[aria-label*='minute'], button[aria-label*='hour'], button[aria-label*='day']");
            if (intervalBtn) intervalBtn.click();
        }""")
        self.page.wait_for_timeout(600)

    def get_available_intervals(self) -> List[Dict[str, str]]:
        """
        Return list of all intervals available in the dropdown menu.
        [{'text': '1 minute', 'value': '1'}, {'text': '5 minutes', 'value': '5'}, ...]
        """
        self.open_interval_dropdown()
        items = self.tv_iframe.locator("body").evaluate("""(body) => {
            const nodes = Array.from(body.querySelectorAll("[data-name='menu-inner'] [data-role='menuitem'], [data-name='menu-inner'] .item-jFqVJoPk"));
            return nodes.map(n => ({
                text: n.innerText ? n.innerText.trim().replace(/\\n/g, ' ') : "",
                value: n.getAttribute("data-value") || "",
                ariaLabel: n.getAttribute("aria-label") || ""
            })).filter(n => n.text.length > 0);
        }""")
        self.close_dialog()
        return items

    def select_interval(self, interval_label: str) -> None:
        """
        Select a timeframe interval (e.g. '1 minute', '5 minutes', '15 minutes', '1 hour', '1 day').
        """
        logger.info(f"Selecting TradingView timeframe interval: {interval_label}")
        self.open_interval_dropdown()
        self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const nodes = Array.from(body.querySelectorAll("[data-name='menu-inner'] [data-role='menuitem'], [data-name='menu-inner'] .item-jFqVJoPk"));
            const target = nodes.find(n => n.innerText.toLowerCase().includes('{interval_label.lower()}') || n.getAttribute('aria-label')?.toLowerCase().includes('{interval_label.lower()}'));
            if (target) target.click();
        }}""")
        self.page.wait_for_timeout(1000)

    def get_active_interval_text(self) -> str:
        """Return the active interval label or button text."""
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const topBar = body.querySelector("div.layout__area--top");
            const intervalBtn = topBar.querySelector("button[aria-label*='minute'], button[aria-label*='hour'], button[aria-label*='day']");
            return intervalBtn ? (intervalBtn.getAttribute("aria-label") || intervalBtn.innerText.trim()) : "";
        }""")

    # =========================================================================
    # Top Bar: Chart Styles / Type Selector
    # =========================================================================

    def open_chart_style_dropdown(self) -> None:
        """Click chart style dropdown in top bar."""
        logger.info("Opening TradingView chart style menu...")
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const topBar = body.querySelector("div.layout__area--top");
            const styleBtn = topBar.querySelector("button.menu-b3Cgff6l, button[aria-label*='Candles'], button[aria-label*='Bars'], button[aria-label*='Line'], button[aria-label*='Area']");
            if (styleBtn) styleBtn.click();
        }""")
        self.page.wait_for_timeout(600)

    def get_available_chart_styles(self) -> List[Dict[str, Any]]:
        """
        Return list of all chart styles:
        [{'text': 'Bars', 'value': 'bar'}, {'text': 'Candles', 'value': 'candle'}, ...]
        """
        self.open_chart_style_dropdown()
        items = self.tv_iframe.locator("body").evaluate("""(body) => {
            const nodes = Array.from(body.querySelectorAll("[data-name='menu-inner'] [data-role='menuitem'], [data-name='menu-inner'] .item-jFqVJoPk"));
            return nodes.map(n => ({
                text: n.innerText ? n.innerText.trim().replace(/\\n/g, ' ') : "",
                value: n.getAttribute("data-value") || "",
                isActive: n.classList.contains("isActive-jFqVJoPk") || n.classList.contains("active-NQERJsv9")
            })).filter(n => n.text.length > 0);
        }""")
        self.close_dialog()
        return items

    def select_chart_style(self, style_name: str) -> None:
        """
        Select a chart style (e.g. 'Candles', 'Bars', 'Line', 'Area', 'Heikin Ashi', 'Hollow candles').
        """
        logger.info(f"Selecting TradingView chart style: {style_name}")
        self.open_chart_style_dropdown()
        self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const nodes = Array.from(body.querySelectorAll("[data-name='menu-inner'] [data-role='menuitem'], [data-name='menu-inner'] .item-jFqVJoPk"));
            const target = nodes.find(n => n.innerText.toLowerCase().includes('{style_name.lower()}') || (n.getAttribute('data-value') || '').toLowerCase().includes('{style_name.lower()}'));
            if (target) target.click();
        }}""")
        self.page.wait_for_timeout(1000)

    # =========================================================================
    # Top Bar: Indicators Dialog & Application
    # =========================================================================

    def open_indicators_dialog(self) -> None:
        """Open the Indicators & Strategies modal dialog."""
        logger.info("Opening TradingView indicators dialog...")
        btn = self.tv_iframe.locator(
            "div.layout__area--top button[data-name='open-indicators-dialog'], div.layout__area--top button[aria-label='Indicators & Strategies']"
        ).last
        btn.evaluate("b => b.click()")
        self.page.wait_for_timeout(1000)

    def search_and_add_indicator(self, indicator_name: str, timeout: int = TIMEOUT_DEFAULT) -> bool:
        """
        Search for `indicator_name` (e.g. 'Relative Strength Index', 'Moving Average')
        and click to apply it to the chart.
        """
        logger.info(f"Adding indicator to chart: {indicator_name}")
        self.open_indicators_dialog()

        # Find and fill search input inside the opened indicators dialog
        search_input = self.tv_iframe.locator(
            "[data-name='indicators-dialog'] input, [data-dialog-name='Indicators'] input"
        ).first
        search_input.wait_for(timeout=5000)
        search_input.fill(indicator_name)
        self.page.wait_for_timeout(800)

        # Click matching item in list
        item_clicked = self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const dialog = body.querySelector("[data-name='indicators-dialog'], [data-dialog-name='Indicators']");
            if (!dialog) return false;
            const items = Array.from(dialog.querySelectorAll("[data-role='list-item']"));
            const target = items.find(i => i.innerText.trim().toLowerCase().includes('{indicator_name.lower()}'));
            if (target) {{
                target.click();
                return true;
            }}
            if (items.length > 0) {{
                items[0].click();
                return true;
            }}
            return false;
        }}""")

        self.page.wait_for_timeout(600)
        self.close_dialog()
        self.page.wait_for_timeout(1000)
        return item_clicked

    def get_study_legend_titles(self) -> List[str]:
        """Return list of indicator study names rendered on the chart canvas legends."""
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const legends = Array.from(body.querySelectorAll(
                ".sources-Ymshn_1t, .titlesWrapper-cq__ntSC, [data-name='legend-source-title'], .study-title, [data-name='legend-series-title']"
            ));
            return legends.map(l => l.innerText ? l.innerText.trim() : "").filter(t => t.length > 0);
        }""")

    # =========================================================================
    # Top Bar: Compare / Add Symbol Dialog
    # =========================================================================

    def open_compare_dialog(self) -> None:
        """Open the Compare / Add Symbol dialog."""
        logger.info("Opening TradingView Compare dialog...")
        btn = self.tv_iframe.locator(
            "div.layout__area--top #header-toolbar-compare, div.layout__area--top button[aria-label='Compare or Add Symbol']"
        ).last
        btn.evaluate("b => b.click()")
        self.page.wait_for_timeout(800)

    # =========================================================================
    # Top Bar: Chart Settings / Properties Modal
    # =========================================================================

    def open_chart_settings_dialog(self) -> None:
        """Open the Chart Properties / Settings modal dialog."""
        logger.info("Opening TradingView Chart settings dialog...")
        btn = self.tv_iframe.locator(
            "div.layout__area--top button[data-name='header-toolbar-properties'], div.layout__area--top button[aria-label='Chart settings']"
        ).last
        btn.evaluate("b => b.click()")
        self.page.wait_for_timeout(1000)

    def get_settings_dialog_tabs(self) -> List[str]:
        """Return list of tab names inside the Chart Settings modal (e.g. Symbol, Status line, Scales, Canvas)."""
        self.open_chart_settings_dialog()
        tabs = self.tv_iframe.locator("body").evaluate("""(body) => {
            const dialog = body.querySelector("[data-name='series-properties-dialog'], [data-dialog-name='Chart settings'], div.dialog-qyCw0PaN");
            if (!dialog) return [];
            const tabEls = Array.from(dialog.querySelectorAll("button[class*='tab-'], [class*='tab-nGEmjtaX']"));
            return tabEls.map(t => t.innerText ? t.innerText.trim() : "").filter(t => t.length > 0 && !t.includes('\\n'));
        }""")
        self.close_dialog()
        return tabs

    def switch_settings_tab(self, tab_name: str) -> bool:
        """Switch to a specific tab in the settings dialog."""
        logger.info(f"Switching settings tab to: {tab_name}")
        self.open_chart_settings_dialog()
        switched = self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const dialog = body.querySelector("[data-name='series-properties-dialog'], [data-dialog-name='Chart settings'], div.dialog-qyCw0PaN");
            if (!dialog) return false;
            const tabs = Array.from(dialog.querySelectorAll("button[class*='tab-'], [class*='tab-nGEmjtaX']"));
            const target = tabs.find(t => t.innerText.trim().toLowerCase() === '{tab_name.lower()}');
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }}""")
        self.page.wait_for_timeout(600)
        self.close_dialog()
        return switched

    # =========================================================================
    # Top Bar: Fullscreen & Snapshot Actions
    # =========================================================================

    def toggle_fullscreen(self) -> None:
        """Click fullscreen button in top bar."""
        logger.info("Toggling TradingView fullscreen mode...")
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const btn = body.querySelector("button[data-name='header-toolbar-fullscreen']");
            if (btn) btn.click();
        }""")
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def click_snapshot(self) -> None:
        """Click snapshot button in top bar."""
        logger.info("Clicking TradingView snapshot button...")
        self.tv_iframe.locator("body").evaluate("""(body) => {
            const btn = body.querySelector("button[aria-label='Take a snapshot'], #header-toolbar-screenshot");
            if (btn) btn.click();
        }""")
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    # =========================================================================
    # Drawing Sidebar: JS Path: #drawing-toolbar > div > div > div
    # =========================================================================

    def get_drawing_sidebar_tools(self) -> List[Dict[str, Any]]:
        """Return list of all tool buttons present in the drawing toolbar."""
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            if (!root) return [];
            const buttons = Array.from(root.querySelectorAll("button"));
            return buttons.map(b => ({
                ariaLabel: b.getAttribute('aria-label') || "",
                dataTooltip: b.getAttribute('data-tooltip') || "",
                dataName: b.getAttribute('data-name') || "",
                ariaPressed: b.getAttribute('aria-pressed'),
                isActive: b.className.includes('isActive') || b.getAttribute('aria-pressed') === 'true',
                visible: b.offsetWidth > 0 && b.offsetHeight > 0
            })).filter(b => b.visible);
        }""")

    def open_tool_group_menu(self, group_name: str) -> bool:
        """
        Click flyout arrow for tool group (e.g. 'Cursors', 'Trend line tools',
        'Gann and Fibonacci tools', 'Geometric shapes', 'Annotation tools',
        'Patterns', 'Forecasting and measurement tools', 'Icons').
        """
        logger.info(f"Opening drawing tool group flyout: {group_name}")
        # Dismiss any open menu first
        self.tv_iframe.locator("body").press("Escape")
        self.page.wait_for_timeout(300)

        opened = self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            if (!root) return false;
            const arrows = Array.from(root.querySelectorAll("button.arrow-pbhJWNrt, button[aria-label]"));
            const target = arrows.find(a => a.getAttribute('aria-label')?.toLowerCase().includes('{group_name.lower()}'));
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }}""")
        self.page.wait_for_timeout(500)
        return opened

    def get_available_subtools(self) -> List[str]:
        """Return list of subtool names in the currently opened flyout menu."""
        return self.tv_iframe.locator("body").evaluate("""() => {
            const menu = document.querySelector("[data-name='menu-inner'], div[class*='menuWrap-']");
            if (!menu) return [];
            const items = Array.from(menu.querySelectorAll("[data-role='menuitem'], div[class*='item-'], button[class*='item-']"));
            return items.map(i => i.innerText.trim().split('\\n')[0]).filter(t => t.length > 0);
        }""")

    def select_subtool(self, group_name: str, subtool_name: str) -> bool:
        """
        Open `group_name` flyout and select `subtool_name` (e.g. 'Horizontal Line', 'Highlighter', 'Note').
        """
        logger.info(f"Selecting subtool '{subtool_name}' from group '{group_name}'...")
        # 1. Dismiss any existing open popup
        self.tv_iframe.locator("body").press("Escape")
        self.page.wait_for_timeout(300)

        # 2. Open target group arrow
        self.tv_iframe.locator("body").evaluate(f"""(body) => {{
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            if (!root) return;
            const arrows = Array.from(root.querySelectorAll("button.arrow-pbhJWNrt, button[aria-label]"));
            const target = arrows.find(a => a.getAttribute('aria-label')?.toLowerCase().includes('{group_name.lower()}'));
            if (target) target.click();
        }}""")
        self.page.wait_for_timeout(500)

        # 3. Find and click subtool item in [data-name='menu-inner']
        clicked = self.tv_iframe.locator("body").evaluate(f"""() => {{
            const menu = document.querySelector("[data-name='menu-inner'], div[class*='menuWrap-']");
            if (!menu) return false;
            const items = Array.from(menu.querySelectorAll("[data-role='menuitem'], div[class*='item-'], button[class*='item-']"));
            const target = items.find(i => i.innerText.trim().toLowerCase().includes('{subtool_name.lower()}'));
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }}""")
        self.page.wait_for_timeout(500)
        return clicked

    def toggle_magnet_mode(self) -> Dict[str, Any]:
        """Toggle Magnet Mode and return before/after states."""
        logger.info("Toggling Magnet Mode...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[aria-label*='Magnet Mode']") : null;
            if (!btn) return { error: "Magnet button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def toggle_drawing_mode(self) -> Dict[str, Any]:
        """Toggle Stay in Drawing Mode and return before/after states."""
        logger.info("Toggling Stay in Drawing Mode...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[data-name='drawginmode'], button[aria-label*='Stay in Drawing Mode']") : null;
            if (!btn) return { error: "Drawing mode button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def toggle_lock_all_drawings(self) -> Dict[str, Any]:
        """Toggle Lock All Drawing Tools and return before/after states."""
        logger.info("Toggling Lock All Drawing Tools...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[data-name='lockAllDrawings'], button[aria-label*='Lock All Drawing Tools']") : null;
            if (!btn) return { error: "Lock button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def toggle_hide_drawings(self) -> Dict[str, Any]:
        """Toggle Hide All Drawings and return before/after states."""
        logger.info("Toggling Hide All Drawings...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[aria-label*='all drawings']") : null;
            if (!btn) return { error: "Hide all drawings button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def trigger_measure_mode(self) -> bool:
        """Activate Measure mode from sidebar."""
        logger.info("Activating Measure mode...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[data-name='measure'], button[aria-label='Measure']") : null;
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    def trigger_zoom_mode(self) -> bool:
        """Activate Zoom In mode from sidebar."""
        logger.info("Activating Zoom In mode...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[data-name='zoom'], button[aria-label='Zoom In']") : null;
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    def open_object_tree(self) -> bool:
        """Open the Object Tree dialog/sidebar panel."""
        logger.info("Opening Object Tree from sidebar...")
        return self.tv_iframe.locator("body").evaluate("""() => {
            const root = document.querySelector("#drawing-toolbar > div > div > div, #drawing-toolbar");
            const btn = root ? root.querySelector("button[data-name='showObjectsTree'], button[aria-label*='Object Tree']") : null;
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    # =========================================================================
    # Bottom Toolbar Controls (Date Range Presets, Go to Date, Timezone, Scales)
    # =========================================================================

    def get_bottombar_date_ranges(self) -> List[str]:
        """Return available date range preset labels on the bottom controls bar."""
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            if (!bar) return [];
            return Array.from(bar.querySelectorAll("button[data-name*='date-range-tab']")).map(b => b.innerText.trim());
        }""")

    def select_date_range_tab(self, range_label: str) -> bool:
        """Select a date range preset tab by label (e.g. '1D', '5D', '1M')."""
        logger.info(f"Selecting bottom bar date range preset: {range_label}")
        return self.tv_iframe.locator("body").evaluate("""(body, rangeLabel) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            if (!bar) return false;
            const tabs = Array.from(bar.querySelectorAll("button[data-name*='date-range-tab']"));
            const target = tabs.find(t => t.innerText && t.innerText.trim().toLowerCase() === rangeLabel.toLowerCase());
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""", range_label)

    def open_goto_date_dialog(self) -> bool:
        """Open the 'Go to Date' dialog from the bottom toolbar."""
        logger.info("Opening Go to Date dialog...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            const btn = bar ? bar.querySelector("button[data-name='go-to-date']") : null;
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    def set_goto_date(self, date_str: str, submit: bool = True) -> bool:
        """Fill date string in the Go to Date dialog and optionally submit."""
        logger.info(f"Setting Go to Date to: {date_str} (submit={submit})")
        return self.tv_iframe.locator("body").evaluate("""(body, options) => {
            const { dateStr, submit } = options;
            const dialog = body.querySelector("[data-name='go-to-date-dialog'], [data-dialog-name='Go to'], div[class*='dialog-']");
            if (!dialog) return false;
            const input = dialog.querySelector("input[type='text']");
            if (input) {
                input.value = dateStr;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (submit) {
                const submitBtn = dialog.querySelector("button[data-name='submit-button'], button[type='submit']");
                if (submitBtn) {
                    submitBtn.click();
                    return true;
                }
            }
            return true;
        }""", {"dateStr": date_str, "submit": submit})

    def get_active_timezone(self) -> str:
        """Return the active timezone string displayed on the bottom bar button."""
        expect(self.timezone_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.timezone_btn.inner_text().strip()

    def open_timezone_menu(self) -> bool:
        """Open the timezone selection menu from the bottom toolbar."""
        logger.info("Opening Timezone menu...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            const btn = bar ? bar.querySelector("button[data-name='time-zone-menu']") : null;
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    def get_available_timezones(self) -> List[str]:
        """Return list of timezone options from the open timezone dropdown."""
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const menu = body.querySelector("div[data-name='menu-inner'], div.menu-box");
            if (!menu) return [];
            return Array.from(menu.querySelectorAll("div[data-role='menuitem'], tr, div[class*='item-']"))
                .map(el => el.innerText ? el.innerText.trim() : "")
                .filter(t => t.length > 0);
        }""")

    def select_timezone(self, tz_name: str) -> bool:
        """Select a specific timezone option from the open dropdown menu."""
        logger.info(f"Selecting timezone: {tz_name}")
        return self.tv_iframe.locator("body").evaluate("""(body, targetTz) => {
            const menu = body.querySelector("div[data-name='menu-inner'], div.menu-box");
            if (!menu) return false;
            const items = Array.from(menu.querySelectorAll("div[data-role='menuitem'], tr, div[class*='item-']"));
            const target = items.find(el => el.innerText && el.innerText.trim().toLowerCase().includes(targetTz.toLowerCase()));
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""", tz_name)

    def toggle_percentage_scale(self) -> Dict[str, Any]:
        """Toggle Percentage scale mode and return before/after aria-pressed states."""
        logger.info("Toggling Percentage scale mode...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            const btn = bar ? bar.querySelector("button[data-name='percentage']") : null;
            if (!btn) return { error: "Percentage scale button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def toggle_log_scale(self) -> Dict[str, Any]:
        """Toggle Logarithmic scale mode and return before/after aria-pressed states."""
        logger.info("Toggling Logarithmic scale mode...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            const btn = bar ? bar.querySelector("button[data-name='logarithm']") : null;
            if (!btn) return { error: "Log scale button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    def toggle_auto_scale(self) -> Dict[str, Any]:
        """Toggle Auto scale mode and return before/after aria-pressed states."""
        logger.info("Toggling Auto scale mode...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const bar = body.querySelector("div.chart-toolbar.chart-controls-bar, .chart-controls-bar");
            const btn = bar ? bar.querySelector("button[data-name='auto']") : null;
            if (!btn) return { error: "Auto scale button not found" };
            const before = btn.getAttribute('aria-pressed');
            btn.click();
            const after = btn.getAttribute('aria-pressed');
            return { before, after, toggled: before !== after };
        }""")

    # =========================================================================
    # Chart Canvas, OHLC Dynamics, Quick Trading & Control Bar
    # =========================================================================

    def get_legend_ohlc_text(self) -> str:
        """Return the current OHLC legend text displayed on the chart pane."""
        expect(self.chart_legend).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.chart_legend.inner_text().strip()

    def hover_chart_at_fraction(self, x_fraction: float, y_fraction: float = 0.5) -> str:
        """
        Move mouse across chart canvas at relative fraction coordinates (0.0 to 1.0)
        and return the updated OHLC legend text.
        """
        expect(self.chart_pane).to_be_visible(timeout=TIMEOUT_DEFAULT)
        pane_box = self.chart_pane.bounding_box()
        if not pane_box:
            raise ValueError("Chart pane bounding box could not be retrieved")

        target_x = pane_box["x"] + pane_box["width"] * x_fraction
        target_y = pane_box["y"] + pane_box["height"] * y_fraction

        self.page.mouse.move(target_x, target_y)
        self.page.wait_for_timeout(500)
        return self.get_legend_ohlc_text()

    def pan_chart_canvas(self, delta_x: int, delta_y: int = 0) -> None:
        """Drag / pan the chart canvas horizontally or vertically."""
        logger.info(f"Panning chart canvas by delta_x={delta_x}, delta_y={delta_y}...")
        expect(self.chart_pane).to_be_visible(timeout=TIMEOUT_DEFAULT)
        pane_box = self.chart_pane.bounding_box()
        if not pane_box:
            raise ValueError("Chart pane bounding box could not be retrieved")

        start_x = pane_box["x"] + pane_box["width"] * 0.5
        start_y = pane_box["y"] + pane_box["height"] * 0.5

        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(start_x + delta_x, start_y + delta_y, steps=5)
        self.page.mouse.up()
        self.page.wait_for_timeout(600)

    def click_reset_chart_view(self) -> bool:
        """Click the 'Reset chart view' button in the chart control bar wrapper."""
        logger.info("Resetting chart view...")
        return self.tv_iframe.locator("body").evaluate("""(body) => {
            const btn = body.querySelector("div.control-bar-wrapper .js-btn-reset, div[title*='Reset chart']");
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")

    def set_quick_trade_lot_size(self, lot_size: str) -> None:
        """Set the lot size in the Quick Trade overlay input on the chart."""
        logger.info(f"Setting Quick Trade lot size to: {lot_size}")
        expect(self.quick_trade_lot_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_trade_lot_input.fill(lot_size)
        self.page.wait_for_timeout(300)

    def get_quick_trade_lot_size(self) -> str:
        """Return the current value in the Quick Trade lot size input."""
        expect(self.quick_trade_lot_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.quick_trade_lot_input.input_value().strip()

    def execute_quick_trade_buy(self) -> bool:
        """Click the Quick Trade BUY button on the chart."""
        logger.info("Executing Quick Trade BUY...")
        expect(self.quick_trade_buy_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_trade_buy_btn.click()
        self.page.wait_for_timeout(1000)
        return True

    def execute_quick_trade_sell(self) -> bool:
        """Click the Quick Trade SELL button on the chart."""
        logger.info("Executing Quick Trade SELL...")
        expect(self.quick_trade_sell_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_trade_sell_btn.click()
        self.page.wait_for_timeout(1000)
        return True

    def get_latest_toast_message(self, timeout: int = 5000) -> Optional[str]:
        """Capture toast notification or alert message from the main application."""
        start = time.time()
        while time.time() - start < timeout / 1000:
            toasts = self.page.evaluate("""() => {
                const nodes = Array.from(document.querySelectorAll(".toast, .notification, .alert, .message, .vue-notification-group"));
                return nodes.map(n => n.innerText.trim()).filter(t => t.length > 0);
            }""")
            if toasts:
                return toasts[-1]
            self.page.wait_for_timeout(200)
        return None




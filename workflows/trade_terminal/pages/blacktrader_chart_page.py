"""
Trade Terminal Black Trader Chart Page Object.
Dedicated Page Object model for the Black Trader Chart engine:
- Hosted iframe (#bt_chart_container iframe#xten)
- Top navbar controls: Symbol badge, Timeframe menu, Chart Type menu, Indicators, Grid layout popup, Fullscreen, Snapshot, Trade lines toggle, More menu, Undo/Redo
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import FrameLocator, Locator, Page, expect

from config.settings import settings
from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT, TIMEOUT_SHORT
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("blacktrader_chart_page")


class BlackTraderChartPage(BasePage):
    """Page Object dedicated exclusively to the Black Trader Chart engine."""

    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Main Workspace Containers
        self.chart_page_container: Locator = page.locator(
            "body > div.body > div.main > div.rightbar > section > div:nth-child(3)"
        )
        self.chart_top_pane: Locator = page.locator(
            "#app > div > div > div.div1.initialHeight, .div1.initialHeight, .div1"
        )
        self.bt_container: Locator = page.locator("#bt_chart_container")
        self.bt_iframe_locator: Locator = page.locator("#bt_chart_container iframe#xten, #bt_chart_container iframe")
        self.bt_iframe: FrameLocator = page.frame_locator("#bt_chart_container iframe#xten, #bt_chart_container iframe")
        self.chart_nav_icon: Locator = page.locator(".lefticons[data-tooltip='Chart']")

        # 2. Profile Menu Chart Switcher
        self.profile_icon: Locator = page.locator(
            "body > div.body > div.leftbar > div.leftlist.pcview > div.lefticons.toplefticon.toggleLeftMenu, "
            ".lefticons.toplefticon.toggleLeftMenu, .toggleLeftMenu"
        ).first
        self.profile_menu: Locator = page.locator("#targetmenu.newmenu, #targetmenu")
        self.profile_bt_btn: Locator = self.profile_menu.locator(".chart-btn.blacktrader")

        # 3. Black Trader Navbar Controls inside IFrame
        self.navbar: Locator = self.bt_iframe.locator("#navbar, nav.navbar").first
        self.save_btn: Locator = self.navbar.locator("button:has-text('SAVE')")
        self.symbol_btn: Locator = self.navbar.locator("button:has-text('XTEN:')").first
        self.timeframe_btn: Locator = self.navbar.locator("button[data-popup='DropMenu']")
        self.chart_type_btn: Locator = self.navbar.locator("button[data-popup='ChartType']")
        self.indicators_btn: Locator = self.navbar.locator("button:has-text('Indicators')")
        self.grid_menu_btn: Locator = self.navbar.locator("button[data-popup='GridPopMenu']")
        self.fullscreen_btn: Locator = self.navbar.locator("button[aria-label='Toggle fullscreen']")
        self.screenshot_btn: Locator = self.navbar.locator("button[data-popup='Screenshot']")
        self.more_menu_btn: Locator = self.navbar.locator("button[data-popup='Menu']")
        self.undo_btn: Locator = self.navbar.locator("button[aria-label='Undo']")
        self.redo_btn: Locator = self.navbar.locator("button[aria-label='Redo']")
        self.hide_trades_btn: Locator = self.navbar.locator("button[aria-label='Hide All Trades'], button[aria-label*='Trades']")

        # 4. Modals and Dialogs
        self.indicators_dialog: Locator = self.bt_iframe.locator(".popup-content, [role='dialog']").first
        self.indicators_search_input: Locator = self.bt_iframe.locator("input[placeholder*='Search'], .popup-content input[type='text']").first

        # 5. Black Trader Sidebar (#leftbar) Drawing Tools
        self.leftbar: Locator = self.bt_iframe.locator("#leftbar, .leftbar").first
        self.drawing_tools_btn: Locator = self.leftbar.locator("button[aria-label='Drawing Tools']")
        self.line_tools_btn: Locator = self.leftbar.locator("button[aria-label='Line Tools']")
        self.patterns_btn: Locator = self.leftbar.locator("button[aria-label='Patterns']")
        self.text_tools_btn: Locator = self.leftbar.locator("button[aria-label='Text Tools']")
        self.measure_tools_btn: Locator = self.leftbar.locator("button[aria-label='Measure Tools']")
        self.fibonacci_tools_btn: Locator = self.leftbar.locator("button[aria-label='Fibonacci Tools']")
        self.lock_all_drawings_btn: Locator = self.leftbar.locator(
            "button[aria-label='Lock All Drawings'], button[aria-label='Unlock All Drawings']"
        )
        self.hide_all_drawings_btn: Locator = self.leftbar.locator(
            "button[aria-label='Hide All Drawings'], button[aria-label='Show All Drawings']"
        )
        self.magnet_mode_btn: Locator = self.leftbar.locator("button[aria-label*='Magnet Mode']")
        self.keep_drawing_btn: Locator = self.leftbar.locator("button[aria-label*='Keep Drawing']")
        self.delete_tools_btn: Locator = self.leftbar.locator("button[aria-label='Delete Tools']")
        self.favorites_btn: Locator = self.leftbar.locator("button[aria-label*='Favorite Drawing Tools Toolbar']")

        # 6. Mainbar Canvas, Hover Controls & Quick Trading Widgets
        self.mainbar: Locator = self.bt_iframe.locator("#mainbar").first
        self.gridbar: Locator = self.bt_iframe.locator("#gridbar").first
        self.chart_grid: Locator = self.bt_iframe.locator("#agrid").first
        self.lwc_container: Locator = self.bt_iframe.locator(".tv-lightweight-charts").first
        self.chart_canvases: Locator = self.lwc_container.locator("canvas")
        self.primary_canvas: Locator = self.lwc_container.locator("canvas[style*='z-index: 2'], canvas").first

        # Hover Controls
        self.hover_controls: Locator = self.bt_iframe.locator("div[id*='hover-controls'][id*='-controls']").first
        self.hover_zoom_out_btn: Locator = self.bt_iframe.locator("button[id*='-btn-zoomOut'], button[title='Zoom Out']").first
        self.hover_zoom_in_btn: Locator = self.bt_iframe.locator("button[id*='-btn-zoomIn'], button[title='Zoom In']").first
        self.hover_scroll_left_btn: Locator = self.bt_iframe.locator("button[id*='-btn-scrollLeft'], button[title='Scroll Left']").first
        self.hover_scroll_right_btn: Locator = self.bt_iframe.locator("button[id*='-btn-scrollRight'], button[title='Scroll Right']").first
        self.hover_reset_view_btn: Locator = self.bt_iframe.locator("button[id*='-btn-refresh'], button[title='Reset View']").first

        # Fit / Scale Controls
        self.fit_price_scale_btn: Locator = self.bt_iframe.locator("button[title='Fit Price Scale']").first
        self.fit_time_scale_btn: Locator = self.bt_iframe.locator("button[title='Fit Time Scale']").first
        self.reset_initial_pos_btn: Locator = self.bt_iframe.locator("button[title='Reset to Initial Position']").first

        # Quick Trading Toolbar & Actions
        self.trade_toolbar: Locator = self.bt_iframe.locator("div.xtreme-trade-toolbar").first
        self.quick_buy_btn: Locator = self.bt_iframe.locator("button.buy-btn").first
        self.quick_sell_btn: Locator = self.bt_iframe.locator("button.sell-btn").first
        self.quick_qty_display: Locator = self.bt_iframe.locator("button.quantity-display").first
        self.quick_qty_input: Locator = self.bt_iframe.locator("input.quantity-input").first
        self.hide_trades_btn: Locator = self.bt_iframe.locator("button.toolbar-hover-button[title='Hide Trades']").first
        self.hide_indicators_btn: Locator = self.bt_iframe.locator("button.indicator-toggle[title='Hide Indicators']").first

        # 7. Rightbar, Layers Panel & Multi-Chart Controls
        self.rightbar: Locator = self.bt_iframe.locator("#rightbar, .rightbar").first
        self.rightbar_gutter: Locator = self.rightbar.locator("button[aria-label='Resize right panel'], .right-gutter").first
        self.layers_btn: Locator = self.rightbar.locator("button[aria-label='Layers']").first
        self.layers_panel: Locator = self.bt_iframe.locator("#rightbar div:has(> div > span:has-text('Drawings'))").first
        self.chart_controls_btn: Locator = self.rightbar.locator("button[aria-label='Chart Controls']").first
        self.chart_controls_menu: Locator = self.bt_iframe.locator("[role='menu']:has(button[aria-label*='All Charts'])").first
        self.zoom_in_all_charts_btn: Locator = self.bt_iframe.locator("button[aria-label='Zoom In All Charts']").first
        self.zoom_out_all_charts_btn: Locator = self.bt_iframe.locator("button[aria-label='Zoom Out All Charts']").first
        self.reset_view_all_charts_btn: Locator = self.bt_iframe.locator("button[aria-label='Reset View All Charts']").first
        self.scroll_left_all_charts_btn: Locator = self.bt_iframe.locator("button[aria-label='Scroll Left All Charts']").first
        self.scroll_right_all_charts_btn: Locator = self.bt_iframe.locator("button[aria-label='Scroll Right All Charts']").first
        self.toggle_logs_btn: Locator = self.rightbar.locator("button[aria-label='Toggle Logs Panel']").first
        self.show_logs_checkbox: Locator = self.bt_iframe.locator("label:has-text('Show logs') input[type='checkbox'], input[type='checkbox']:near(:text('Show logs'))").first

        # 8. Bottombar Tabs, Script Editor, Screener, Algo, Backtest & Trade Panel
        self.bottombar: Locator = self.bt_iframe.locator("#bottombar, .bottombar").first
        self.bottombar_gutter: Locator = self.bottombar.locator("button[aria-label='Resize bottom panel'], .sideseperator.gutter").first
        self.bottombar_collapse_btn: Locator = self.bottombar.locator(
            "button[aria-label='Toggle up/down'], button[aria-label='Toggle minimize']"
        ).first
        self.bottombar_maximize_btn: Locator = self.bottombar.locator(
            "button[aria-label='Toggle maximize'], button[aria-label='Toggle restore']"
        ).first

        # Bottombar Main Tabs
        self.tab_coder: Locator = self.bottombar.locator(".tab-headers button:has-text('Coder')").first
        self.tab_screener: Locator = self.bottombar.locator(".tab-headers button:has-text('Screener')").first
        self.tab_algo: Locator = self.bottombar.locator(".tab-headers button:has-text('Algo')").first
        self.tab_backtest: Locator = self.bottombar.locator(".tab-headers button:has-text('Backtest')").first
        self.tab_trade: Locator = self.bottombar.locator(".tab-headers button:has-text('Trade')").first
        self.bottombar_content: Locator = self.bottombar.locator(".tab-content").first

        # Coder Tab Elements
        self.coder_preview_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Preview')").first
        self.coder_publish_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Publish')").first
        self.coder_backtest_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Backtest')").first
        self.coder_tutorials_btn: Locator = self.bottombar.locator(".tab-content button[title*='Tutorial'], .tab-content button:has-text('?')").first
        self.coder_editor_textarea: Locator = self.bottombar.locator(".tab-content textarea.inputarea").first
        self.coder_show_logs_checkbox: Locator = self.bottombar.locator("label:has-text('Show logs') input[type='checkbox']").first

        # Screener Tab Elements
        self.screener_new_btn: Locator = self.bottombar.locator(
            ".tab-content button:has-text('New'), .tab-content button:has-text('Create Your First Screener')"
        ).first
        self.screener_close_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Close')").first
        self.screener_reset_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Reset All')").first
        self.screener_name_input: Locator = self.bottombar.locator(".tab-content input[placeholder*='screener name']").first
        self.screener_preview_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Preview')").first
        self.screener_save_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Save')").first

        # Algo Tab Elements
        self.algo_new_btn: Locator = self.bottombar.locator(
            ".tab-content button:has-text('New Algo'), .tab-content button:has-text('Create Your First Algo')"
        ).first
        self.algo_name_input: Locator = self.bottombar.locator(".tab-content input[placeholder*='algo name']").first
        self.algo_choose_strategy_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Choose an algo')").first
        self.algo_save_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Save Algo')").first

        # Backtest Tab Elements
        self.backtest_run_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Backtest')").first
        self.backtest_create_algo_btn: Locator = self.bottombar.locator(".tab-content button:has-text('Create Your First Algorithm')").first

        # Trade Tab Elements
        self.trade_account_btn: Locator = self.bottombar.locator(".tab-content button:has-text('xten')").first
        self.trade_broker_settings_btn: Locator = self.bottombar.locator(".tab-content button[title='Broker Settings']").first
        self.trade_subtab_positions: Locator = self.bottombar.locator(".tab-content button:has-text('Positions')").first
        self.trade_subtab_pending: Locator = self.bottombar.locator(".tab-content button:has-text('Pending')").first
        self.trade_subtab_orders: Locator = self.bottombar.locator(".tab-content button:has-text('Orders')").first
        self.trade_subtab_history: Locator = self.bottombar.locator(".tab-content button:has-text('History')").first
        self.trade_positions_table: Locator = self.bottombar.locator(".tab-content table").first
        self.trade_position_rows: Locator = self.bottombar.locator(".tab-content table tbody tr, .tab-content table tr:not(:first-child)")

    # =========================================================================
    # Navigation & Lifecycle
    # =========================================================================

    def navigate_to_chart(self, url: Optional[str] = None) -> None:
        """Navigate to dashboard and activate Black Trader Chart workspace."""
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard for Black Trader Chart: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self.dismiss_disclaimer_if_present()

        if not self.is_chart_nav_active():
            logger.info("Activating Chart workspace via left sidebar...")
            expect(self.chart_nav_icon).to_be_visible(timeout=TIMEOUT_DEFAULT)
            self.chart_nav_icon.click()
            self.page.wait_for_timeout(1000)

        self.ensure_blacktrader_active()
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

    def ensure_blacktrader_active(self, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Ensure Black Trader engine is the active chart engine."""
        if not self.bt_container.is_visible():
            logger.info("Black Trader is not active. Switching to Black Trader via profile menu...")
            self.profile_icon.click()
            self.page.wait_for_timeout(500)
            expect(self.profile_bt_btn).to_be_visible(timeout=timeout)
            self.profile_bt_btn.click()
            self.page.wait_for_timeout(1000)
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)

        # Close profile menu if it remained open
        try:
            self.page.evaluate("""() => {
                const targetmenu = document.querySelector("#targetmenu");
                if (targetmenu && targetmenu.classList.contains("newmenu") && window.getComputedStyle(targetmenu).display !== "none") {
                    const toggle = document.querySelector(".toggleLeftMenu");
                    if (toggle) toggle.click();
                }
            }""")
            self.page.wait_for_timeout(300)
        except Exception:
            pass

        expect(self.bt_container).to_be_visible(timeout=timeout)
        expect(self.bt_iframe_locator).to_be_visible(timeout=timeout)

    # =========================================================================
    # Toolbar Actions & Dropdown Navigation
    # =========================================================================

    def get_active_symbol_text(self) -> str:
        """Return the active symbol text displayed on the Black Trader toolbar."""
        expect(self.symbol_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.symbol_btn.inner_text().strip()

    def get_active_timeframe(self) -> str:
        """Return the active timeframe displayed on the navbar button."""
        expect(self.timeframe_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.timeframe_btn.inner_text().strip()

    def open_timeframe_menu(self) -> bool:
        """Click timeframe dropdown button."""
        logger.info("Opening Black Trader Timeframe dropdown...")
        expect(self.timeframe_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.timeframe_btn.click()
        self.page.wait_for_timeout(500)
        return True

    def select_timeframe(self, tf_label: str) -> bool:
        """Select a timeframe option from the open dropdown."""
        logger.info(f"Selecting Black Trader timeframe: {tf_label}")
        return self.bt_iframe.locator("body").evaluate("""(body, targetTf) => {
            const items = Array.from(body.querySelectorAll("button, li, a, div[class*='cursor-pointer']"));
            const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase() === targetTf.toLowerCase());
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""", tf_label)

    def open_chart_type_menu(self) -> bool:
        """Click chart type dropdown button."""
        logger.info("Opening Black Trader Chart Type dropdown...")
        expect(self.chart_type_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.chart_type_btn.click()
        self.page.wait_for_timeout(500)
        return True

    def select_chart_type(self, chart_type_label: str) -> bool:
        """Select a chart type option (e.g. 'Candles', 'Line', 'Bar') from the dropdown."""
        logger.info(f"Selecting Black Trader chart type: {chart_type_label}")
        return self.bt_iframe.locator("body").evaluate("""(body, targetType) => {
            const items = Array.from(body.querySelectorAll("button, li, a, div[class*='cursor-pointer']"));
            const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase().includes(targetType.toLowerCase()));
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""", chart_type_label)

    def open_indicators_dialog(self) -> bool:
        """Click indicators button in toolbar."""
        logger.info("Opening Black Trader Indicators dialog...")
        expect(self.indicators_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.indicators_btn.click()
        self.page.wait_for_timeout(800)
        return True

    def search_indicator(self, query: str) -> None:
        """Fill search query in the indicators modal."""
        logger.info(f"Searching for indicator: {query}")
        self.bt_iframe.locator("body").evaluate("""(body, q) => {
            const input = body.querySelector("input[placeholder*='Search'], .popup-content input[type='text'], input[type='text']");
            if (input) {
                input.value = q;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""", query)
        self.page.wait_for_timeout(500)

    def close_indicators_dialog(self) -> bool:
        """Close the open indicators dialog."""
        logger.info("Closing Black Trader Indicators dialog...")
        closed = self.bt_iframe.locator("body").evaluate("""(body) => {
            const btn = body.querySelector("button[aria-label='Close indicators']") || body.querySelector("button[aria-label*='Close']");
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")
        self.page.wait_for_timeout(500)
        return closed

    def open_grid_menu(self) -> bool:
        """Click multi-chart grid menu button."""
        logger.info("Opening Black Trader Grid menu...")
        expect(self.grid_menu_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.grid_menu_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_fullscreen(self) -> bool:
        """Click fullscreen toggle button."""
        logger.info("Toggling Black Trader fullscreen...")
        expect(self.fullscreen_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.fullscreen_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def open_screenshot_menu(self) -> bool:
        """Click screenshot / snapshot button."""
        logger.info("Opening Black Trader Screenshot dropdown...")
        expect(self.screenshot_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.screenshot_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def open_more_menu(self) -> bool:
        """Click More settings menu button."""
        logger.info("Opening Black Trader More menu...")
        expect(self.more_menu_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.more_menu_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_trade_lines(self) -> bool:
        """Click Hide/Show all trades toggle button."""
        logger.info("Toggling Black Trader trade lines...")
        expect(self.hide_trades_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.hide_trades_btn.click()
        self.page.wait_for_timeout(400)
        return True

    # =========================================================================
    # Sidebar (#leftbar) Drawing Tools & Flyout Drawers
    # =========================================================================

    def get_drawing_sidebar_tools(self) -> List[str]:
        """Return list of aria-labels of all visible buttons in #leftbar."""
        return self.bt_iframe.locator("body").evaluate("""(body) => {
            const leftbar = body.querySelector("#leftbar, .leftbar");
            if (!leftbar) return [];
            return Array.from(leftbar.querySelectorAll("button"))
                .map(b => b.getAttribute("aria-label"))
                .filter(label => label && label.length > 0);
        }""")

    def open_drawing_tool_flyout(self, group_name: str) -> bool:
        """Open the subtool flyout drawer for a tool group by clicking its arrow."""
        logger.info(f"Opening Black Trader drawing tool flyout: {group_name}")
        btn = self.leftbar.locator(f"button[aria-label='{group_name}']")
        expect(btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        arrow = btn.locator("svg").last
        if arrow.is_visible():
            arrow.click()
            self.page.wait_for_timeout(600)
            return True
        return False

    def get_flyout_subtools(self) -> List[str]:
        """Return list of subtool names from the currently open flyout drawer."""
        return self.bt_iframe.locator("body").evaluate("""(body) => {
            const drawer = body.querySelector("div.z-\\\\[100\\\\], div[class*='z-[100]']");
            if (!drawer) return [];
            return Array.from(drawer.querySelectorAll("button, div[class*='cursor-pointer']"))
                .map(b => b.innerText.trim())
                .filter(t => t.length > 0);
        }""")

    def is_drawer_open(self) -> bool:
        """Check if any subtool drawer is open."""
        return self.bt_iframe.locator("body").evaluate("""(body) => {
            const drawer = body.querySelector("div.z-\\\\[100\\\\], div[class*='z-[100]']");
            return !!drawer;
        }""")

    def select_drawing_subtool(self, group_name: str, subtool_name: str) -> bool:
        """Open the drawer for group_name if not already open and select subtool."""
        logger.info(f"Selecting subtool '{subtool_name}' from group '{group_name}'")
        if not self.is_drawer_open():
            self.open_drawing_tool_flyout(group_name)
        return self.bt_iframe.locator("body").evaluate("""(body, targetName) => {
            const drawer = body.querySelector("div.z-\\\\[100\\\\], div[class*='z-[100]']");
            if (!drawer) return false;
            const items = Array.from(drawer.querySelectorAll("button, div[class*='cursor-pointer']"));
            const target = items.find(i => i.innerText && i.innerText.trim().toLowerCase().includes(targetName.toLowerCase()));
            if (target) {
                target.click();
                return true;
            }
            return false;
        }""", subtool_name)

    def trigger_measure_mode(self) -> bool:
        """Click the Measure Tools button in the sidebar."""
        logger.info("Activating Measure mode from Black Trader sidebar...")
        expect(self.measure_tools_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.measure_tools_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_lock_all_drawings(self) -> bool:
        """Click the Lock All Drawings toggle button."""
        logger.info("Toggling Lock All Drawings in Black Trader sidebar...")
        expect(self.lock_all_drawings_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.lock_all_drawings_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_hide_all_drawings(self) -> bool:
        """Click the Hide All Drawings toggle button."""
        logger.info("Toggling Hide All Drawings in Black Trader sidebar...")
        expect(self.hide_all_drawings_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.hide_all_drawings_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_magnet_mode(self) -> bool:
        """Click the Magnet Mode toggle button."""
        logger.info("Toggling Magnet Mode in Black Trader sidebar...")
        expect(self.magnet_mode_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.magnet_mode_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_keep_drawing_mode(self) -> bool:
        """Click the Keep Drawing mode toggle button."""
        logger.info("Toggling Keep Drawing in Black Trader sidebar...")
        expect(self.keep_drawing_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.keep_drawing_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def click_delete_tools(self) -> bool:
        """Click the Delete Tools button."""
        logger.info("Clicking Delete Tools in Black Trader sidebar...")
        expect(self.delete_tools_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.delete_tools_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def toggle_favorites_toolbar(self) -> bool:
        """Click the Favorite Drawing Tools Toolbar toggle button."""
        logger.info("Toggling Favorite Drawing Tools Toolbar in Black Trader sidebar...")
        expect(self.favorites_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.favorites_btn.click()
        self.page.wait_for_timeout(400)
        return True

    # =========================================================================
    # Section 6: Mainbar Canvas, Hover Controls & Quick Trading Actions
    # =========================================================================

    def get_chart_series_data(self) -> dict:
        """
        Extract current OHLC legend, active symbol, timeframe, and quick trade quotes.
        """
        logger.info("Extracting Black Trader chart series data and OHLC values...")
        expect(self.lwc_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.bt_iframe.locator("body").evaluate("""body => {
            const grid = body.querySelector("#agrid");
            const text = grid ? grid.innerText : "";
            
            // Match symbol
            const symbolBtn = grid ? grid.querySelector("button.svelte-60yka9, button:not([class*='btn']):not([class*='scale'])") : null;
            const symbol = symbolBtn ? symbolBtn.innerText.trim() : (text.match(/XTEN:[^\\s\\n]+/)?.[0] || "");
            
            // Match timeframe
            const tfMatch = text.match(/(1m|5m|15m|30m|1h|4h|1D|1W|1M)/);
            const timeframe = tfMatch ? tfMatch[0] : "";
            
            // Match OHLC
            const oMatch = text.match(/O:\\s*([0-9.]+)/);
            const hMatch = text.match(/H:\\s*([0-9.]+)/);
            const lMatch = text.match(/L:\\s*([0-9.]+)/);
            const cMatch = text.match(/C:\\s*([0-9.]+)/);

            // Match Buy and Sell prices
            const sellBtn = body.querySelector("button.sell-btn");
            const buyBtn = body.querySelector("button.buy-btn");
            const sellPrice = sellBtn ? sellBtn.innerText.trim() : "";
            const buyPrice = buyBtn ? buyBtn.innerText.trim() : "";

            // Match quantity
            const qtyBtn = body.querySelector("button.quantity-display");
            const qty = qtyBtn ? qtyBtn.innerText.replace(/[SB\\n]/g, '').trim() : "";

            return {
                symbol: symbol,
                timeframe: timeframe,
                open: oMatch ? parseFloat(oMatch[1]) : null,
                high: hMatch ? parseFloat(hMatch[1]) : null,
                low: lMatch ? parseFloat(lMatch[1]) : null,
                close: cMatch ? parseFloat(cMatch[1]) : null,
                sellPrice: sellPrice ? parseFloat(sellPrice) : null,
                buyPrice: buyPrice ? parseFloat(buyPrice) : null,
                quantity: qty ? parseFloat(qty) : null,
                rawText: text.substring(0, 300)
            };
        }""")

    def reveal_hover_controls(self) -> bool:
        """
        Move mouse to bottom-center of the Lightweight Charts container to reveal hover controls.
        """
        logger.info("Revealing Black Trader chart hover controls...")
        expect(self.lwc_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.bt_iframe.locator("body").evaluate("""body => {
            const wrapper = body.querySelector('.tv-lightweight-charts');
            if (!wrapper) return;
            const rect = wrapper.getBoundingClientRect();
            const clientX = rect.left + rect.width * 0.5;
            const clientY = rect.top + rect.height - 50;
            wrapper.dispatchEvent(new MouseEvent('mousemove', {
                bubbles: true,
                clientX: clientX,
                clientY: clientY
            }));
        }""")
        self.page.wait_for_timeout(300)
        return self.hover_controls.is_visible()

    def click_hover_control(self, action: str) -> bool:
        """
        Click a button in the hover controls bar.
        Action can be: 'zoom_in', 'zoom_out', 'scroll_left', 'scroll_right', 'reset_view'.
        """
        logger.info(f"Clicking hover control: {action}...")
        self.reveal_hover_controls()
        action_map = {
            "zoom_in": self.hover_zoom_in_btn,
            "zoom_out": self.hover_zoom_out_btn,
            "scroll_left": self.hover_scroll_left_btn,
            "scroll_right": self.hover_scroll_right_btn,
            "reset_view": self.hover_reset_view_btn,
        }
        btn = action_map.get(action.lower().replace("-", "_").replace(" ", "_"))
        if not btn:
            raise ValueError(f"Unknown hover control action: {action}")
        btn.click(force=True)
        self.page.wait_for_timeout(300)
        return True

    def scroll_chart_canvas(self, delta_y: int = -100) -> bool:
        """
        Scroll (zoom) chart canvas using mouse wheel events.
        Negative delta_y zooms in, positive delta_y zooms out.
        """
        logger.info(f"Scrolling Black Trader chart canvas (delta_y={delta_y})...")
        expect(self.lwc_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        box = self.lwc_container.bounding_box()
        if not box:
            return False
        cx = box["x"] + box["width"] / 2
        cy = box["y"] + box["height"] / 2
        self.page.mouse.move(cx, cy)
        self.page.mouse.wheel(0, delta_y)
        self.page.wait_for_timeout(400)
        return True

    def pan_chart_canvas(self, delta_x: int = -150) -> bool:
        """
        Pan chart canvas horizontally by clicking and dragging.
        """
        logger.info(f"Panning Black Trader chart canvas (delta_x={delta_x})...")
        expect(self.lwc_container).to_be_visible(timeout=TIMEOUT_DEFAULT)
        box = self.lwc_container.bounding_box()
        if not box:
            return False
        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2
        end_x = start_x + delta_x
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(end_x, start_y, steps=10)
        self.page.mouse.up()
        self.page.wait_for_timeout(400)
        return True

    def set_quick_trade_lot_size(self, lot_size: str) -> bool:
        """
        Click quantity display, input custom lot size, and confirm.
        """
        logger.info(f"Setting quick trade lot size to {lot_size}...")
        expect(self.quick_qty_display).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_qty_display.click()
        self.page.wait_for_timeout(300)
        if self.quick_qty_input.is_visible():
            self.quick_qty_input.fill(lot_size)
            self.quick_qty_input.press("Enter")
            self.page.wait_for_timeout(300)
        return True

    def execute_quick_buy(self) -> bool:
        """
        Execute a Quick Buy order from the chart toolbar.
        """
        logger.info("Executing Quick Buy order from Black Trader chart...")
        expect(self.quick_buy_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_buy_btn.click()
        self.page.wait_for_timeout(500)
        return True

    def execute_quick_sell(self) -> bool:
        """
        Execute a Quick Sell order from the chart toolbar.
        """
        logger.info("Executing Quick Sell order from Black Trader chart...")
        expect(self.quick_sell_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.quick_sell_btn.click()
        self.page.wait_for_timeout(500)
        return True

    def fit_scales(self, scale_type: str = "all") -> bool:
        """
        Click scale fit buttons: 'price', 'time', 'initial', or 'all'.
        """
        logger.info(f"Fitting chart scales: {scale_type}...")
        if scale_type in ("price", "all") and self.fit_price_scale_btn.is_visible():
            self.fit_price_scale_btn.click()
            self.page.wait_for_timeout(200)
        if scale_type in ("time", "all") and self.fit_time_scale_btn.is_visible():
            self.fit_time_scale_btn.click()
            self.page.wait_for_timeout(200)
        if scale_type in ("initial", "all") and self.reset_initial_pos_btn.is_visible():
            self.reset_initial_pos_btn.click()
            self.page.wait_for_timeout(200)
        return True

    # =========================================================================
    # Section 7: Rightbar, Layers Panel & Multi-Chart Controls
    # =========================================================================

    def toggle_layers_panel(self) -> bool:
        """
        Click the Layers button in the rightbar to toggle the Layers/Drawings panel.
        Returns True if open after toggle, False if closed.
        """
        logger.info("Toggling Layers panel in Black Trader rightbar...")
        expect(self.layers_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.layers_btn.click()
        self.page.wait_for_timeout(500)
        return self.layers_panel.is_visible()

    def is_layers_panel_open(self) -> bool:
        """Return True if Layers panel is visible."""
        return self.layers_panel.is_visible()

    def open_chart_controls_menu(self) -> bool:
        """
        Open the Chart Controls popup menu from the rightbar.
        """
        logger.info("Opening Chart Controls menu from Black Trader rightbar...")
        expect(self.chart_controls_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        if not self.chart_controls_menu.is_visible():
            self.chart_controls_btn.click()
            self.page.wait_for_timeout(400)
        expect(self.chart_controls_menu).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return True

    def close_chart_controls_menu(self) -> bool:
        """
        Close the Chart Controls popup menu.
        """
        logger.info("Closing Chart Controls menu...")
        if self.chart_controls_menu.is_visible():
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        return True

    def click_chart_control_menu_action(self, action: str) -> bool:
        """
        Click an action in the Chart Controls popup menu:
        'zoom_in', 'zoom_out', 'reset_view', 'scroll_left', 'scroll_right'.
        """
        logger.info(f"Clicking chart control menu action: {action}...")
        self.open_chart_controls_menu()
        action_map = {
            "zoom_in": self.zoom_in_all_charts_btn,
            "zoom_out": self.zoom_out_all_charts_btn,
            "reset_view": self.reset_view_all_charts_btn,
            "scroll_left": self.scroll_left_all_charts_btn,
            "scroll_right": self.scroll_right_all_charts_btn,
        }
        btn = action_map.get(action.lower().replace("-", "_").replace(" ", "_"))
        if not btn:
            raise ValueError(f"Unknown chart control action: {action}")
        expect(btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        btn.click()
        self.page.wait_for_timeout(300)
        return True

    def toggle_logs_panel(self) -> bool:
        """
        Click the Toggle Logs Panel button in the rightbar.
        """
        logger.info("Toggling Logs Panel via Black Trader rightbar...")
        expect(self.toggle_logs_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.toggle_logs_btn.click()
        self.page.wait_for_timeout(400)
        return True

    def is_logs_panel_checked(self) -> bool:
        """
        Check if the 'Show logs' checkbox is checked.
        """
        if self.show_logs_checkbox.is_visible():
            return self.show_logs_checkbox.is_checked()
        return False

    def resize_right_panel(self, delta_x: int = -50) -> bool:
        """
        Drag the rightbar resize gutter horizontally.
        """
        logger.info(f"Resizing Black Trader right panel (delta_x={delta_x})...")
        expect(self.rightbar_gutter).to_be_visible(timeout=TIMEOUT_DEFAULT)
        box = self.rightbar_gutter.bounding_box()
        if not box:
            return False
        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(start_x + delta_x, start_y, steps=5)
        self.page.mouse.up()
        self.page.wait_for_timeout(400)
        return True

    # =========================================================================
    # Section 8: Bottombar Tabs, Script Editor, Screener, Algo, Backtest & Trade
    # =========================================================================

    def select_bottombar_tab(self, tab_name: str) -> bool:
        """
        Click a tab in the bottombar: 'Coder', 'Screener', 'Algo', 'Backtest', 'Trade'.
        """
        logger.info(f"Selecting bottombar tab: {tab_name}...")
        expect(self.bottombar).to_be_visible(timeout=TIMEOUT_DEFAULT)
        tab_map = {
            "coder": self.tab_coder,
            "screener": self.tab_screener,
            "algo": self.tab_algo,
            "backtest": self.tab_backtest,
            "trade": self.tab_trade,
        }
        tab = tab_map.get(tab_name.lower().strip())
        if not tab:
            raise ValueError(f"Unknown bottombar tab: {tab_name}")
        expect(tab).to_be_visible(timeout=TIMEOUT_DEFAULT)
        tab.click()
        self.page.wait_for_timeout(400)
        return True

    def get_active_bottombar_tab(self) -> str:
        """Return the name of the currently active bottombar tab."""
        return self.bottombar.locator(".tab-headers button.tab-header.active").inner_text().strip()

    def toggle_bottombar_collapse(self) -> bool:
        """
        Click the collapse/minimize button in the bottombar header.
        """
        logger.info("Toggling bottombar collapse/expand...")
        expect(self.bottombar_collapse_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.bottombar_collapse_btn.click()
        self.page.wait_for_timeout(500)
        return self.is_bottombar_collapsed()

    def is_bottombar_collapsed(self) -> bool:
        """Return True if bottombar is collapsed (< 60px height)."""
        box = self.bottombar.bounding_box()
        return box["height"] < 60 if box else False

    def toggle_bottombar_maximize(self) -> bool:
        """
        Click the maximize/restore button in the bottombar header.
        """
        logger.info("Toggling bottombar maximize/restore...")
        expect(self.bottombar_maximize_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.bottombar_maximize_btn.click()
        self.page.wait_for_timeout(500)
        return self.is_bottombar_maximized()

    def is_bottombar_maximized(self) -> bool:
        """Return True if bottombar is maximized (> 700px height)."""
        box = self.bottombar.bounding_box()
        return box["height"] > 700 if box else False

    def coder_trigger_preview(self) -> bool:
        """
        Click Preview in the Coder tab to compile and run strategy preview.
        """
        logger.info("Triggering Coder Preview in Black Trader bottombar...")
        self.select_bottombar_tab("Coder")
        expect(self.coder_preview_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.coder_preview_btn.click()
        self.page.wait_for_timeout(1000)
        return True

    def close_coder_preview_console(self) -> bool:
        """
        Close the strategy preview console if open.
        """
        logger.info("Closing Coder Preview console...")
        console = self.bt_iframe.locator("div[class*='z-[55]']").first
        if console.is_visible():
            close_btn = console.locator("button:has(svg):last-child").first
            if close_btn.is_visible():
                close_btn.click()
                self.page.wait_for_timeout(400)
        return True

    def coder_toggle_show_logs(self) -> bool:
        """
        Toggle the 'Show logs' checkbox in the Coder tab.
        """
        logger.info("Toggling Show logs in Coder tab...")
        self.select_bottombar_tab("Coder")
        label = self.bottombar.locator("label:has-text('Show logs')").first
        expect(label).to_be_visible(timeout=TIMEOUT_DEFAULT)
        label.click()
        self.page.wait_for_timeout(400)
        return self.coder_show_logs_checkbox.is_checked()

    def screener_open_builder(self) -> bool:
        """
        Open the Screener builder in the Screener tab.
        """
        logger.info("Opening Screener builder in Black Trader bottombar...")
        self.select_bottombar_tab("Screener")
        expect(self.screener_new_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.screener_new_btn.click()
        self.page.wait_for_timeout(500)
        expect(self.screener_close_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return True

    def screener_close_builder(self) -> bool:
        """
        Close the Screener builder.
        """
        logger.info("Closing Screener builder...")
        if self.screener_close_btn.is_visible():
            self.screener_close_btn.click()
            self.page.wait_for_timeout(400)
        return True

    def create_screener(self, name: str) -> bool:
        """
        Create a new screener with the given name, trigger preview, and save it.
        Verifies that the screener is saved and active in the screener list.
        """
        logger.info(f"Creating new screener: '{name}' in Black Trader...")
        self.select_bottombar_tab("Screener")
        expect(self.screener_new_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.screener_new_btn.click()
        self.page.wait_for_timeout(500)

        expect(self.screener_name_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.screener_name_input.fill(name)
        self.page.wait_for_timeout(300)

        # Trigger Preview
        if self.screener_preview_btn.is_visible():
            self.screener_preview_btn.click()
            self.page.wait_for_timeout(600)

        # Save screener
        expect(self.screener_save_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.screener_save_btn.click()
        self.page.wait_for_timeout(1000)

        # Verify screener name appears in the screener view
        saved_screener_label = self.bottombar.locator(f"text='{name}'").first
        expect(saved_screener_label).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return True

    def algo_open_builder(self) -> bool:
        """
        Open the Algo builder in the Algo tab.
        """
        logger.info("Opening Algo builder in Black Trader bottombar...")
        self.select_bottombar_tab("Algo")
        expect(self.algo_new_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.algo_new_btn.click()
        self.page.wait_for_timeout(500)
        expect(self.algo_name_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return True

    def create_algo(
        self,
        name: str,
        strategy_name: str = "Cross Over - MA",
        screener_name: Optional[str] = None,
    ) -> bool:
        """
        Create a new algo strategy with the given name, select a system strategy,
        link a screener or symbol, and save it.
        Verifies that the newly created algo appears in the Algos list.
        """
        logger.info(f"Creating new algo: '{name}' (strategy: {strategy_name}) in Black Trader...")
        self.select_bottombar_tab("Algo")
        expect(self.algo_new_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.algo_new_btn.click()
        self.page.wait_for_timeout(500)

        expect(self.algo_name_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.algo_name_input.fill(name)
        self.page.wait_for_timeout(300)

        # Open Strategy selection modal
        expect(self.algo_choose_strategy_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self.algo_choose_strategy_btn.click()
        self.page.wait_for_timeout(600)

        modal = self.bt_iframe.locator("div.popup-content").first
        expect(modal).to_be_visible(timeout=TIMEOUT_DEFAULT)

        # Switch to System tab
        system_tab = modal.locator("button:has-text('System')").first
        expect(system_tab).to_be_visible(timeout=TIMEOUT_DEFAULT)
        system_tab.click()
        self.page.wait_for_timeout(500)

        # Select strategy
        strategy_opt = modal.locator(f"text='{strategy_name}'").first
        if not strategy_opt.is_visible():
            strategy_opt = modal.locator("div[class*='cursor-pointer'], button[class*='cursor-pointer']").first
        strategy_opt.click()
        self.page.wait_for_timeout(600)

        # Link Screener for symbols
        choose_scr_btn = self.bottombar.locator("button:has-text('Choose a screener')").first
        if choose_scr_btn.is_visible():
            choose_scr_btn.click()
            self.page.wait_for_timeout(500)
            if screener_name:
                scr_item = self.bt_iframe.locator(f"button:has-text('{screener_name}'), div:has-text('{screener_name}')").last
            else:
                scr_item = self.bt_iframe.locator("button:has-text('Screener'), div:has-text('Screener')").last
            if scr_item.is_visible():
                scr_item.click()
                self.page.wait_for_timeout(500)
        else:
            # Fallback to manual symbol selection
            choose_manual_btn = self.bottombar.locator("button:has-text('Choose Manually')").first
            if choose_manual_btn.is_visible():
                choose_manual_btn.click()
                self.page.wait_for_timeout(400)
                search_input = self.bottombar.locator("input[placeholder*='Search symbols']").first
                if search_input.is_visible():
                    search_input.fill("BTC")
                    self.page.wait_for_timeout(500)
                    first_sym = self.bt_iframe.locator("text='BTC'").first
                    if first_sym.is_visible():
                        first_sym.click()
                        self.page.wait_for_timeout(500)

        # Save Algo
        expect(self.algo_save_btn).to_be_enabled(timeout=TIMEOUT_DEFAULT)
        self.algo_save_btn.click()
        self.page.wait_for_timeout(1000)

        # Verify algo appears in the list
        algo_label = self.bottombar.locator(f"text='{name}'").first
        expect(algo_label).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return True

    def select_trade_subtab(self, subtab_name: str) -> bool:
        """
        Click a subtab in the Trade tab: 'Positions', 'Pending', 'Orders', 'History'.
        """
        logger.info(f"Selecting Trade subtab: {subtab_name}...")
        self.select_bottombar_tab("Trade")
        subtab_map = {
            "positions": self.trade_subtab_positions,
            "pending": self.trade_subtab_pending,
            "orders": self.trade_subtab_orders,
            "history": self.trade_subtab_history,
        }
        btn = subtab_map.get(subtab_name.lower().strip())
        if not btn:
            raise ValueError(f"Unknown Trade subtab: {subtab_name}")
        expect(btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        btn.click()
        self.page.wait_for_timeout(400)
        return True

    def get_trade_positions_rows_count(self) -> int:
        """Return number of position rows currently visible in Trade tab."""
        self.select_trade_subtab("Positions")
        return self.trade_position_rows.count()

    def resize_bottom_panel(self, delta_y: int = -40) -> bool:
        """
        Drag the bottombar resize gutter vertically.
        """
        logger.info(f"Resizing bottom panel (delta_y={delta_y})...")
        expect(self.bottombar_gutter).to_be_visible(timeout=TIMEOUT_DEFAULT)
        box = self.bottombar_gutter.bounding_box()
        if not box:
            return False
        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(start_x, start_y + delta_y, steps=5)
        self.page.mouse.up()
        self.page.wait_for_timeout(400)
        return True



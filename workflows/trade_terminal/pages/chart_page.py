"""
Trade Terminal Chart Page Object.
Encapsulates all chart engine elements: TradingView / BlackTrader chart panes,
chart iframes, symbol title, and left sidebar Chart navigation active state.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("chart_page")

TIMEOUT_DEFAULT = 15000


class TradingChartPage(BasePage):
    """Page object for Trade Terminal Chart workspace."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Chart pane containers
        self.tv_chart_container: Locator = page.locator("#tv_chart_container")
        self.bt_chart_container: Locator = page.locator("#bt_chart_container")
        self.chart_panes: Locator = page.locator(".chart-pane")

        # TradingView iframe and canvas
        self.chart_iframe: Locator = page.locator("#tv_chart_container iframe, iframe[id*='tradingview']")

        # Left navigation icon for Chart
        self.chart_nav_icon: Locator = page.locator(".lefticons[data-tooltip='Chart']")

    def is_chart_pane_visible(self) -> bool:
        """Return True if either TradingView or BlackTrader chart container is visible."""
        return self.tv_chart_container.is_visible() or self.bt_chart_container.is_visible()

    def is_chart_nav_active(self) -> bool:
        """Return True if left sidebar Chart icon has 'active' class."""
        classes = self.chart_nav_icon.get_attribute("class") or ""
        return "active" in classes.split()

    def wait_for_chart_rendered(self, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Wait for chart container and iframe to be attached and visible."""
        logger.info("Waiting for chart engine container to render...")
        expect(self.tv_chart_container).to_be_visible(timeout=timeout)

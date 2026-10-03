"""
Trade Terminal Pytest Fixtures.
Provides isolated pages, authenticated sessions, and page objects for Trade Terminal tests.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import settings
from workflows.shared.fixtures.auth_fixtures import ensure_authenticated_context
from workflows.shared.utils.diagnostics import PageDiagnostics
from workflows.shared.utils.error_monitor import ErrorMonitor
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.screenshot import capture_screenshot
from workflows.trade_terminal.pages.api_access_page import ApiAccessPage
from workflows.trade_terminal.pages.blacktrader_chart_page import BlackTraderChartPage
from workflows.trade_terminal.pages.chart_page import TradingChartPage
from workflows.trade_terminal.pages.history_page import HistoryPage
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.navigation_bar_page import NavigationBarPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.profile_menu_page import ProfileMenuPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage
from workflows.trade_terminal.pages.tradingview_chart_page import TradingViewChartPage
from workflows.trade_terminal.pages.watchlist_page import WatchlistPage

logger = get_logger("trade_fixtures")


def _perform_trade_login(page: Page, creds) -> None:
    """Helper used during fresh session generation."""
    login_page = TradeLoginPage(page)
    login_page.navigate(creds.login_url or creds.base_url)
    try:
        login_page.login_and_wait_for_dashboard(
            username=creds.username,
            password=creds.password,
            remember_me=True,
            timeout=25000,
        )
    except Exception:
        if creds.post_login_url_pattern:
            try:
                page.wait_for_url(creds.post_login_url_pattern, timeout=15000)
            except Exception:
                pass


@pytest.fixture(scope="function")
def trade_page(workflow_page: Page) -> Page:
    """
    Unauthenticated page ready for Trade Terminal interactions (e.g. login testing).
    """
    return workflow_page


@pytest.fixture(scope="function")
def authenticated_trade_context(workflow_browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Browser context pre-authenticated for Trade Terminal workflows.
    Reuses cached auth_state_trade.json when available.
    """
    context = ensure_authenticated_context(
        browser=workflow_browser,
        credentials=settings.trade_terminal,
        login_action_fn=_perform_trade_login,
        auth_state_file=settings.trade_terminal.auth_state_path,
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def authenticated_trade_page(
    authenticated_trade_context: BrowserContext,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    """
    Pre-authenticated page instance for Trade Terminal tests with diagnostics telemetry.
    """
    page = authenticated_trade_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    diagnostics = PageDiagnostics(page)
    page._diagnostics = diagnostics
    page.error_monitor = ErrorMonitor(page)

    yield page

    # Screenshot and diagnostics capture on test failure
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if test_failed:
        if settings.browser.screenshot_on_failure:
            capture_screenshot(
                page=page,
                test_name=request.node.name,
                suffix="failure",
                destination_dir=settings.screenshots_dir,
            )
        try:
            diag_path = diagnostics.save_report(
                test_name=request.node.name,
                destination_dir=settings.diagnostics_dir,
            )
            logger.info(f"Saved failure diagnostic telemetry to: {diag_path}")
            if diagnostics.has_errors():
                logger.error(
                    f"Diagnostic errors detected during failed test '{request.node.name}':\n"
                    f"{diagnostics.format_report()}"
                )
        except Exception as e:
            logger.error(f"Failed to save diagnostic telemetry: {e}")

    try:
        page.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def trade_error_monitor(authenticated_trade_page: Page) -> ErrorMonitor:
    """Provide the active ErrorMonitor for the current Trade Terminal page."""
    return authenticated_trade_page.error_monitor


@pytest.fixture(scope="function")
def trade_login_page(trade_page: Page) -> TradeLoginPage:
    """Provide an unauthenticated TradeLoginPage object."""
    return TradeLoginPage(trade_page)


@pytest.fixture(scope="function")
def trading_dashboard_page(authenticated_trade_page: Page) -> TradingDashboardPage:
    """Provide an authenticated TradingDashboardPage object."""
    dashboard = TradingDashboardPage(authenticated_trade_page)
    return dashboard


@pytest.fixture(scope="function")
def order_entry_page(authenticated_trade_page: Page) -> OrderEntryPage:
    """Provide an authenticated OrderEntryPage object."""
    return OrderEntryPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def positions_page(authenticated_trade_page: Page) -> PositionsPage:
    """Provide an authenticated PositionsPage object."""
    return PositionsPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def profile_menu_page(authenticated_trade_page: Page) -> ProfileMenuPage:
    """Provide an authenticated ProfileMenuPage object."""
    profile = ProfileMenuPage(authenticated_trade_page)
    return profile


@pytest.fixture(scope="function")
def watchlist_page(authenticated_trade_page: Page) -> WatchlistPage:
    """Provide an authenticated WatchlistPage object."""
    return WatchlistPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def trading_chart_page(authenticated_trade_page: Page) -> TradingChartPage:
    """Provide an authenticated TradingChartPage object."""
    return TradingChartPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def tradingview_chart_page(authenticated_trade_page: Page) -> TradingViewChartPage:
    """Provide an authenticated TradingViewChartPage object dedicated to TradingView."""
    return TradingViewChartPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def blacktrader_chart_page(authenticated_trade_page: Page) -> BlackTraderChartPage:
    """Provide an authenticated BlackTraderChartPage object dedicated to Black Trader."""
    return BlackTraderChartPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def history_page(authenticated_trade_page: Page) -> HistoryPage:
    """Provide an authenticated HistoryPage object."""
    return HistoryPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def api_access_page(authenticated_trade_page: Page) -> ApiAccessPage:
    """Provide an authenticated ApiAccessPage object."""
    return ApiAccessPage(authenticated_trade_page)


@pytest.fixture(scope="function")
def navigation_bar_page(authenticated_trade_page: Page) -> NavigationBarPage:
    """Provide an authenticated NavigationBarPage object for sidebar navigation."""
    return NavigationBarPage(authenticated_trade_page)

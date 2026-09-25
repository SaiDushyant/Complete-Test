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
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


def _perform_trade_login(page: Page, creds) -> None:
    """Helper used during fresh session generation."""
    login_page = TradeLoginPage(page)
    login_page.navigate(creds.login_url or creds.base_url)
    login_page.login(
        username=creds.username,
        password=creds.password,
        remember_me=True,
    )
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
def authenticated_trade_page(authenticated_trade_context: BrowserContext) -> Generator[Page, None, None]:
    """
    Pre-authenticated page instance for Trade Terminal tests.
    """
    page = authenticated_trade_context.new_page()
    page.set_default_timeout(settings.browser.timeout)
    yield page
    page.close()


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

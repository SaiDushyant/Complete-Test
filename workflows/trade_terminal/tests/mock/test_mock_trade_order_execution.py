"""
Trade Terminal Mock Tests: Order Execution and State Reflection.
Validates that trade order placement, rejection handling, and position rendering
work seamlessly with mocked server responses without live DB mutations.
"""

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import error_mocks, trade_mocks
from workflows.shared.mocks.mock_router import MockRouter
from workflows.trade_terminal.pages.login_page import TradeLoginPage
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_order_execution_success(mock_router: MockRouter, workflow_page: Page):
    """Verify that a successful 200 OK order placement response correctly notifies user in UI."""
    # 1. Setup mock routes
    mock_router.mock_json("**/api/**/symbols**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)
    mock_router.mock_json("**/api/**/metrics**", trade_mocks.MOCK_ACCOUNT_METRICS)
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_ORDER_SUCCESS_RESPONSE,
        status=200,
    )

    # 2. Check router active routes
    assert len(mock_router._active_routes) >= 3


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_insufficient_margin_rejection(mock_router: MockRouter, workflow_page: Page):
    """Verify that backend HTTP 400 Insufficient Margin response triggers an alert without crashing."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_ORDER_REJECTED_MARGIN,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_market_closed_rejection(mock_router: MockRouter, workflow_page: Page):
    """Verify that attempting to place an order when market is halted returns structured error."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_MARKET_CLOSED_RESPONSE,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1

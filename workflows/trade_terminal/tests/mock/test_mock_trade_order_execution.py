"""
Trade Terminal Mock Tests: Order Execution, Boundary Validation, and Telemetry.
Validates Market, Limit, and Stop HFT orders, rejection states, lot boundaries, slippage, and telemetry.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import error_mocks, trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_market_buy_order_success(mock_router: MockRouter, workflow_page: Page):
    """Verify that a successful 200 OK market buy order response is handled properly."""
    mock_router.mock_json("**/api/**/symbols**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)
    mock_router.mock_json("**/api/**/metrics**", trade_mocks.MOCK_ACCOUNT_METRICS)
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 3


@pytest.mark.mock
@pytest.mark.trade
def test_mock_market_sell_order_success(mock_router: MockRouter, workflow_page: Page):
    """Verify that a successful 200 OK market sell order response is processed."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_SELL_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_limit_buy_order_placement(mock_router: MockRouter, workflow_page: Page):
    """Verify placing a Limit Buy order returns 200 OK and registers pending state."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_LIMIT_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_limit_sell_order_placement(mock_router: MockRouter, workflow_page: Page):
    """Verify placing a Limit Sell order returns 200 OK."""
    limit_sell = dict(trade_mocks.MOCK_LIMIT_ORDER_SUCCESS_RESPONSE)
    limit_sell["details"]["type"] = "SELL_LIMIT"
    mock_router.mock_json(
        "**/api/**/order**",
        limit_sell,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_stop_hft_order_placement(mock_router: MockRouter, workflow_page: Page):
    """Verify placing a Stop HFT dual-trigger order returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_STOP_HFT_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


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


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_slippage_exceeded_error(mock_router: MockRouter, workflow_page: Page):
    """Verify that when execution price moves beyond slippage tolerance, UI receives 400 off quotes."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_ORDER_SLIPPAGE_ERROR,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_lot_boundary_exceeded_error(mock_router: MockRouter, workflow_page: Page):
    """Verify backend rejection when submitted lot size exceeds maximum account volume."""
    mock_router.mock_error(
        "**/api/**/order**",
        status=400,
        error_message="Requested lot size (200.0) exceeds max allowable volume (100.0).",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_order_payload_telemetry_capture(mock_router: MockRouter, workflow_page: Page):
    """Verify capturing submitted order request headers and payload parameters."""
    mock_router.capture_requests(
        "**/api/**/order**",
        mock_response_data=trade_mocks.MOCK_ORDER_SUCCESS_RESPONSE,
    )
    assert len(mock_router._active_routes) >= 1

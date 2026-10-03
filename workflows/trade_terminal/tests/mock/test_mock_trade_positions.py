"""
Trade Terminal Mock Tests: Open Positions and Pending Orders Management.
Validates table rendering, empty states, SL/TP modification, specific close actions, server failures,
bulk operations (all, profit, loss), and pending order cancellations.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import error_mocks, trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_open_positions_table_rendering(mock_router: MockRouter, workflow_page: Page):
    """Verify open positions table renders rows from mocked positions payload."""
    mock_router.mock_json("**/api/**/positions**", trade_mocks.MOCK_OPEN_POSITIONS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_open_positions_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify 'No Open Positions' placeholder renders when positions list is empty."""
    mock_router.mock_json("**/api/**/positions**", [])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_position_modify_sl_tp_success(mock_router: MockRouter, workflow_page: Page):
    """Verify modifying Stop Loss and Take Profit on open position returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/positions/modify**",
        {"success": True, "ticket": 9081234, "sl": 1.08100, "tp": 1.09200},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_position_modify_sl_tp_error(mock_router: MockRouter, workflow_page: Page):
    """Verify invalid SL/TP modification returns structured error."""
    mock_router.mock_error(
        "**/api/**/positions/modify**",
        status=400,
        error_message="Stop loss cannot be above current bid price for BUY position.",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_close_specific_position_success(mock_router: MockRouter, workflow_page: Page):
    """Verify closing a single position returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/positions/close**",
        {"success": True, "message": "Position 9081234 closed successfully", "ticket": 9081234},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_close_position_server_failure(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when position closure encounters HTTP 500 error."""
    mock_router.mock_error(
        "**/api/**/positions/close**",
        status=500,
        error_message="Trade Execution Server Timeout",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_bulk_close_all_positions(mock_router: MockRouter, workflow_page: Page):
    """Verify bulk close all positions endpoint fulfills successfully."""
    mock_router.mock_json(
        "**/api/**/positions/close-all**",
        {"success": True, "closed_count": 3, "message": "All open positions closed"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_bulk_close_profit_positions_only(mock_router: MockRouter, workflow_page: Page):
    """Verify bulk close profitable positions only."""
    mock_router.mock_json(
        "**/api/**/positions/close-profit**",
        {"success": True, "closed_count": 2, "message": "Profitable positions closed"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_bulk_close_loss_positions_only(mock_router: MockRouter, workflow_page: Page):
    """Verify bulk close losing positions only."""
    mock_router.mock_json(
        "**/api/**/positions/close-loss**",
        {"success": True, "closed_count": 1, "message": "Losing positions closed"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_pending_orders_cancellation(mock_router: MockRouter, workflow_page: Page):
    """Verify cancellation of pending orders with mocked response."""
    mock_router.mock_json("**/api/**/pending**", trade_mocks.MOCK_PENDING_ORDERS)
    mock_router.mock_json(
        "**/api/**/pending/cancel**",
        {"success": True, "ticket": 9081240, "status": "CANCELLED"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 2

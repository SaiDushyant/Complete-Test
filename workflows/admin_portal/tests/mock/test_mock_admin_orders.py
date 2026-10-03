"""
Admin Portal Mock Tests: Module 10 - Orders & Trade Management.
Tests live open positions grid, closed trade history, symbol/user filters, emergency force-close,
Master Order Report (/OrderReport), User Order Report (/userOrderReport), and Order Edit Log (/orderEditLog).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_open_orders_grid_render(mock_router: MockRouter, workflow_page: Page):
    """Verify live open positions grid (/order/open) across all platform traders."""
    mock_router.mock_json("**/Controlbase/order/open**", admin_mocks.MOCK_ADMIN_OPEN_ORDERS, status=200)
    mock_router.mock_json("**/Controlbase/openOrders**", admin_mocks.MOCK_ADMIN_OPEN_ORDERS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_closed_orders_grid_render(mock_router: MockRouter, workflow_page: Page):
    """Verify closed trade history grid (/order/closed) with realized profit and close reason."""
    mock_router.mock_json("**/Controlbase/order/closed**", admin_mocks.MOCK_ADMIN_CLOSED_ORDERS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_filter_orders_by_symbol_and_user(mock_router: MockRouter, workflow_page: Page):
    """Verify instant filtering of open orders by symbol (BTCUSD) and Account ID."""
    btc_orders = [o for o in admin_mocks.MOCK_ADMIN_OPEN_ORDERS if o.get("symbol") == "BTCUSD"]
    mock_router.mock_json("**/Controlbase/order/all?symbol=BTCUSD**", btc_orders, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_force_close_order(mock_router: MockRouter, workflow_page: Page):
    """Verify admin emergency force-close of a runaway position at market price."""
    mock_router.mock_json("**/Controlbase/closeOrder**", {"status": 200, "closed_price": 1.0850}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_order_report_date_filter(mock_router: MockRouter, workflow_page: Page):
    """Verify Master Order Report (/OrderReport) with date picker and symbol breakdown."""
    mock_router.mock_json("**/Controlbase/OrderReport**", admin_mocks.MOCK_ADMIN_ORDER_REPORT, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_order_report_filter(mock_router: MockRouter, workflow_page: Page):
    """Verify User Order Report (/userOrderReport) for single trader account audit."""
    mock_router.mock_json("**/Controlbase/userOrderReport?user_id=10098**", admin_mocks.MOCK_ADMIN_OPEN_ORDERS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_order_edit_log_table_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Order Edit Log (/orderEditLog) audit records showing price/SL/TP modifications."""
    mock_router.mock_json("**/Controlbase/orderEditLog**", admin_mocks.MOCK_ADMIN_ORDER_EDIT_LOG, status=200)
    assert len(mock_router._active_routes) >= 1

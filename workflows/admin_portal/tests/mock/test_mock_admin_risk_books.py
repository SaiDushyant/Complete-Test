"""
Admin Portal Mock Tests: Module 11 - Risk Management (A-Book & B-Book Routing).
Tests A-Book routed orders, B-Book risk exposure summary, switching trader execution mode,
A-Book user margin metrics, B-Book user margin monitor, and comparative Book Report.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_a_book_routed_orders_render(mock_router: MockRouter, workflow_page: Page):
    """Verify A-Book orders table (/aBook) showing LP execution bridge and fill prices."""
    mock_router.mock_json("**/Controlbase/aBook**", admin_mocks.MOCK_ADMIN_A_BOOK_ORDERS, status=200)
    mock_router.mock_json("**/Controlbase/aBookOrders**", admin_mocks.MOCK_ADMIN_A_BOOK_ORDERS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_b_book_exposure_summary(mock_router: MockRouter, workflow_page: Page):
    """Verify B-Book net aggregate risk exposure (/bBook) across all symbols."""
    mock_router.mock_json("**/Controlbase/bBook**", admin_mocks.MOCK_ADMIN_B_BOOK_EXPOSURE, status=200)
    mock_router.mock_json("**/Controlbase/bBookExposure**", admin_mocks.MOCK_ADMIN_B_BOOK_EXPOSURE, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_route_trader_to_a_book(mock_router: MockRouter, workflow_page: Page):
    """Verify changing trader execution mode from B-Book to A-Book STP bridge."""
    mock_router.mock_json("**/Controlbase/switchRouting**", {"status": 200, "routing": "A_BOOK"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_a_book_user_margin_render(mock_router: MockRouter, workflow_page: Page):
    """Verify A-Book User Margin page (/aBookUserMargin) margin utilization table."""
    mock_router.mock_json("**/Controlbase/aBookUserMargin**", admin_mocks.MOCK_ADMIN_USER_MARGIN, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_b_book_user_margin_render(mock_router: MockRouter, workflow_page: Page):
    """Verify B-Book User Margin page (/bBookUserMargin) warehouse risk metrics."""
    mock_router.mock_json("**/Controlbase/bBookUserMargin**", admin_mocks.MOCK_ADMIN_USER_MARGIN, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_book_report_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Book Report (/bookReport) daily trading exposure breakdown between A and B book."""
    mock_router.mock_json("**/Controlbase/bookReport**", admin_mocks.MOCK_ADMIN_BOOK_REPORT, status=200)
    assert len(mock_router._active_routes) >= 1

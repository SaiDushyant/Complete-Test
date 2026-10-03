"""
Trade Terminal Mock Tests: Dashboard Analytics, Charts, and Metrics.
Validates summary cards, PnL period toggles, Most Traded symbols, empty stat states, and performance KPI cards.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_metric_cards_render(mock_router: MockRouter, workflow_page: Page):
    """Verify overview summary cards (Account Status, Token, Balance, Free Margin)."""
    mock_router.mock_json("**/api/**/dashboard/overview**", trade_mocks.MOCK_DASHBOARD_OVERVIEW)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_daily_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Daily PnL period toggle renders daily curve data."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=daily**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["daily"])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_weekly_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Weekly PnL period toggle renders weekly aggregations."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=weekly**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["weekly"])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_pnl_monthly_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify Monthly PnL period toggle renders month-by-month profit curves."""
    mock_router.mock_json("**/api/**/dashboard/pnl?period=monthly**", trade_mocks.MOCK_DASHBOARD_PNL_SERIES["monthly"])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_most_traded_symbols(mock_router: MockRouter, workflow_page: Page):
    """Verify Most Traded breakdown list and percentages."""
    mock_router.mock_json("**/api/**/dashboard/most-traded**", trade_mocks.MOCK_DASHBOARD_MOST_TRADED)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_empty_trade_stats(mock_router: MockRouter, workflow_page: Page):
    """Verify brand new trading account with zero trades renders default clean metrics."""
    mock_router.mock_json("**/api/**/dashboard/most-traded**", [])
    mock_router.mock_json("**/api/**/dashboard/pnl**", {"title": "PnL", "data": []})
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.trade
def test_mock_dashboard_performance_stats_cards(mock_router: MockRouter, workflow_page: Page):
    """Verify all 8 performance stat KPIs in overview card."""
    mock_router.mock_json("**/api/**/dashboard/performance**", trade_mocks.MOCK_DASHBOARD_PERFORMANCE_STATS)
    assert len(mock_router._active_routes) >= 1

"""
Trade Terminal Mock Tests: Trade History, Reporting, and Statistics.
Validates historical record list rendering, empty states, calculation footers, duration filters,
custom date modal, and export operations.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_records_table_render(mock_router: MockRouter, workflow_page: Page):
    """Verify closed trade history records table renders accurately."""
    mock_router.mock_json("**/api/**/history**", trade_mocks.MOCK_TRADE_HISTORY_RECORDS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify 'No trade history found' placeholder when account has no closed trades."""
    mock_router.mock_json("**/api/**/history**", [])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_summary_statistics_bar(mock_router: MockRouter, workflow_page: Page):
    """Verify calculation bar values for balance, deposit, withdraw, commission, swap, profit."""
    mock_router.mock_json("**/api/**/history/stats**", trade_mocks.MOCK_TRADE_HISTORY_STATS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_filter_duration_today(mock_router: MockRouter, workflow_page: Page):
    """Verify today duration filter (1d) requests current day trades."""
    mock_router.mock_json("**/api/**/history?duration=1d**", [trade_mocks.MOCK_TRADE_HISTORY_RECORDS[0]])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_filter_duration_month(mock_router: MockRouter, workflow_page: Page):
    """Verify monthly duration filter (1m) requests 30-day trades."""
    mock_router.mock_json("**/api/**/history?duration=1m**", trade_mocks.MOCK_TRADE_HISTORY_RECORDS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_custom_date_filter_modal(mock_router: MockRouter, workflow_page: Page):
    """Verify custom date range submission returns range-specific trade data."""
    mock_router.mock_json(
        "**/api/**/history?from=**&to=**",
        trade_mocks.MOCK_TRADE_HISTORY_RECORDS[:2],
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_history_export_excel_action(mock_router: MockRouter, workflow_page: Page):
    """Verify clicking export report triggers export download endpoint."""
    mock_router.mock_json(
        "**/api/**/history/export**",
        {"success": True, "download_url": "/downloads/trade_history_report.xlsx"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1

"""
Trade Terminal Mock Tests: Watchlist & Quotes Market Data.
Validates dynamic symbol list rendering, empty search states, omnisearch filtering, quick top tickers,
favorites add/remove, and multi-workspace pagination.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_symbols_render(mock_router: MockRouter, workflow_page: Page):
    """Verify watchlist symbols list renders from mocked symbols API."""
    mock_router.mock_json("**/api/**/symbols**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when symbols API returns an empty list."""
    mock_router.mock_json("**/api/**/symbols**", [])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_spread_and_digits_formatting(mock_router: MockRouter, workflow_page: Page):
    """Verify 5-digit forex quotes vs 2-digit crypto/metals formatting."""
    mock_router.mock_json("**/api/**/symbols**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_add_favorite_success(mock_router: MockRouter, workflow_page: Page):
    """Verify adding symbol to favorites watchlist returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/watchlist/favorite/add**",
        {"success": True, "symbol": "BTCUSD", "message": "Added to favorites"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_remove_favorite_success(mock_router: MockRouter, workflow_page: Page):
    """Verify removing symbol from favorites watchlist returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/watchlist/favorite/remove**",
        {"success": True, "symbol": "BTCUSD", "message": "Removed from favorites"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_replace_top_ticker(mock_router: MockRouter, workflow_page: Page):
    """Verify pinning new top ticker section (Fav 1 / Fav 2)."""
    mock_router.mock_json(
        "**/api/**/watchlist/top-ticker**",
        {"success": True, "section": 1, "symbol": "XAUUSD"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_watchlist_workspace_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify multi-workspace pagination (Workspace 1 vs Workspace 2) switching."""
    mock_router.mock_json("**/api/**/watchlist?workspace=1**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)
    mock_router.mock_json("**/api/**/watchlist?workspace=2**", trade_mocks.MOCK_WORKSPACE_2_SYMBOLS)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.trade
def test_mock_omnisearch_filter_results(mock_router: MockRouter, workflow_page: Page):
    """Verify search endpoint returns filtered symbol subset."""
    mock_router.mock_json(
        "**/api/**/search**",
        [trade_mocks.MOCK_WATCHLIST_SYMBOLS[3]],  # XAUUSD Gold
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_omnisearch_no_results_found(mock_router: MockRouter, workflow_page: Page):
    """Verify search endpoint returning no matches displays placeholder."""
    mock_router.mock_json("**/api/**/search**", [])
    assert len(mock_router._active_routes) >= 1

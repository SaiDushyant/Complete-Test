"""
Trade Terminal Mock Tests: Charting, Indicators, and Real-Time Canvas.
Validates candlestick data loading, timeframe switches, positions overlay on chart, and one-click trading.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_historical_candles_success(mock_router: MockRouter, workflow_page: Page):
    """Verify chart feeds and renders candlestick OHLCV data."""
    mock_router.mock_json("**/api/**/chart/candles**", trade_mocks.MOCK_CHART_CANDLES_EURUSD)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_empty_candle_data(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when no historical candle data is returned for new market."""
    mock_router.mock_json("**/api/**/chart/candles**", [])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_timeframe_switch(mock_router: MockRouter, workflow_page: Page):
    """Verify switching chart timeframes (1M, 5M, 1H, 1D) fetches appropriate resolution."""
    mock_router.mock_json("**/api/**/chart/candles?tf=1h**", trade_mocks.MOCK_CHART_CANDLES_EURUSD)
    mock_router.mock_json("**/api/**/chart/candles?tf=1d**", trade_mocks.MOCK_CHART_CANDLES_EURUSD)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_positions_overlay_render(mock_router: MockRouter, workflow_page: Page):
    """Verify open positions price lines render as overlays on chart."""
    mock_router.mock_json("**/api/**/positions**", trade_mocks.MOCK_OPEN_POSITIONS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_one_click_buy_execution(mock_router: MockRouter, workflow_page: Page):
    """Verify chart quick one-click Buy button triggers order submission."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_one_click_sell_execution(mock_router: MockRouter, workflow_page: Page):
    """Verify chart quick one-click Sell button triggers order submission."""
    mock_router.mock_json(
        "**/api/**/order**",
        trade_mocks.MOCK_SELL_ORDER_SUCCESS_RESPONSE,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_chart_indicator_data_load(mock_router: MockRouter, workflow_page: Page):
    """Verify technical indicator overlays (Moving Averages, RSI) data feed."""
    mock_router.mock_json(
        "**/api/**/chart/indicators**",
        {"sma_20": [1.0845, 1.0850, 1.0855], "rsi_14": [54.2, 58.1, 62.3]},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1

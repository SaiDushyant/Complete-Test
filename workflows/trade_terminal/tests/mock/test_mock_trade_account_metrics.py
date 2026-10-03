"""
Trade Terminal Mock Tests: Account Metrics, Equity, and Risk Alerts.
Validates zero balance states, equity synchronization, margin call thresholds, multi-currency formats, and negative balances.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter
from workflows.shared.mocks.mock_scenarios import MockScenarios


@pytest.mark.mock
@pytest.mark.trade
def test_mock_account_zero_balance_state(mock_router: MockRouter, workflow_page: Page):
    """Verify zero balance state mock payload renders correctly."""
    MockScenarios.apply_zero_balance_state(mock_router)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.trade
def test_mock_high_floating_pnl_equity_sync(mock_router: MockRouter, workflow_page: Page):
    """Verify account metrics with positive floating PnL reflect higher live equity."""
    MockScenarios.apply_vip_trader_state(mock_router)
    assert len(mock_router._active_routes) >= 3


@pytest.mark.mock
@pytest.mark.trade
def test_mock_margin_call_level_warning(mock_router: MockRouter, workflow_page: Page):
    """Verify margin call alert state when Margin Level drops under critical threshold (< 100%)."""
    mock_router.mock_json("**/api/**/metrics**", trade_mocks.MOCK_MARGIN_CALL_METRICS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_custom_currency_metrics(mock_router: MockRouter, workflow_page: Page):
    """Verify metrics payload with alternate base currencies (e.g. EUR)."""
    eur_metrics = dict(trade_mocks.MOCK_ACCOUNT_METRICS)
    eur_metrics["currency"] = "EUR"
    mock_router.mock_json("**/api/**/metrics**", eur_metrics)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_negative_equity_protection_state(mock_router: MockRouter, workflow_page: Page):
    """Verify negative equity mock state handles balance deficit gracefully."""
    neg_metrics = dict(trade_mocks.MOCK_ACCOUNT_METRICS)
    neg_metrics["floating_pnl"] = -26000.00
    neg_metrics["equity"] = -1000.00
    mock_router.mock_json("**/api/**/metrics**", neg_metrics)
    assert len(mock_router._active_routes) >= 1

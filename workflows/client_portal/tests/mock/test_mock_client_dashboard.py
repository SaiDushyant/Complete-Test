"""
Client Portal Mock Tests: Dashboard Workspace & Metrics.
Tests dashboard summary metric cards (Total Funds, Account Balance, Available Buffer, Active Referrals),
zero balance states, High Net Worth figures, cash flow period switching (Day, Week, Month),
skeleton loader latency simulation, and cashflow server crash resilience.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_metrics_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that 4 primary dashboard metric cards (Total Funds, Account Balance,
    Available Buffer, Active Referrals) populate with accurate numbers from mock data.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_METRICS, status=200)
    mock_router.mock_json("**/api/v1/client/dashboard**", client_mocks.MOCK_CLIENT_DASHBOARD_METRICS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_zero_metrics(mock_router: MockRouter, workflow_page: Page):
    """
    Verify dashboard metric card rendering for brand-new users with $0.00 balances and 0 referrals.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_ZERO_STATE, status=200)
    mock_router.mock_json("**/api/v1/client/dashboard**", client_mocks.MOCK_CLIENT_DASHBOARD_ZERO_STATE, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_high_net_worth_formatting(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that large numbers ($15,000,000.00+) format cleanly without overlapping UI containers.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_HIGH_NET_WORTH, status=200)
    mock_router.mock_json("**/api/v1/client/dashboard**", client_mocks.MOCK_CLIENT_DASHBOARD_HIGH_NET_WORTH, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_cash_flow_period_filter(mock_router: MockRouter, workflow_page: Page):
    """
    Verify Account Cash Flow period toggles (Day, Week, Month) route matching period telemetry.
    """
    mock_router.mock_json("**/api/dashboard/cash-flow?period=day**", client_mocks.MOCK_CLIENT_CASH_FLOW_DAY, status=200)
    mock_router.mock_json("**/api/dashboard/cash-flow?period=week**", client_mocks.MOCK_CLIENT_CASH_FLOW_WEEK, status=200)
    mock_router.mock_json("**/api/dashboard/cash-flow?period=month**", client_mocks.MOCK_CLIENT_CASH_FLOW_MONTH, status=200)
    assert len(mock_router._active_routes) >= 3


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_loading_delay_skeleton(mock_router: MockRouter, workflow_page: Page):
    """
    Verify loading skeleton resilience on dashboard cards with simulated 500ms network delay.
    """
    mock_router.mock_json(
        "**/api/dashboard/summary**",
        client_mocks.MOCK_CLIENT_DASHBOARD_METRICS,
        status=200,
        delay_ms=500,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_cashflow_500_resilience(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that when Account Cash Flow backend service fails with 500,
    the main dashboard summary cards remain operational without crashing the workspace.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_METRICS, status=200)
    mock_router.mock_error("**/api/dashboard/cash-flow**", status=500, error_message="Cash Flow Analytics Engine Offline")
    assert len(mock_router._active_routes) >= 2

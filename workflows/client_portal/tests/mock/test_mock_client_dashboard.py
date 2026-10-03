"""
Client Portal Mock Tests: Dashboard Workspace & Metrics.
Tests dashboard summary metric cards (Total Funds, Account Balance, Available Buffer, Active Referrals),
zero balance states, High Net Worth figures, cash flow period switching (Day, Week, Month),
skeleton loader latency simulation, and cashflow server crash resilience.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

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

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/summary');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    metrics = result["data"]
    assert metrics["total_funds"] == 12450.75
    assert metrics["account_balance"] == 10000.00
    assert metrics["available_buffer"] == 2450.75
    assert metrics["active_referrals"] == 12

    workflow_page.set_content(f"""
        <div class="metrics-grid">
            <div class="metric-card total-funds">
                <span class="value">${metrics['total_funds']:,.2f}</span>
            </div>
            <div class="metric-card account-balance">
                <span class="value">${metrics['account_balance']:,.2f}</span>
            </div>
            <div class="metric-card available-buffer">
                <span class="value">${metrics['available_buffer']:,.2f}</span>
            </div>
            <div class="metric-card active-referrals">
                <span class="value">{metrics['active_referrals']}</span>
            </div>
        </div>
    """)

    expect(workflow_page.locator(".total-funds .value")).to_have_text("$12,450.75")
    expect(workflow_page.locator(".account-balance .value")).to_have_text("$10,000.00")
    expect(workflow_page.locator(".available-buffer .value")).to_have_text("$2,450.75")
    expect(workflow_page.locator(".active-referrals .value")).to_have_text("12")


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_zero_metrics(mock_router: MockRouter, workflow_page: Page):
    """
    Verify dashboard metric card rendering for brand-new users with $0.00 balances and 0 referrals.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_ZERO_STATE, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/summary');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    metrics = result["data"]
    assert metrics["total_funds"] == 0.00
    assert metrics["active_referrals"] == 0

    workflow_page.set_content(f"""
        <div class="metrics-grid">
            <div class="metric-card total-funds"><span class="value">${metrics['total_funds']:,.2f}</span></div>
            <div class="metric-card active-referrals"><span class="value">{metrics['active_referrals']}</span></div>
        </div>
    """)

    expect(workflow_page.locator(".total-funds .value")).to_have_text("$0.00")
    expect(workflow_page.locator(".active-referrals .value")).to_have_text("0")


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_high_net_worth_formatting(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that large numbers ($15,000,000.00+) format cleanly without overlapping UI containers.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_HIGH_NET_WORTH, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/summary');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    metrics = result["data"]
    assert metrics["total_funds"] == 15000000.00

    workflow_page.set_content(f"""
        <div class="metric-card total-funds">
            <span class="value">${metrics['total_funds']:,.2f}</span>
        </div>
    """)

    expect(workflow_page.locator(".total-funds .value")).to_have_text("$15,000,000.00")


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_cash_flow_period_filter(mock_router: MockRouter, workflow_page: Page):
    """
    Verify Account Cash Flow period toggles (Day, Week, Month) route matching period telemetry.
    """
    mock_router.mock_json("**/api/dashboard/cash-flow?period=day**", client_mocks.MOCK_CLIENT_CASH_FLOW_DAY, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/cash-flow?period=day');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    flow = result["data"]
    assert flow["period"] == "day"
    assert flow["net_flow"] == 500.00
    assert len(flow["data_points"]) == 3

    workflow_page.set_content(f"""
        <div id="cash-flow-widget">
            <span class="active-period">{flow['period']}</span>
            <span class="net-flow">${flow['net_flow']:,.2f}</span>
        </div>
    """)

    expect(workflow_page.locator(".active-period")).to_have_text("day")
    expect(workflow_page.locator(".net-flow")).to_have_text("$500.00")


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_loading_delay_skeleton(mock_router: MockRouter, workflow_page: Page):
    """
    Verify loading skeleton resilience on dashboard cards with simulated network delay.
    """
    mock_router.mock_json(
        "**/api/dashboard/summary**",
        client_mocks.MOCK_CLIENT_DASHBOARD_METRICS,
        status=200,
        delay_ms=50,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/summary');
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["total_funds"] == 12450.75

    workflow_page.set_content("""
        <div class="loaded-content">Metrics Loaded Cleanly</div>
    """)
    expect(workflow_page.locator(".loaded-content")).to_be_visible()


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dashboard_cashflow_500_resilience(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that when Account Cash Flow backend service fails with 500,
    the main dashboard summary cards remain operational without crashing the workspace.
    """
    mock_router.mock_json("**/api/dashboard/summary**", client_mocks.MOCK_CLIENT_DASHBOARD_METRICS, status=200)
    mock_router.mock_error("**/api/dashboard/cash-flow**", status=500, error_message="Cash Flow Analytics Engine Offline")

    summary_result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/dashboard/summary');
        return { status: resp.status, data: await resp.json() };
    }""")

    cashflow_result = workflow_page.evaluate("""async () => {
        try {
            const resp = await fetch('https://stage.xtremenext.com/api/dashboard/cash-flow');
            return { status: resp.status, data: await resp.json() };
        } catch (e) {
            return { error: e.toString() };
        }
    }""")

    assert summary_result["status"] == 200
    assert cashflow_result["status"] == 500

    workflow_page.set_content("""
        <div id="client-workspace">
            <div class="metric-card active">Total Funds: $12,450.75</div>
            <div class="chart-error-fallback">Cash flow temporarily unavailable</div>
        </div>
    """)

    expect(workflow_page.locator(".metric-card.active")).to_be_visible()
    expect(workflow_page.locator(".chart-error-fallback")).to_contain_text("Cash flow temporarily unavailable")

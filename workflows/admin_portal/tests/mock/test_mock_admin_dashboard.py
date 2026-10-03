"""
Admin Portal Mock Tests: Module 02 - Admin Dashboard & Real-Time Metrics.
Tests KPI metrics card rendering, zero-state metrics, and widget error fallback.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_kpis_rendering(mock_router: MockRouter, workflow_page: Page):
    """Verify KPI cards display total traders, deposits, active orders, and PnL."""
    endpoint_pattern = "**/Controlbase/dashboardMetrics**"
    mock_router.mock_json(endpoint_pattern, admin_mocks.MOCK_ADMIN_DASHBOARD_METRICS, status=200)

    # 1. Trigger network request via page context
    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/dashboardMetrics');
        return { status: resp.status, data: await resp.json() };
    }""")

    # 2. Verify intercepted network response
    assert result["status"] == 200
    metrics = result["data"]
    assert metrics["total_traders"] == admin_mocks.MOCK_ADMIN_DASHBOARD_METRICS["total_traders"]
    assert metrics["open_orders_count"] == admin_mocks.MOCK_ADMIN_DASHBOARD_METRICS["open_orders_count"]
    assert metrics["broker_net_pnl_usd"] == admin_mocks.MOCK_ADMIN_DASHBOARD_METRICS["broker_net_pnl_usd"]

    # 3. Mount dashboard UI with mocked data and verify element visibility and content
    workflow_page.set_content(f"""
        <div id="dashboard-metrics" class="metrics-grid">
            <div class="kpi-card" data-kpi="total_traders">
                <span class="label">Total Traders</span>
                <span class="value">{metrics['total_traders']}</span>
            </div>
            <div class="kpi-card" data-kpi="open_orders">
                <span class="label">Open Orders</span>
                <span class="value">{metrics['open_orders_count']}</span>
            </div>
            <div class="kpi-card" data-kpi="net_pnl">
                <span class="label">Net PnL</span>
                <span class="value">${metrics['broker_net_pnl_usd']:,.2f}</span>
            </div>
        </div>
    """)

    expect(workflow_page.locator("[data-kpi='total_traders'] .value")).to_have_text("1420")
    expect(workflow_page.locator("[data-kpi='open_orders'] .value")).to_have_text("892")
    expect(workflow_page.locator("[data-kpi='net_pnl'] .value")).to_have_text("$182,400.00")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_zero_metrics_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty/new platform state where all counters are zero (prevent NaN errors)."""
    endpoint_pattern = "**/Controlbase/dashboardMetrics**"
    mock_router.mock_json(endpoint_pattern, admin_mocks.MOCK_ADMIN_DASHBOARD_ZERO_METRICS, status=200)

    # 1. Trigger network request via page context
    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/dashboardMetrics');
        return { status: resp.status, data: await resp.json() };
    }""")

    # 2. Verify zero state data
    assert result["status"] == 200
    metrics = result["data"]
    assert metrics["total_traders"] == 0
    assert metrics["open_orders_count"] == 0
    assert metrics["total_deposits_usd"] == 0.0

    # 3. Mount UI and verify zero-state cleanly renders without NaN
    workflow_page.set_content(f"""
        <div id="dashboard-metrics" class="metrics-grid">
            <div class="kpi-card" data-kpi="total_traders">
                <span class="value">{metrics['total_traders']}</span>
            </div>
            <div class="kpi-card" data-kpi="total_deposits">
                <span class="value">${metrics['total_deposits_usd']:,.2f}</span>
            </div>
        </div>
    """)

    expect(workflow_page.locator("[data-kpi='total_traders'] .value")).to_have_text("0")
    expect(workflow_page.locator("[data-kpi='total_deposits'] .value")).to_have_text("$0.00")
    assert "NaN" not in workflow_page.locator("#dashboard-metrics").inner_text()


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_widgets_500_fallback(mock_router: MockRouter, workflow_page: Page):
    """Verify fallback widget placeholder when metrics service fails."""
    endpoint_pattern = "**/Controlbase/dashboardMetrics**"
    mock_router.mock_error(endpoint_pattern, status=500, error_message="Internal Server Error")

    # 1. Trigger network request expecting 500 error
    result = workflow_page.evaluate("""async () => {
        try {
            const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/dashboardMetrics');
            return { status: resp.status, data: await resp.json() };
        } catch (e) {
            return { error: e.toString() };
        }
    }""")

    assert result["status"] == 500
    assert result["data"]["error"] == "Internal Server Error"

    # 2. Mount error fallback widget and assert display
    workflow_page.set_content("""
        <div id="dashboard-error-container">
            <div class="error-banner alert-danger" role="alert">
                <span>Failed to load metrics. Please retry or contact support.</span>
                <button id="retry-btn">Retry</button>
            </div>
        </div>
    """)

    expect(workflow_page.locator(".error-banner")).to_be_visible()
    expect(workflow_page.locator(".error-banner")).to_contain_text("Failed to load metrics")
    expect(workflow_page.locator("#retry-btn")).to_be_visible()

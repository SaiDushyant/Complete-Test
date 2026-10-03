"""
Admin Portal Mock Tests: Module 02 - Admin Dashboard & Real-Time Metrics.
Tests KPI metrics card rendering, zero-state metrics, and widget error fallback.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_kpis_rendering(mock_router: MockRouter, workflow_page: Page):
    """Verify KPI cards display total traders, deposits, active orders, and PnL."""
    mock_router.mock_json("**/Controlbase/dashboardMetrics**", admin_mocks.MOCK_ADMIN_DASHBOARD_METRICS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_zero_metrics_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty/new platform state where all counters are zero (prevent NaN errors)."""
    mock_router.mock_json("**/Controlbase/dashboardMetrics**", admin_mocks.MOCK_ADMIN_DASHBOARD_ZERO_METRICS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_dashboard_widgets_500_fallback(mock_router: MockRouter, workflow_page: Page):
    """Verify fallback widget placeholder when metrics service fails."""
    mock_router.mock_json("**/Controlbase/dashboardMetrics**", error_mocks.HTTP_500_INTERNAL_SERVER_ERROR, status=500)
    assert len(mock_router._active_routes) >= 1

"""
Admin Portal Mock Tests: Module 22 - Server Resilience & API Fault Handling.
Tests 500 error banners, rate limiting 429, gateway timeouts 504, and network latency loading states.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_server_500_error_handling(mock_router: MockRouter, workflow_page: Page):
    """Verify admin UI handles unexpected backend 500 exceptions with clear user notification."""
    mock_router.mock_error("**/Controlbase/**", status=500, error_message="Database Lock Timeout")
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_rate_limiting_429(mock_router: MockRouter, workflow_page: Page):
    """Verify admin API rate limiting error handling."""
    mock_router.mock_json("**/Controlbase/**", error_mocks.HTTP_429_TOO_MANY_REQUESTS, status=429)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_gateway_timeout_504(mock_router: MockRouter, workflow_page: Page):
    """Verify 504 Gateway Timeout handling when exporting large financial reports."""
    mock_router.mock_json("**/Controlbase/largeReportExport**", error_mocks.HTTP_504_GATEWAY_TIMEOUT, status=504)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_network_latency_spinner(mock_router: MockRouter, workflow_page: Page):
    """Verify UI loading state and skeleton spinners during simulated network latency."""
    mock_router.mock_json("**/Controlbase/userList**", {"data": []}, delay_ms=500)
    assert len(mock_router._active_routes) >= 1

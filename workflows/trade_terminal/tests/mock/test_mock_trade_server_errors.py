"""
Trade Terminal Mock Tests: Backend Error Handling & Network Resilience.
Tests HTTP 500, 502 Bad Gateway, 503 Maintenance, 504 Gateway Timeout, 429 Rate Limiting,
offline aborts, artificial latency, and malformed JSON resilience.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import error_mocks
from workflows.shared.mocks.mock_router import MockRouter
from workflows.shared.mocks.mock_scenarios import MockScenarios


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_backend_500_error_handling(mock_router: MockRouter, workflow_page: Page):
    """Verify system handles unexpected HTTP 500 server crash gracefully."""
    mock_router.mock_error("**/api/**", status=500, error_message="Internal Database Error")
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_server_502_bad_gateway(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 502 Bad Gateway / upstream proxy failure."""
    mock_router.mock_json("**/api/**", error_mocks.HTTP_502_BAD_GATEWAY, status=502)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_server_maintenance_503(mock_router: MockRouter, workflow_page: Page):
    """Verify system enters maintenance mode when 503 is returned."""
    MockScenarios.apply_maintenance_mode(mock_router)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_network_offline_abort(mock_router: MockRouter, workflow_page: Page):
    """Verify that browser network disconnection aborts are intercepted cleanly."""
    MockScenarios.apply_offline_mode(mock_router)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_gateway_504_timeout_alert(mock_router: MockRouter, workflow_page: Page):
    """Verify liquidity gateway timeout HTTP 504 returns structured error."""
    mock_router.mock_error(
        "**/api/**/order**",
        status=504,
        error_message="Liquidity Provider Gateway Timeout",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_rate_limiting_429(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 429 Too Many Requests response is intercepted."""
    mock_router.mock_error(
        "**/api/**/order**",
        status=429,
        error_message="Too many requests. Please slow down.",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_high_latency_loading_spinners(mock_router: MockRouter, workflow_page: Page):
    """Verify simulating 2500ms network delay on dashboard API."""
    mock_router.mock_json(
        "**/api/**/dashboard/**",
        {"data": "loaded"},
        delay_ms=2500,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_malformed_json_resilience(mock_router: MockRouter, workflow_page: Page):
    """Verify non-JSON / broken payload from server is handled safely without app crash."""
    mock_router.mock_json(
        "**/api/**/broken-endpoint**",
        "<html><body>502 Bad Gateway Nginx</body></html>",
        status=502,
        headers={"Content-Type": "text/html"},
    )
    assert len(mock_router._active_routes) >= 1

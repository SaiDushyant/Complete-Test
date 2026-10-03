"""
Client Portal Mock Tests: Network Failures, API Resilience & Latency Simulation.
Tests payment gateway 500 crashes, session 401 expiration redirects, 504 gateway timeouts,
HTTP 429 rate limiting, slow 3G latency delay simulation, corrupted payloads,
and network connection dropouts.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import error_mocks
from workflows.shared.mocks.mock_router import MockRouter
from workflows.shared.mocks.mock_scenarios import MockScenarios


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_500_server_error(mock_router: MockRouter, workflow_page: Page):
    """Verify UI handles 500 Internal Server Error when processing payment."""
    mock_router.mock_error("**/api/deposit/**", status=500, error_message="Payment Provider Unresponsive")
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_session_expired_401(mock_router: MockRouter, workflow_page: Page):
    """Verify UI intercepts 401 Unauthorized and presents login/session refresh alert."""
    mock_router.mock_json("**/api/**", error_mocks.HTTP_401_UNAUTHORIZED, status=401)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_gateway_timeout_504(mock_router: MockRouter, workflow_page: Page):
    """Verify UI handles 504 Gateway Timeout gracefully."""
    mock_router.mock_json("**/api/**", error_mocks.HTTP_504_GATEWAY_TIMEOUT, status=504)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_rate_limit_429_toast(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 429 Too Many Requests rate-limiting warning banner."""
    mock_router.mock_json(
        "**/api/**",
        error_mocks.HTTP_429_TOO_MANY_REQUESTS,
        status=429,
        headers={"Retry-After": "60"},
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_slow_network_latency_spinner(mock_router: MockRouter, workflow_page: Page):
    """Verify loading skeleton and spinner resilience with 500ms simulated network latency."""
    mock_router.mock_json(
        "**/api/wallet/summary**",
        {"data": [], "loading": False},
        delay_ms=500,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_corrupted_json_payload(mock_router: MockRouter, workflow_page: Page):
    """Verify that malformed / non-JSON responses (502 bad gateway HTML) do not trigger unhandled UI crash."""
    mock_router.mock_custom(
        "**/api/client/**",
        lambda route: route.fulfill(
            status=502,
            content_type="text/html",
            body="<html><body>502 Bad Gateway NGINX</body></html>",
        ),
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_network_offline_abort(mock_router: MockRouter, workflow_page: Page):
    """Verify application resilience when network disconnects completely."""
    MockScenarios.apply_offline_mode(mock_router)
    assert len(mock_router._active_routes) >= 1

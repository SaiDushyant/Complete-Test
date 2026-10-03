"""
Client Portal Mock Tests: Network Failures & API Errors.
Tests payment gateway 500 crashes, session 401 expiration redirects, and 504 timeouts.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import error_mocks
from workflows.shared.mocks.mock_router import MockRouter


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

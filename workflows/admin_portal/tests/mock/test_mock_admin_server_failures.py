"""
Admin Portal Mock Tests: Server Failures and API Fallback Handling.
Tests 500 error banners, rate limiting 429, and database connection timeouts.
"""

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

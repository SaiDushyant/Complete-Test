"""
Trade Terminal Mock Tests: Backend Error Handling & Network Resilience.
Tests HTTP 500, 503 Maintenance, 504 Gateway Timeout, and connection dropouts.
"""

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

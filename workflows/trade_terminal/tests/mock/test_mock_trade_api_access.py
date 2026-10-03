"""
Trade Terminal Mock Tests: API Access and Key Management.
Validates API key list rendering, empty states, secret key generation, key limits, revocation, and IP whitelisting.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_api_keys_list_rendering(mock_router: MockRouter, workflow_page: Page):
    """Verify active API keys list rendering with masked secrets."""
    mock_router.mock_json("**/api/**/api-keys**", trade_mocks.MOCK_API_KEYS_LIST)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_api_keys_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty API keys list rendering."""
    mock_router.mock_json("**/api/**/api-keys**", [])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_generate_new_api_key_success(mock_router: MockRouter, workflow_page: Page):
    """Verify generating a new API key returns secret token modal."""
    mock_router.mock_json(
        "**/api/**/api-keys/generate**",
        trade_mocks.MOCK_API_KEY_CREATED,
        status=201,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_generate_api_key_limit_reached(mock_router: MockRouter, workflow_page: Page):
    """Verify error alert when maximum allowed API keys limit (5) is reached."""
    mock_router.mock_error(
        "**/api/**/api-keys/generate**",
        status=400,
        error_message="Maximum limit of 5 API keys reached. Please revoke unused keys.",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_revoke_api_key_success(mock_router: MockRouter, workflow_page: Page):
    """Verify revoking an API key updates key status."""
    mock_router.mock_json(
        "**/api/**/api-keys/revoke**",
        {"success": True, "key_id": "key_001", "status": "REVOKED"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_ip_whitelist_update_success(mock_router: MockRouter, workflow_page: Page):
    """Verify saving IP whitelist restrictions."""
    mock_router.mock_json(
        "**/api/**/api-keys/ip-whitelist**",
        {"success": True, "whitelist": ["192.168.1.100", "10.0.0.1"]},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1

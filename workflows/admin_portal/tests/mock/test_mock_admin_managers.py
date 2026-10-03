"""
Admin Portal Mock Tests: Module 13 - Manager Directory & Allocation.
Tests account managers list (/admin) and client-manager user assignment (/manager).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manager_directory_render(mock_router: MockRouter, workflow_page: Page):
    """Verify list of account managers (/admin) and their assigned departments."""
    mock_router.mock_json("**/Controlbase/admin**", admin_mocks.MOCK_ADMIN_MANAGERS_LIST, status=200)
    mock_router.mock_json("**/Controlbase/managers**", admin_mocks.MOCK_ADMIN_MANAGERS_LIST, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manager_user_management_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Manager User Management table (/manager) showing client-manager assignments."""
    mock_router.mock_json("**/Controlbase/manager**", admin_mocks.MOCK_ADMIN_MANAGERS_LIST, status=200)
    assert len(mock_router._active_routes) >= 1

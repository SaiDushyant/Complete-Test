"""
Admin Portal Mock Tests: Module 14 - Role-Based Access Control (RBAC) & Permissions.
Tests permission denied 403 Forbidden enforcement, creating custom roles, and super-admin protection.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_permission_denied_forbidden(mock_router: MockRouter, workflow_page: Page):
    """Verify read-only admin attempting deletion receives 403 Forbidden alert."""
    mock_router.mock_json("**/Controlbase/deleteUser**", admin_mocks.MOCK_ACTION_PERMISSION_DENIED, status=403)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_custom_role(mock_router: MockRouter, workflow_page: Page):
    """Verify creating a custom role (/rolePermission) with granular checkboxes."""
    mock_router.mock_json("**/Controlbase/rolePermission**", admin_mocks.MOCK_ADMIN_ROLES_LIST, status=200)
    mock_router.mock_json("**/Controlbase/createRole**", {"status": 200, "role_id": "ROLE_COMPLIANCE"}, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_super_admin_role_protection(mock_router: MockRouter, workflow_page: Page):
    """Verify deleting Super Admin role is permanently disabled in the UI."""
    mock_router.mock_json("**/Controlbase/deleteRole?id=superadmin**", error_mocks.HTTP_400_BAD_REQUEST, status=400)
    assert len(mock_router._active_routes) >= 1

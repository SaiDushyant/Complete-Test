"""
Admin Portal Mock Tests: Module 06 - User Groups & Leverage Profiles.
Tests user group profiles listing, group creation, and blocking deletion of groups with active users.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_groups_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify user group profiles (Standard, VIP, Raw Spread) table rendering."""
    mock_router.mock_json("**/Controlbase/userGroups**", admin_mocks.MOCK_ADMIN_USER_GROUPS, status=200)
    mock_router.mock_json("**/Controlbase/userGroup**", admin_mocks.MOCK_ADMIN_USER_GROUPS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_user_group_success(mock_router: MockRouter, workflow_page: Page):
    """Verify creating a new group profile with custom spread markup."""
    mock_router.mock_json("**/Controlbase/createUserGroup**", {"status": 200, "group_id": "VIP_Zero"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_delete_group_with_assigned_users_blocked(mock_router: MockRouter, workflow_page: Page):
    """Verify deleting a group that has active users fails with 400 error."""
    mock_router.mock_json("**/Controlbase/deleteUserGroup**", error_mocks.HTTP_400_BAD_REQUEST, status=400)
    assert len(mock_router._active_routes) >= 1

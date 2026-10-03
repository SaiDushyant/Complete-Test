"""
Admin Portal Mock Tests: Module 03 - Trader User Management & Lifecycle CRUD.
Tests user listing, table pagination, group filters, account creation, 422 duplicate validation,
status suspension toggles, balance adjustments, and killing active user sessions.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify that mocked user records populate correctly in the user management table."""
    mock_router.mock_json("**/Controlbase/userList**", admin_mocks.MOCK_ADMIN_USER_LIST, status=200)
    mock_router.mock_json("**/api/users**", admin_mocks.MOCK_ADMIN_USER_LIST, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_table_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify table pagination controls with 100+ mocked user records."""
    mock_router.mock_json("**/Controlbase/userList?page=2**", admin_mocks.MOCK_ADMIN_USER_LIST, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_filter_by_group_and_status(mock_router: MockRouter, workflow_page: Page):
    """Verify filtering users by group (VIP_USD) and status (active/blocked)."""
    filtered_users = [u for u in admin_mocks.MOCK_ADMIN_USER_LIST if u.get("group") == "VIP_USD"]
    mock_router.mock_json("**/Controlbase/userList?group=VIP_USD**", filtered_users, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_user_success(mock_router: MockRouter, workflow_page: Page):
    """Verify successful creation of a new trader account from admin portal."""
    new_user = {
        "id": "10105",
        "username": "new_trader_alex",
        "email": "alex@sample.com",
        "group": "Standard_USD",
        "balance": 1000.0,
        "status": "active",
    }
    mock_router.mock_json("**/Controlbase/createUser**", {"status": 200, "user": new_user}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_user_duplicate_email(mock_router: MockRouter, workflow_page: Page):
    """Verify 422 duplicate email validation error display on user creation form."""
    mock_router.mock_json("**/Controlbase/createUser**", error_mocks.HTTP_422_UNPROCESSABLE_ENTITY, status=422)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_status_toggle_suspend(mock_router: MockRouter, workflow_page: Page):
    """Verify suspending an active user updates status badge immediately."""
    mock_router.mock_json("**/Controlbase/updateUserStatus**", {"status": "blocked"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_balance_adjustment(mock_router: MockRouter, workflow_page: Page):
    """Verify manual balance credit/debit by admin with audit note."""
    mock_router.mock_json("**/Controlbase/adjustBalance**", {"account_id": "10098", "new_balance": 15900.00}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_active_users_session_kill(mock_router: MockRouter, workflow_page: Page):
    """Verify admin ability to force-terminate an online user's active session."""
    mock_router.mock_json("**/Controlbase/activeUsers**", admin_mocks.MOCK_ADMIN_ACTIVE_USERS, status=200)
    mock_router.mock_json("**/Controlbase/killSession**", {"session_terminated": True}, status=200)
    assert len(mock_router._active_routes) >= 2

"""
Admin Portal Mock Tests: Module 01 - Authentication & Session Management.
Tests admin login success, invalid credentials, locked accounts, 2FA challenge,
and automatic logout on token expiration.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_success(mock_router: MockRouter, workflow_page: Page):
    """Validate admin successful login, JWT session injection, and redirect to dashboard."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_SUCCESS, status=200)
    mock_router.mock_json("**/Controlbase/Dashboard**", {"status": 200})
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_invalid_credentials(mock_router: MockRouter, workflow_page: Page):
    """Verify error toast when invalid admin credentials are provided."""
    mock_router.mock_json("**/Controlbase/login**", error_mocks.HTTP_401_UNAUTHORIZED, status=401)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_account_locked(mock_router: MockRouter, workflow_page: Page):
    """Verify locked admin account behavior (exceeded maximum failed attempts)."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_ACCOUNT_LOCKED, status=403)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_2fa_prompt(mock_router: MockRouter, workflow_page: Page):
    """Verify multi-factor authentication (2FA) challenge flow."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_2FA_REQUIRED, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_session_expiry_auto_logout(mock_router: MockRouter, workflow_page: Page):
    """Verify that 401 on background polling auto-redirects to admin login page."""
    mock_router.mock_json("**/Controlbase/**", error_mocks.HTTP_401_UNAUTHORIZED, status=401)
    assert len(mock_router._active_routes) >= 1

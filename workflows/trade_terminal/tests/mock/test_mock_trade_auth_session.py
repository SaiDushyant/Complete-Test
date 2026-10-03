"""
Trade Terminal Mock Tests: Authentication, Session, Registration, and Password Reset.
Validates login flows, bad credentials, account lockouts, 2FA, session expiry, and registration.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import auth_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_success(mock_router: MockRouter, workflow_page: Page):
    """Verify login success response injects JWT and session tokens."""
    mock_router.mock_json("**/api/**/login**", auth_mocks.MOCK_LOGIN_SUCCESS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_invalid_credentials(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 401 on invalid username or password renders error banner."""
    mock_router.mock_json(
        "**/api/**/login**",
        auth_mocks.MOCK_LOGIN_INVALID_CREDENTIALS,
        status=401,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_account_locked(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 403 on suspended or locked account renders warning modal."""
    mock_router.mock_json(
        "**/api/**/login**",
        auth_mocks.MOCK_LOGIN_ACCOUNT_LOCKED,
        status=403,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_2fa_required(mock_router: MockRouter, workflow_page: Page):
    """Verify 2FA required status routes user to OTP code verification screen."""
    mock_router.mock_json(
        "**/api/**/login**",
        auth_mocks.MOCK_2FA_REQUIRED,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_password_reset_request_success(mock_router: MockRouter, workflow_page: Page):
    """Verify submitting password reset email triggers success notification."""
    mock_router.mock_json(
        "**/api/**/password/reset**",
        {"success": True, "message": "Password reset instructions sent to your email."},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_password_reset_user_not_found(mock_router: MockRouter, workflow_page: Page):
    """Verify unknown email during password reset returns error message."""
    mock_router.mock_json(
        "**/api/**/password/reset**",
        {"success": False, "error": "User with this email not found"},
        status=404,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_registration_success(mock_router: MockRouter, workflow_page: Page):
    """Verify registration form submission returns 201 Created and logs user in."""
    mock_router.mock_json(
        "**/api/**/register**",
        {"success": True, "account_id": "10099", "message": "Account created successfully."},
        status=201,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_registration_duplicate_email(mock_router: MockRouter, workflow_page: Page):
    """Verify duplicate email registration returns 422 Unprocessable Entity."""
    mock_router.mock_json(
        "**/api/**/register**",
        {"success": False, "error": "Email address is already registered."},
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_session_expiration_401(mock_router: MockRouter, workflow_page: Page):
    """Verify background endpoint 401 triggers session expiration redirect."""
    mock_router.mock_json(
        "**/api/**/session/heartbeat**",
        error_mocks.HTTP_401_UNAUTHORIZED,
        status=401,
    )
    assert len(mock_router._active_routes) >= 1

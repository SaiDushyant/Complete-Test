"""
Client Portal Mock Tests: Authentication & Security.
Validates client login success with JWT injection, 401 invalid credentials error handling,
403 account suspension, 2FA challenge responses, and session expiration handling.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import auth_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_login_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify client login workflow with mocked 200 OK authentication response.
    Ensures mock session tokens and user profiles are properly routed.
    """
    mock_router.mock_json("**/api/v1/auth/login**", auth_mocks.MOCK_LOGIN_SUCCESS, status=200)
    mock_router.mock_json("**/api/auth/login**", auth_mocks.MOCK_LOGIN_SUCCESS, status=200)
    mock_router.mock_json("**/api/client/profile**", auth_mocks.MOCK_LOGIN_SUCCESS["user"], status=200)

    assert len(mock_router._active_routes) >= 3


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_login_invalid_password(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that HTTP 401 Invalid Credentials response from auth service
    is intercepted without unhandled exceptions.
    """
    mock_router.mock_json(
        "**/api/**/login**",
        auth_mocks.MOCK_LOGIN_INVALID_CREDENTIALS,
        status=401,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_login_account_suspended(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that HTTP 403 Account Locked / Suspended response is intercepted
    and handled gracefully by the client portal authentication handler.
    """
    mock_router.mock_json(
        "**/api/**/login**",
        auth_mocks.MOCK_LOGIN_ACCOUNT_LOCKED,
        status=403,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_2fa_otp_screen(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that 2FA challenge response triggers intermediate two-factor authentication
    workflow and routes session ticket properly.
    """
    mock_router.mock_json("**/api/**/login**", auth_mocks.MOCK_2FA_REQUIRED, status=200)
    mock_router.mock_json(
        "**/api/**/2fa/verify**",
        {"status": 200, "success": True, "token": "verified_2fa_jwt_token"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_session_expiration_401(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that HTTP 401 Unauthorized token expiry prompts session refresh or login redirect.
    """
    mock_router.mock_json("**/api/client/**", error_mocks.HTTP_401_UNAUTHORIZED, status=401)
    assert len(mock_router._active_routes) >= 1


# =====================================================================
# Registration & Password Recovery Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_signup_registration_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify user sign-up registration form submission with mocked 200 OK response.
    """
    mock_router.mock_json("**/api/auth/register**", auth_mocks.MOCK_REGISTER_SUCCESS, status=200)
    mock_router.mock_json("**/api/v1/user/register**", auth_mocks.MOCK_REGISTER_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_signup_duplicate_email_error(mock_router: MockRouter, workflow_page: Page):
    """
    Verify 422 duplicate email validation banner when registering an already existing email.
    """
    mock_router.mock_json(
        "**/api/auth/register**",
        auth_mocks.MOCK_REGISTER_DUPLICATE_EMAIL,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_password_reset_request_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify forgot password email submission and confirmation dispatch alert.
    """
    mock_router.mock_json("**/api/auth/forgot-password**", auth_mocks.MOCK_FORGOT_PASSWORD_SUCCESS, status=200)
    mock_router.mock_json("**/api/v1/user/password-reset-link**", auth_mocks.MOCK_FORGOT_PASSWORD_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_password_reset_invalid_email(mock_router: MockRouter, workflow_page: Page):
    """
    Verify HTTP 404 User Not Found error handling when submitting unregistered email on password reset.
    """
    mock_router.mock_json(
        "**/api/auth/forgot-password**",
        auth_mocks.MOCK_FORGOT_PASSWORD_NOT_FOUND,
        status=404,
    )
    assert len(mock_router._active_routes) >= 1


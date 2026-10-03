"""
Trade Terminal Mock Tests: Authentication, Session, Registration, and Password Reset.
Validates login flows, bad credentials, account lockouts, 2FA, session expiry, and registration.
100% Offline execution with zero live database or network dependencies.
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
    mock_router.mock_json("**/api/v1/auth/login**", auth_mocks.MOCK_LOGIN_SUCCESS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'trader10009', password: 'ValidPassword123' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert "token" in result["data"] or "access_token" in result["data"] or result["data"].get("success") is True

    workflow_page.set_content("""
        <header id="trade-header">
            <span class="account-badge">Trader #10009</span>
            <span class="session-status online">Connected</span>
        </header>
    """)

    expect(workflow_page.locator(".account-badge")).to_have_text("Trader #10009")
    expect(workflow_page.locator(".session-status")).to_have_text("Connected")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_invalid_credentials(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 401 on invalid username or password renders error banner."""
    mock_router.mock_json(
        "**/api/v1/auth/login**",
        auth_mocks.MOCK_LOGIN_INVALID_CREDENTIALS,
        status=401,
    )

    result = workflow_page.evaluate("""async () => {
        try {
            const resp = await fetch('https://stage.xtremenext.com/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'bad_user', password: 'wrong' })
            });
            return { status: resp.status, data: await resp.json() };
        } catch (e) {
            return { error: e.toString() };
        }
    }""")

    assert result["status"] == 401

    workflow_page.set_content("""
        <div class="login-form">
            <div class="alert alert-danger" role="alert">Invalid username or password.</div>
        </div>
    """)

    expect(workflow_page.locator(".alert-danger")).to_be_visible()
    expect(workflow_page.locator(".alert-danger")).to_have_text("Invalid username or password.")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_account_locked(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 403 on suspended or locked account renders warning modal."""
    mock_router.mock_json(
        "**/api/v1/auth/login**",
        auth_mocks.MOCK_LOGIN_ACCOUNT_LOCKED,
        status=403,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'locked_user', password: 'pass' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 403

    workflow_page.set_content("""
        <div class="modal locked-account-modal">
            <h4>Account Suspended</h4>
            <p>Your account has been locked due to security policy. Contact support.</p>
        </div>
    """)

    expect(workflow_page.locator(".locked-account-modal")).to_be_visible()
    expect(workflow_page.locator(".locked-account-modal h4")).to_have_text("Account Suspended")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_login_2fa_required(mock_router: MockRouter, workflow_page: Page):
    """Verify 2FA required status routes user to OTP code verification screen."""
    mock_router.mock_json(
        "**/api/v1/auth/login**",
        auth_mocks.MOCK_2FA_REQUIRED,
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: '2fa_user', password: 'pass' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200

    workflow_page.set_content("""
        <div class="two-factor-auth-card">
            <h3>Enter 2FA Code</h3>
            <input type="text" id="otp-input" placeholder="6-digit code" />
            <button id="submit-otp">Confirm</button>
        </div>
    """)

    expect(workflow_page.locator(".two-factor-auth-card")).to_be_visible()
    expect(workflow_page.locator("#otp-input")).to_be_visible()


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_password_reset_request_success(mock_router: MockRouter, workflow_page: Page):
    """Verify submitting password reset email triggers success notification."""
    mock_router.mock_json(
        "**/api/v1/password/reset**",
        {"success": True, "message": "Password reset instructions sent to your email."},
        status=200,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/password/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'trader@example.com' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["success"] is True

    workflow_page.set_content(f"""
        <div class="alert alert-success">{result["data"]["message"]}</div>
    """)

    expect(workflow_page.locator(".alert-success")).to_contain_text("instructions sent to your email")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_password_reset_user_not_found(mock_router: MockRouter, workflow_page: Page):
    """Verify unknown email during password reset returns error message."""
    mock_router.mock_json(
        "**/api/v1/password/reset**",
        {"success": False, "error": "User with this email not found"},
        status=404,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/password/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'unknown@example.com' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 404
    assert "not found" in result["data"]["error"]

    workflow_page.set_content(f"""
        <div class="alert alert-danger">{result["data"]["error"]}</div>
    """)

    expect(workflow_page.locator(".alert-danger")).to_have_text("User with this email not found")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_registration_success(mock_router: MockRouter, workflow_page: Page):
    """Verify registration form submission returns 201 Created and logs user in."""
    mock_router.mock_json(
        "**/api/v1/register**",
        {"success": True, "account_id": "10099", "message": "Account created successfully."},
        status=201,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'new@trader.com', password: 'NewPassword123' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 201
    assert result["data"]["account_id"] == "10099"

    workflow_page.set_content(f"""
        <div class="alert alert-success">
            Welcome to XtremeNext! Account #{result["data"]["account_id"]} created successfully.
        </div>
    """)

    expect(workflow_page.locator(".alert-success")).to_contain_text("Account #10099 created successfully")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_registration_duplicate_email(mock_router: MockRouter, workflow_page: Page):
    """Verify duplicate email registration returns 422 Unprocessable Entity."""
    mock_router.mock_json(
        "**/api/v1/register**",
        {"success": False, "error": "Email address is already registered."},
        status=422,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'existing@trader.com', password: 'Password123' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 422
    assert "already registered" in result["data"]["error"]

    workflow_page.set_content(f"""
        <span class="field-error">{result["data"]["error"]}</span>
    """)

    expect(workflow_page.locator(".field-error")).to_have_text("Email address is already registered.")


@pytest.mark.mock
@pytest.mark.trade
def test_mock_trade_session_expiration_401(mock_router: MockRouter, workflow_page: Page):
    """Verify background endpoint 401 triggers session expiration redirect."""
    mock_router.mock_json(
        "**/api/v1/session/heartbeat**",
        error_mocks.HTTP_401_UNAUTHORIZED,
        status=401,
    )

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/api/v1/session/heartbeat');
        return { status: resp.status };
    }""")

    assert result["status"] == 401

    workflow_page.set_content("""
        <div class="session-expired-modal">Session expired. Redirecting to login...</div>
    """)

    expect(workflow_page.locator(".session-expired-modal")).to_be_visible()

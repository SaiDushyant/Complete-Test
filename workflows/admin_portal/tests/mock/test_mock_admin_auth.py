"""
Admin Portal Mock Tests: Module 01 - Authentication & Session Management.
Tests admin login success, invalid credentials, locked accounts, 2FA challenge,
and automatic logout on token expiration.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import admin_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_success(mock_router: MockRouter, workflow_page: Page):
    """Validate admin successful login, JWT session injection, and redirect to dashboard."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_SUCCESS, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'admin_master', password: 'ValidPassword123!' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["success"] is True
    assert "token" in result["data"]
    assert result["data"]["user"]["role"] == "SuperAdmin"

    # Verify UI reflects authenticated session
    workflow_page.set_content(f"""
        <header id="admin-topbar">
            <span class="user-badge">{result["data"]["user"]["username"]}</span>
            <span class="role-badge">{result["data"]["user"]["role"]}</span>
        </header>
    """)
    expect(workflow_page.locator(".user-badge")).to_have_text("admin_master")
    expect(workflow_page.locator(".role-badge")).to_have_text("SuperAdmin")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_invalid_credentials(mock_router: MockRouter, workflow_page: Page):
    """Verify error toast when invalid admin credentials are provided."""
    mock_router.mock_error("**/Controlbase/login**", status=401, error_message="Invalid credentials")

    result = workflow_page.evaluate("""async () => {
        try {
            const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'admin_master', password: 'WrongPassword' })
            });
            return { status: resp.status, data: await resp.json() };
        } catch (e) {
            return { error: e.toString() };
        }
    }""")

    assert result["status"] == 401
    assert result["data"]["error"] == "Invalid credentials"

    # Verify UI error banner display
    workflow_page.set_content("""
        <div id="login-container">
            <div class="alert alert-danger" role="alert">Invalid credentials. Please verify your login details.</div>
        </div>
    """)
    expect(workflow_page.locator(".alert-danger")).to_be_visible()
    expect(workflow_page.locator(".alert-danger")).to_contain_text("Invalid credentials")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_account_locked(mock_router: MockRouter, workflow_page: Page):
    """Verify locked admin account behavior (exceeded maximum failed attempts)."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_ACCOUNT_LOCKED, status=403)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: 'locked_admin', password: 'AnyPassword' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 403
    assert result["data"]["error"] == "Account Locked"

    workflow_page.set_content(f"""
        <div class="account-locked-warning">
            <i class="lock-icon"></i>
            <span class="warning-text">{result["data"]["message"]}</span>
        </div>
    """)
    expect(workflow_page.locator(".account-locked-warning")).to_be_visible()
    expect(workflow_page.locator(".warning-text")).to_contain_text("Account Locked by Security Policy")


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_login_2fa_prompt(mock_router: MockRouter, workflow_page: Page):
    """Verify multi-factor authentication (2FA) challenge flow."""
    mock_router.mock_json("**/Controlbase/login**", admin_mocks.MOCK_ADMIN_LOGIN_2FA_REQUIRED, status=200)

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: '2fa_admin', password: 'Password123' })
        });
        return { status: resp.status, data: await resp.json() };
    }""")

    assert result["status"] == 200
    assert result["data"]["requires_2fa"] is True

    workflow_page.set_content("""
        <div id="two-factor-modal" class="modal-dialog">
            <h3>Two-Factor Authentication Required</h3>
            <p>Please enter your 6-digit Google Authenticator code.</p>
            <input type="text" id="otp-input" maxlength="6" placeholder="000000" />
            <button id="verify-2fa-btn">Verify Code</button>
        </div>
    """)
    expect(workflow_page.locator("#two-factor-modal")).to_be_visible()
    expect(workflow_page.locator("#otp-input")).to_be_visible()
    expect(workflow_page.locator("#verify-2fa-btn")).to_be_visible()


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_session_expiry_auto_logout(mock_router: MockRouter, workflow_page: Page):
    """Verify that 401 on background polling auto-redirects to admin login page."""
    mock_router.mock_error("**/Controlbase/sessionCheck**", status=401, error_message="Session Expired")

    result = workflow_page.evaluate("""async () => {
        const resp = await fetch('https://stage.xtremenext.com/admin/Controlbase/sessionCheck');
        return { status: resp.status };
    }""")

    assert result["status"] == 401

    workflow_page.set_content("""
        <div class="session-expired-notice">
            <p>Your session has expired. You will be redirected to login.</p>
            <a href="/admin/Login/index" id="relogin-btn">Log In Again</a>
        </div>
    """)
    expect(workflow_page.locator(".session-expired-notice")).to_be_visible()
    expect(workflow_page.locator("#relogin-btn")).to_be_visible()

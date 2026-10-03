"""
Mock Authentication Data Payloads.
Provides mock JWT tokens, user profiles, session cookies, and login responses.
"""

from typing import Any, Dict

MOCK_LOGIN_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Login successful",
    "token": "mock_jwt_token_header.eyJ1c2VySWQiOiIxMDA5OCIsInJvbGUiOiJ0cmFkZXIifQ.mock_signature",
    "user": {
        "id": "10098",
        "username": "mock_trader_10098",
        "email": "mock_trader@xtremenext.com",
        "first_name": "Mock",
        "last_name": "Trader",
        "role": "client",
        "kyc_status": "approved",
        "account_type": "standard_live",
        "currency": "USD",
        "created_at": "2026-01-01T00:00:00Z",
    },
    "redirect_url": "/dashboard",
}

MOCK_ADMIN_LOGIN_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Admin authorization granted",
    "token": "mock_admin_jwt_token_xyz987",
    "user": {
        "id": "1",
        "username": "madmin",
        "email": "admin@xtremenext.com",
        "role": "super_admin",
        "permissions": ["all"],
    },
    "redirect_url": "/admin/Controlbase/Dashboard",
}

MOCK_LOGIN_INVALID_CREDENTIALS: Dict[str, Any] = {
    "status": 401,
    "success": False,
    "error": "Invalid username or password",
    "message": "Invalid username or password. Please try again.",
    "code": "AUTH_INVALID_CREDENTIALS",
}

MOCK_LOGIN_ACCOUNT_LOCKED: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "Account suspended",
    "message": "Your account has been locked due to security policy violations. Contact support.",
    "code": "AUTH_ACCOUNT_LOCKED",
}

MOCK_2FA_REQUIRED: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "requires_2fa": True,
    "session_ticket": "2fa_session_temp_ticket_12345",
    "message": "Please provide your two-factor authentication code.",
}

# =====================================================================
# Registration & Password Reset Mocks
# =====================================================================
MOCK_REGISTER_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Registration successful. Please check your email to verify your account.",
    "user_id": "10099",
    "email": "newtrader@xtremenext.com",
    "requires_verification": True,
}

MOCK_REGISTER_DUPLICATE_EMAIL: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Duplicate Email",
    "message": "An account with this email address already exists. Please sign in instead.",
    "code": "EMAIL_ALREADY_EXISTS",
}

MOCK_FORGOT_PASSWORD_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Password reset link has been dispatched to your registered email address.",
}

MOCK_FORGOT_PASSWORD_NOT_FOUND: Dict[str, Any] = {
    "status": 404,
    "success": False,
    "error": "User Not Found",
    "message": "No account found matching the provided email address.",
    "code": "USER_NOT_FOUND",
}

MOCK_CREATE_TRADING_ACCOUNT_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "account_number": "30098",
    "type": "Live Standard",
    "server": "XtremeNext-Live",
    "balance": 0.00,
    "currency": "USD",
    "leverage": 500,
    "message": "New trading account 30098 provisioned successfully.",
}

MOCK_CREATE_TRADING_ACCOUNT_LIMIT_EXCEEDED: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Account Limit Reached",
    "message": "Maximum active trading accounts limit (5) reached for standard tier.",
    "code": "MAX_ACCOUNTS_LIMIT",
}


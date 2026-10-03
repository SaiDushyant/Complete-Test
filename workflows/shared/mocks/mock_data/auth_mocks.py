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

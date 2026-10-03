"""
Mock Data Payloads for Admin Portal.
Provides mock user management records, KYC document requests, deposit approvals,
role permission matrices, and symbol configuration datasets.
"""

from typing import Any, Dict, List

MOCK_ADMIN_USER_LIST: List[Dict[str, Any]] = [
    {
        "id": "10098",
        "username": "trader_john",
        "email": "john.trader@example.com",
        "group": "Standard_USD",
        "balance": 15400.00,
        "equity": 15400.00,
        "leverage": 100,
        "status": "active",
        "kyc": "verified",
        "created_at": "2026-02-14",
    },
    {
        "id": "10099",
        "username": "trader_sarah",
        "email": "sarah.trader@example.com",
        "group": "VIP_USD",
        "balance": 85000.00,
        "equity": 89200.50,
        "leverage": 200,
        "status": "active",
        "kyc": "verified",
        "created_at": "2026-03-01",
    },
    {
        "id": "10100",
        "username": "trader_banned",
        "email": "banned.user@example.com",
        "group": "Standard_USD",
        "balance": 0.00,
        "equity": 0.00,
        "leverage": 50,
        "status": "blocked",
        "kyc": "rejected",
        "created_at": "2026-01-10",
    },
]

MOCK_KYC_DOCUMENTS_QUEUE: List[Dict[str, Any]] = [
    {
        "request_id": "KYC-8812",
        "user_id": "10098",
        "user_name": "John Doe",
        "doc_type": "Passport",
        "doc_number": "P88129034",
        "doc_file_url": "/uploads/mock_passport.png",
        "status": "PENDING",
        "submitted_at": "2026-10-02 09:30:00",
    },
    {
        "request_id": "KYC-8813",
        "user_id": "10101",
        "user_name": "Alice Smith",
        "doc_type": "National ID",
        "doc_number": "ID-99210",
        "doc_file_url": "/uploads/mock_id.pdf",
        "status": "PENDING",
        "submitted_at": "2026-10-02 11:15:00",
    },
]

MOCK_PENDING_DEPOSITS: List[Dict[str, Any]] = [
    {
        "transaction_id": "DEP-7731",
        "account_id": "10098",
        "amount": 2500.00,
        "currency": "USD",
        "gateway": "Crypto (USDT-TRC20)",
        "tx_hash": "0x7a89b...3c12",
        "proof_img": "/uploads/proof_7731.jpg",
        "status": "PENDING_APPROVAL",
        "created_at": "2026-10-03 08:00:00",
    }
]

MOCK_ACTION_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Action completed successfully and state synchronized.",
}

MOCK_ACTION_PERMISSION_DENIED: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "Permission Denied",
    "message": "You do not have administrative privileges to perform this operation.",
    "code": "ACCESS_CONTROL_FORBIDDEN",
}

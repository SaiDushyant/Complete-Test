"""
Mock Data Payloads for Client Portal.
Provides mock wallet balance, deposit gateway configurations, withdrawal OTP requests,
internal transfer validations, and copy trading leaderboards.
"""

from typing import Any, Dict, List

MOCK_CLIENT_WALLET_SUMMARY: Dict[str, Any] = {
    "wallet_id": "W-10098",
    "total_balance_usd": 12450.75,
    "trading_accounts_count": 2,
    "kyc_status": "VERIFIED",
    "currency": "USD",
    "accounts": [
        {
            "account_number": "10098",
            "type": "Live Standard",
            "server": "XtremeNext-Live",
            "balance": 10000.00,
            "equity": 10250.00,
            "currency": "USD",
            "leverage": 100,
        },
        {
            "account_number": "20098",
            "type": "Demo Pro",
            "server": "XtremeNext-Demo",
            "balance": 50000.00,
            "equity": 50000.00,
            "currency": "USD",
            "leverage": 500,
        },
    ],
}

MOCK_PAYMENT_GATEWAYS: List[Dict[str, Any]] = [
    {
        "id": "usdt_trc20",
        "name": "USDT (TRC20)",
        "min_deposit": 10.0,
        "max_deposit": 100000.0,
        "fee_pct": 0.0,
        "processing_time": "Instant (1-3 mins)",
        "deposit_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
    },
    {
        "id": "bank_wire",
        "name": "International Bank Wire",
        "min_deposit": 100.0,
        "max_deposit": 500000.0,
        "fee_pct": 0.0,
        "processing_time": "1-3 Business Days",
    },
    {
        "id": "oxapay",
        "name": "OxaPay Crypto",
        "min_deposit": 10.0,
        "max_deposit": 50000.0,
        "fee_pct": 0.0,
        "processing_time": "Instant",
    },
]

MOCK_WITHDRAWAL_SUBMIT_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "request_id": "WDR-9921",
    "message": "Withdrawal request submitted successfully. Pending processing.",
    "amount": 500.00,
    "fee": 0.00,
}

MOCK_INTERNAL_TRANSFER_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "transaction_id": "TRF-3381",
    "message": "Internal transfer executed instantly.",
    "from_account": "10098",
    "to_account": "20098",
    "amount": 250.00,
}

MOCK_LEADERBOARD_MANAGERS: List[Dict[str, Any]] = [
    {
        "manager_id": "M-501",
        "name": "Alpha Trend Trader",
        "roi_all_time": 245.8,
        "drawdown_max": 12.4,
        "followers_count": 84,
        "min_investment": 100.0,
        "performance_fee_pct": 20.0,
    },
    {
        "manager_id": "M-502",
        "name": "Safe Forex Scalper",
        "roi_all_time": 118.2,
        "drawdown_max": 6.1,
        "followers_count": 142,
        "min_investment": 50.0,
        "performance_fee_pct": 15.0,
    },
]

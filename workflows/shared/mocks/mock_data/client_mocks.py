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

MOCK_WITHDRAW_INSUFFICIENT_FUNDS: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Insufficient Funds",
    "message": "Requested withdrawal amount exceeds withdrawable balance after margin reserve.",
    "code": "INSUFFICIENT_FUNDS",
    "withdrawable_balance": 150.00,
}

MOCK_DEPOSIT_MINIMUM_ERROR: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Minimum Deposit Threshold Not Met",
    "message": "Minimum deposit amount for selected gateway is $10.00.",
    "code": "MINIMUM_DEPOSIT_THRESHOLD",
}

MOCK_STRATEGY_SUBSCRIBE_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "subscription_id": "SUB-7712",
    "manager_id": "M-501",
    "trade_method": "Balance Based",
    "status_text": "ACTIVE",
    "message": "Successfully subscribed to strategy Alpha Trend Trader.",
}

MOCK_PAMM_INVESTMENT_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "pool_id": "PAMM-801",
    "invested_amount": 500.00,
    "equity_share_pct": 4.85,
    "status_text": "JOINED",
    "message": "PAMM pool investment confirmed successfully.",
}

MOCK_MAM_ALLOCATION_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "mam_id": "MAM-302",
    "allocation_ratio": 1.5,
    "status_text": "CONNECTED",
    "message": "MAM allocation settings updated successfully.",
}

# =====================================================================
# Extended Mock Payloads for KYC & Multi-Account States
# =====================================================================
MOCK_KYC_STATUS_PENDING: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "kyc_status": "PENDING",
    "submitted_at": "2026-10-02T14:30:00Z",
    "message": "Your verification documents are currently undergoing compliance review.",
    "documents": [
        {"type": "ID_CARD", "status": "PENDING"},
        {"type": "PROOF_OF_ADDRESS", "status": "PENDING"},
    ],
}

MOCK_KYC_STATUS_REJECTED: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "kyc_status": "REJECTED",
    "rejected_at": "2026-10-02T16:00:00Z",
    "rejection_reason": "Utility bill must be issued within the last 90 days with clear name and address.",
    "can_resubmit": True,
}

MOCK_KYC_FILE_SIZE_ERROR: Dict[str, Any] = {
    "status": 413,
    "success": False,
    "error": "Payload Too Large",
    "message": "Uploaded KYC document exceeds the 10MB maximum file size limit.",
    "code": "FILE_SIZE_EXCEEDED",
}

MOCK_CLIENT_ZERO_BALANCE_WALLET: Dict[str, Any] = {
    "wallet_id": "W-10099",
    "total_balance_usd": 0.00,
    "trading_accounts_count": 1,
    "kyc_status": "VERIFIED",
    "currency": "USD",
    "accounts": [
        {
            "account_number": "10099",
            "type": "Live Standard",
            "server": "XtremeNext-Live",
            "balance": 0.00,
            "equity": 0.00,
            "currency": "USD",
            "leverage": 100,
        }
    ],
}

MOCK_CLIENT_MULTI_CURRENCY_WALLET: Dict[str, Any] = {
    "wallet_id": "W-10098",
    "total_balance_usd": 45250.00,
    "trading_accounts_count": 3,
    "kyc_status": "VERIFIED",
    "currency": "USD",
    "accounts": [
        {
            "account_number": "10098",
            "type": "USD Standard",
            "balance": 15000.00,
            "currency": "USD",
        },
        {
            "account_number": "10099",
            "type": "EUR Standard",
            "balance": 12000.00,
            "currency": "EUR",
        },
        {
            "account_number": "10100",
            "type": "USDT Account",
            "balance": 18250.00,
            "currency": "USDT",
        },
    ],
}

# =====================================================================
# Extended Withdrawal & Deposit Edge Cases
# =====================================================================
MOCK_WITHDRAW_INVALID_OTP: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Invalid OTP Code",
    "message": "The one-time verification passcode provided is incorrect or has expired.",
    "code": "INVALID_WITHDRAWAL_OTP",
}

MOCK_WITHDRAW_KYC_UNVERIFIED: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "KYC Verification Required",
    "message": "Withdrawals are restricted until your account identity verification (KYC) is approved.",
    "code": "KYC_REQUIRED_FOR_WITHDRAWAL",
}

MOCK_WITHDRAW_DAILY_LIMIT_EXCEEDED: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Daily Limit Exceeded",
    "message": "Withdrawal amount exceeds your tier daily limit of $50,000.00.",
    "code": "DAILY_LIMIT_EXCEEDED",
}

MOCK_DEPOSIT_MAXIMUM_BOUNDARY_ERROR: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Maximum Deposit Limit Exceeded",
    "message": "Maximum deposit per single transaction is $100,000.00.",
    "code": "MAX_DEPOSIT_EXCEEDED",
}

MOCK_DEPOSIT_CRYPTO_ADDRESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "gateway": "USDT_TRC20",
    "address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
    "qr_code_data": "https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
    "min_deposit": 10.00,
    "network": "TRON (TRC20)",
}

MOCK_DEPOSIT_PROOF_UPLOAD_FAILURE: Dict[str, Any] = {
    "status": 500,
    "success": False,
    "error": "File Storage Error",
    "message": "Unable to upload payment proof to storage server. Please try again.",
}

# =====================================================================
# Extended Internal Transfer Edge Cases
# =====================================================================
MOCK_TRANSFER_SAME_ACCOUNT_ERROR: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Identical Accounts",
    "message": "Source and destination trading accounts cannot be identical.",
    "code": "SAME_ACCOUNT_TRANSFER",
}

MOCK_TRANSFER_ZERO_AMOUNT_ERROR: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Invalid Amount",
    "message": "Transfer amount must be greater than $0.00.",
    "code": "INVALID_TRANSFER_AMOUNT",
}

MOCK_TRANSFER_CONCURRENCY_ERROR: Dict[str, Any] = {
    "status": 409,
    "success": False,
    "error": "Concurrent Transfer Lock",
    "message": "A transfer operation on this account is already in progress.",
    "code": "CONCURRENT_TRANSACTION",
}

# =====================================================================
# Extended Copy Trading & Social States
# =====================================================================
MOCK_COPY_LEADERBOARD_EMPTY: List[Dict[str, Any]] = []

MOCK_UNFOLLOW_MANAGER_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "manager_id": "M-501",
    "status_text": "UNSUBSCRIBED",
    "message": "Successfully unfollowed manager Alpha Trend Trader. Open positions unlinked.",
}

MOCK_COPY_INSUFFICIENT_MARGIN: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Minimum Capital Not Met",
    "message": "Manager Alpha Trend Trader requires a minimum equity of $500.00 to follow.",
    "code": "INSUFFICIENT_STRATEGY_CAPITAL",
}

# =====================================================================
# Refer & Earn / Affiliate Stats
# =====================================================================
MOCK_REFERRAL_STATS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "referral_code": "XTREME-VIP-99",
    "referral_link": "https://xtremenext.com/register?ref=XTREME-VIP-99",
    "total_referred_clients": 18,
    "active_traders": 12,
    "total_commission_usd": 3840.50,
    "tier": "Tier 2 Partner",
    "rebate_per_lot_usd": 4.50,
}

MOCK_REFERRAL_HISTORY_EMPTY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "commissions": [],
    "total_records": 0,
}

# =====================================================================
# Profile, Settings & Security Edge Cases
# =====================================================================
MOCK_PASSWORD_CHANGE_MISMATCH: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Incorrect Password",
    "message": "Current password entered does not match our records.",
    "code": "CURRENT_PASSWORD_MISMATCH",
}

MOCK_2FA_SETUP_QR: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_url": "otpauth://totp/XtremeNext:user10098?secret=JBSWY3DPEHPK3PXP&issuer=XtremeNext",
}

MOCK_BANK_DETAILS_UPDATE_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Payment & bank payout instructions saved successfully.",
    "updated_at": "2026-10-03T15:30:00Z",
}

# =====================================================================
# Dashboard Metric Cards & Cash Flow Mock Payloads
# =====================================================================
MOCK_CLIENT_DASHBOARD_METRICS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_funds": 12450.75,
    "account_balance": 10000.00,
    "available_buffer": 2450.75,
    "active_referrals": 12,
    "currency": "USD",
}

MOCK_CLIENT_DASHBOARD_ZERO_STATE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_funds": 0.00,
    "account_balance": 0.00,
    "available_buffer": 0.00,
    "active_referrals": 0,
    "currency": "USD",
}

MOCK_CLIENT_DASHBOARD_HIGH_NET_WORTH: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_funds": 15000000.00,
    "account_balance": 12500000.00,
    "available_buffer": 2500000.00,
    "active_referrals": 150,
    "currency": "USD",
}

MOCK_CLIENT_CASH_FLOW_DAY: Dict[str, Any] = {
    "period": "day",
    "deposits": 500.00,
    "withdrawals": 0.00,
    "net_flow": 500.00,
    "data_points": [
        {"timestamp": "08:00", "amount": 0.00},
        {"timestamp": "12:00", "amount": 250.00},
        {"timestamp": "16:00", "amount": 500.00},
    ],
}

MOCK_CLIENT_CASH_FLOW_WEEK: Dict[str, Any] = {
    "period": "week",
    "deposits": 3500.00,
    "withdrawals": 1200.00,
    "net_flow": 2300.00,
    "data_points": [
        {"day": "Mon", "net": 500.00},
        {"day": "Tue", "net": 800.00},
        {"day": "Wed", "net": -200.00},
        {"day": "Thu", "net": 1200.00},
        {"day": "Fri", "net": 0.00},
    ],
}

MOCK_CLIENT_CASH_FLOW_MONTH: Dict[str, Any] = {
    "period": "month",
    "deposits": 18500.00,
    "withdrawals": 6200.00,
    "net_flow": 12300.00,
    "data_points": [
        {"week": "W1", "net": 3200.00},
        {"week": "W2", "net": 4100.00},
        {"week": "W3", "net": 2800.00},
        {"week": "W4", "net": 2200.00},
    ],
}

# =====================================================================
# Extended Deposit History & Edge Cases
# =====================================================================
MOCK_DEPOSIT_HISTORY_POPULATED: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 4,
    "records": [
        {
            "id": "DEP-101",
            "date": "2026-10-03 14:15:00",
            "method": "USDT (TRC20)",
            "amount": "$500.00",
            "status": "APPROVED",
            "detail": "TxHash: 7a8b9c...f12",
        },
        {
            "id": "DEP-102",
            "date": "2026-10-02 11:30:00",
            "method": "Bank Transfer",
            "amount": "$2,500.00",
            "status": "PENDING",
            "detail": "Ref: WIRE-8819",
        },
        {
            "id": "DEP-103",
            "date": "2026-10-01 09:45:00",
            "method": "OxaPay Crypto",
            "amount": "$100.00",
            "status": "PROCESSING",
            "detail": "Confirming Block 28491",
        },
        {
            "id": "DEP-104",
            "date": "2026-09-28 16:20:00",
            "method": "Bank Transfer",
            "amount": "$1,000.00",
            "status": "REJECTED",
            "detail": "Name mismatch on receipt",
        },
    ],
}

MOCK_DEPOSIT_HISTORY_EMPTY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 0,
    "records": [],
}

MOCK_DEPOSIT_HISTORY_PAGINATED_50: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5,
    "records": [
        {
            "id": f"DEP-{i}",
            "date": f"2026-09-{i % 28 + 1:02d} 10:00:00",
            "method": "USDT (TRC20)" if i % 2 == 0 else "Bank Transfer",
            "amount": f"${100 * (i + 1)}.00",
            "status": "APPROVED" if i % 3 == 0 else ("PENDING" if i % 3 == 1 else "PROCESSING"),
            "detail": f"Auto-Tx #{i}",
        }
        for i in range(1, 51)
    ],
}

MOCK_DEPOSIT_PROOF_INVALID_FORMAT: Dict[str, Any] = {
    "status": 415,
    "success": False,
    "error": "Unsupported Media Type",
    "message": "Only JPG, PNG, and PDF file formats are supported for payment proof.",
    "code": "INVALID_FILE_FORMAT",
}

MOCK_DEPOSIT_PROOF_FILE_TOO_LARGE: Dict[str, Any] = {
    "status": 413,
    "success": False,
    "error": "Payload Too Large",
    "message": "Payment receipt file size must not exceed 5MB.",
    "code": "FILE_TOO_LARGE",
}

MOCK_DEPOSIT_BANK_WIRE_INSTRUCTIONS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "beneficiary_name": "XtremeNext Global Liquidity Ltd",
    "bank_name": "Barclays Bank International",
    "iban": "GB29BARC20041538192019",
    "swift_bic": "BARCGB22",
    "reference_code": "CLIENT-10098-DEP",
    "instructions": "Please include your unique reference code in the bank transfer notes.",
}

MOCK_DEPOSIT_GATEWAY_MAINTENANCE: Dict[str, Any] = {
    "status": 503,
    "success": False,
    "error": "Gateway Maintenance",
    "message": "OxaPay Crypto payment rail is temporarily undergoing maintenance. Please use USDT TRC20 or Bank Transfer.",
    "code": "GATEWAY_MAINTENANCE",
}

# =====================================================================
# Extended Withdrawal Mock Data
# =====================================================================
MOCK_WITHDRAW_FEE_CALCULATION: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "amount": 1000.00,
    "fee_pct": 1.0,
    "fee_amount": 10.00,
    "net_payout": 990.00,
    "currency": "USD",
}

MOCK_WITHDRAW_HISTORY_EMPTY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 0,
    "records": [],
}

MOCK_WITHDRAW_HISTORY_PAGINATED_50: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 50,
    "records": [
        {
            "id": f"WDR-{i}",
            "date": f"2026-09-{i % 28 + 1:02d} 14:00:00",
            "method": "USDT (TRC20)" if i % 2 == 0 else "Bank Wire",
            "amount": f"${50 * (i + 1)}.00",
            "status": "APPROVED" if i % 3 == 0 else ("PENDING" if i % 3 == 1 else "COMPLETED"),
            "detail": f"Account W-10098 -> Payout #{i}",
        }
        for i in range(1, 51)
    ],
}

MOCK_WITHDRAW_INVALID_BANK_DETAILS: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Invalid Banking Details",
    "message": "The provided SWIFT/BIC or IFSC code format is invalid.",
    "code": "INVALID_BANK_ROUTING",
}

# =====================================================================
# Extended Internal Transfer Mock Data
# =====================================================================
MOCK_TRANSFER_HISTORY_EMPTY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_transfers": 0,
    "transfers": [],
}

MOCK_TRANSFER_HISTORY_PAGINATED_50: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_transfers": 50,
    "transfers": [
        {
            "id": f"TRF-{i}",
            "date": f"2026-09-{i % 28 + 1:02d} 12:00:00",
            "details": f"10098 -> 20098 (Memo: Move #{i})",
            "amount": f"${25 * (i + 1)}.00",
            "status": "SUCCESS",
        }
        for i in range(1, 51)
    ],
}

MOCK_TRANSFER_INSUFFICIENT_SOURCE_BALANCE: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Insufficient Source Balance",
    "message": "Source account 10098 does not have sufficient free margin for this transfer.",
    "code": "INSUFFICIENT_SOURCE_FUNDS",
}

# =====================================================================
# Extended Wallet Mock Data
# =====================================================================
MOCK_WALLET_CONSOLIDATED_FUNDS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "client_wallet": {
        "account_id": "CW-10098",
        "balance": 12450.75,
        "status": "ACTIVE",
    },
    "ib_wallet": {
        "account_id": "IBW-10098",
        "balance": 3840.50,
        "status": "ACTIVE",
    },
    "trading_accounts_balance": 60000.00,
    "total_consolidated_funds": 76291.25,
    "currency": "USD",
}

MOCK_WALLET_TRANSFER_HISTORY_POPULATED: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 3,
    "records": [
        {
            "date": "2026-10-02 10:15:00",
            "movement": "Account -> Wallet",
            "wallet": "Client Wallet",
            "reference": "WTR-1101",
            "amount": "$1,000.00",
            "remarks": "Trading Account 10098",
        },
        {
            "date": "2026-09-30 16:40:00",
            "movement": "Wallet -> Account",
            "wallet": "Client Wallet",
            "reference": "WTR-1102",
            "amount": "$500.00",
            "remarks": "Trading Account 20098",
        },
        {
            "date": "2026-09-25 09:10:00",
            "movement": "IB Rebate -> IB Wallet",
            "wallet": "IB Wallet",
            "reference": "WTR-1103",
            "amount": "$250.00",
            "remarks": "Commission Tier 2 Settlement",
        },
    ],
}

MOCK_WALLET_TRANSFER_HISTORY_EMPTY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_records": 0,
    "records": [],
}

# =====================================================================
# Extended Copy Trading Mock Data
# =====================================================================
MOCK_COPY_MY_SUBSCRIPTIONS_POPULATED: List[Dict[str, Any]] = [
    {
        "account": "Alpha Trend Trader (M-501)",
        "follow_date": "2026-09-15",
        "trade_method": "Balance Based",
        "rank": "#1",
        "status": "ACTIVE",
        "allocated_capital": 5000.00,
        "total_profit": 845.20,
    },
    {
        "account": "Safe Forex Scalper (M-502)",
        "follow_date": "2026-09-20",
        "trade_method": "Equity Based",
        "rank": "#2",
        "status": "ACTIVE",
        "allocated_capital": 2500.00,
        "total_profit": 210.50,
    },
]

MOCK_COPY_STATISTICS_MODAL_METRICS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "manager_id": "M-501",
    "manager_name": "Alpha Trend Trader",
    "net_profit": 42500.00,
    "growth_pct": 245.8,
    "win_rate_pct": 74.2,
    "profit_factor": 2.15,
    "closed_trades": 840,
    "total_lots": 1420.5,
    "max_drawdown_pct": 12.4,
    "managed_funds": 250000.00,
}

# =====================================================================
# Extended MAM & PAMM Mock Data
# =====================================================================
MOCK_MAM_FOLLOWERS_TABLE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "followers": [
        {
            "follower_name": "John Doe Trader",
            "profit_share": "20%",
            "user_id": "USR-10101",
            "mam_id": "MAM-302",
            "allocated_capital": "$10,000.00",
        },
        {
            "follower_name": "Sarah Connor Forex",
            "profit_share": "15%",
            "user_id": "USR-10102",
            "mam_id": "MAM-302",
            "allocated_capital": "$25,000.00",
        },
    ],
}

MOCK_MAM_STATISTICS_MODAL: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "mam_id": "MAM-302",
    "net_profit": 31200.00,
    "growth_pct": 182.5,
    "win_rate_pct": 68.4,
    "profit_factor": 1.95,
    "closed_trades": 510,
    "total_lots": 890.0,
    "drawdown": 8.5,
    "managed_capital": 180000.00,
}

MOCK_PAMM_INVESTORS_TABLE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "investors": [
        {
            "investor_name": "Elite Growth Fund",
            "equity_share": "12.5%",
            "user_id": "INV-201",
            "pool_id": "PAMM-801",
            "invested_amount": "$50,000.00",
        },
        {
            "investor_name": "Crypto Capital LLC",
            "equity_share": "8.0%",
            "user_id": "INV-202",
            "pool_id": "PAMM-801",
            "invested_amount": "$32,000.00",
        },
    ],
}

MOCK_PAMM_STATISTICS_MODAL: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "pool_id": "PAMM-801",
    "total_pool_equity": 400000.00,
    "all_time_roi_pct": 312.4,
    "active_investors_count": 28,
    "closed_trades": 1250,
    "max_drawdown_pct": 9.2,
    "manager_fee_pct": 20.0,
}

MOCK_PAMM_UNINVEST_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "pool_id": "PAMM-801",
    "redeemed_amount": 500.00,
    "status_text": "REDEEMED",
    "message": "Successfully uninvested capital from PAMM pool. Funds returned to wallet.",
}

# =====================================================================
# Extended Refer & Earn Mock Data
# =====================================================================
MOCK_REFERRAL_TREE_HIERARCHY: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "direct_referrals_count": 6,
    "sub_referrals_count": 12,
    "tree": [
        {
            "id": "REF-101",
            "name": "Alex Trader",
            "tier": "Direct Tier 1",
            "commission_generated": 1200.00,
            "children": [
                {"id": "REF-101-1", "name": "Sub-Trader 1", "commission_generated": 450.00},
                {"id": "REF-101-2", "name": "Sub-Trader 2", "commission_generated": 300.00},
            ],
        },
        {
            "id": "REF-102",
            "name": "Maria Forex",
            "tier": "Direct Tier 1",
            "commission_generated": 950.00,
            "children": [],
        },
    ],
}

MOCK_REFERRED_CLIENTS_TABLE_POPULATED: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "total_clients": 3,
    "clients": [
        {
            "client": "David Miller",
            "account": "10045",
            "ref_id": "REF-9901",
            "mobile": "+1 *** *** 4821",
            "balance": "$5,000.00",
            "activity": "Active (14 lots)",
            "ib_earned": "$63.00",
        },
        {
            "client": "Elena Rostova",
            "account": "10046",
            "ref_id": "REF-9902",
            "mobile": "+44 *** *** 8912",
            "balance": "$12,500.00",
            "activity": "Active (38 lots)",
            "ib_earned": "$171.00",
        },
        {
            "client": "Kenji Sato",
            "account": "10047",
            "ref_id": "REF-9903",
            "mobile": "+81 *** *** 1209",
            "balance": "$2,000.00",
            "activity": "Inactive",
            "ib_earned": "$9.00",
        },
    ],
}

# =====================================================================
# Extended Settings & Profile Mock Data
# =====================================================================
MOCK_PERSONAL_INFO_UPDATE_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Personal contact details and address updated successfully.",
    "user": {
        "full_name": "Mock Trader Updated",
        "phone": "+1 555 019 2831",
        "address": "450 Financial District Blvd",
        "city": "New York",
        "state": "NY",
        "zip": "10005",
        "country": "United States",
    },
}

MOCK_PERSONAL_INFO_INVALID_PHONE_EMAIL: Dict[str, Any] = {
    "status": 422,
    "success": False,
    "error": "Validation Error",
    "message": "Provided telephone number or email format is invalid.",
    "code": "INVALID_CONTACT_DATA",
}

MOCK_TRADING_SETTINGS_UPDATE_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "account_number": "10098",
    "leverage": 500,
    "account_type": "Live Pro ECN",
    "message": "Trading account leverage updated to 1:500 successfully.",
}

MOCK_SECURITY_PASSWORD_UPDATE_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "message": "Password changed successfully. New session token generated.",
}

# =====================================================================
# Extended Trading Account Creation Mock Data
# =====================================================================
MOCK_CREATE_TRADING_ACCOUNT_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "account_number": "30098",
    "account_type": "Pro ECN",
    "currency": "USD",
    "leverage": "1:500",
    "balance": 0.00,
    "message": "New MT5 Pro ECN trading account #30098 created successfully.",
}

MOCK_CREATE_TRADING_ACCOUNT_LIMIT_ERROR: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "Account Limit Reached",
    "message": "Maximum number of live trading accounts (5) has been reached for this profile.",
    "code": "MAX_ACCOUNTS_LIMIT_EXCEEDED",
}







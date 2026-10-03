"""
Mock Data Payloads for Admin Portal.
Provides comprehensive mock datasets across all 22 administrative modules:
Auth, Dashboard KPIs, User CRUD, KYC, Account Requests, Groups, Bonuses,
Deposits, Withdrawals, Orders, Risk Management (A/B Book), Symbols, Managers,
RBAC Roles, Copy Trading, PAMM/MAM, Leads CRM, LP Execution, Cron Jobs,
Audit Logs, and Global Platform Settings.
"""

from typing import Any, Dict, List

# ----------------------------------------------------------------------
# 01. ADMIN AUTHENTICATION
# ----------------------------------------------------------------------
MOCK_ADMIN_LOGIN_SUCCESS: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "token": "mock-jwt-admin-session-xyz99210",
    "user": {
        "id": "1",
        "username": "admin_master",
        "email": "master.admin@brokerage.com",
        "role": "SuperAdmin",
        "permissions": ["ALL"],
    },
}

MOCK_ADMIN_LOGIN_2FA_REQUIRED: Dict[str, Any] = {
    "status": 200,
    "success": False,
    "requires_2fa": True,
    "temp_token": "temp-2fa-token-44123",
    "message": "Please enter your 6-digit Google Authenticator code.",
}

MOCK_ADMIN_LOGIN_ACCOUNT_LOCKED: Dict[str, Any] = {
    "status": 403,
    "success": False,
    "error": "Account Locked",
    "message": "Account Locked by Security Policy due to excessive failed attempts.",
}

# ----------------------------------------------------------------------
# 02. DASHBOARD METRICS
# ----------------------------------------------------------------------
MOCK_ADMIN_DASHBOARD_METRICS: Dict[str, Any] = {
    "status": 200,
    "total_traders": 1420,
    "active_traders_24h": 384,
    "total_deposits_usd": 1245800.00,
    "total_withdrawals_usd": 482100.50,
    "open_orders_count": 892,
    "platform_volume_lots": 14520.40,
    "broker_net_pnl_usd": 182400.00,
}

MOCK_ADMIN_DASHBOARD_ZERO_METRICS: Dict[str, Any] = {
    "status": 200,
    "total_traders": 0,
    "active_traders_24h": 0,
    "total_deposits_usd": 0.00,
    "total_withdrawals_usd": 0.00,
    "open_orders_count": 0,
    "platform_volume_lots": 0.00,
    "broker_net_pnl_usd": 0.00,
}

# ----------------------------------------------------------------------
# 03. USER MANAGEMENT & ACTIVE SESSIONS
# ----------------------------------------------------------------------
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

MOCK_ADMIN_ACTIVE_USERS: List[Dict[str, Any]] = [
    {
        "session_id": "sess-8812",
        "user_id": "10098",
        "username": "trader_john",
        "ip_address": "192.168.1.45",
        "device": "Chrome on Windows",
        "logged_in_at": "2026-10-03 14:10:00",
        "status": "ONLINE",
    },
    {
        "session_id": "sess-8813",
        "user_id": "10099",
        "username": "trader_sarah",
        "ip_address": "192.168.1.88",
        "device": "Safari on macOS",
        "logged_in_at": "2026-10-03 15:00:22",
        "status": "ONLINE",
    },
]

# ----------------------------------------------------------------------
# 04. KYC & DOCUMENTS
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# 05. ACCOUNT REQUESTS
# ----------------------------------------------------------------------
MOCK_ADMIN_ACCOUNT_REQUESTS: List[Dict[str, Any]] = [
    {
        "request_id": "REQ-101",
        "user_id": "10098",
        "user_name": "John Doe",
        "account_type": "LIVE_ECN",
        "currency": "USD",
        "leverage": 200,
        "status": "PENDING",
        "requested_at": "2026-10-03 10:00:00",
    },
    {
        "request_id": "REQ-102",
        "user_id": "10105",
        "user_name": "Bob Martin",
        "account_type": "DEMO_STANDARD",
        "currency": "USD",
        "leverage": 100,
        "status": "PENDING",
        "requested_at": "2026-10-03 11:30:00",
    },
]

# ----------------------------------------------------------------------
# 06. USER GROUPS
# ----------------------------------------------------------------------
MOCK_ADMIN_USER_GROUPS: List[Dict[str, Any]] = [
    {
        "group_id": "Standard_USD",
        "name": "Standard USD",
        "currency": "USD",
        "default_leverage": 100,
        "spread_markup_pips": 1.2,
        "commission_per_lot": 0.0,
        "active_users_count": 842,
    },
    {
        "group_id": "VIP_USD",
        "name": "VIP Raw Spread",
        "currency": "USD",
        "default_leverage": 200,
        "spread_markup_pips": 0.1,
        "commission_per_lot": 5.0,
        "active_users_count": 128,
    },
]

# ----------------------------------------------------------------------
# 07. USER BONUSES (CREDIT LIST)
# ----------------------------------------------------------------------
MOCK_ADMIN_USER_BONUSES: List[Dict[str, Any]] = [
    {
        "bonus_id": "BONUS-4401",
        "user_id": "10098",
        "bonus_type": "Deposit Match 50%",
        "amount": 500.00,
        "currency": "USD",
        "required_volume_lots": 25.0,
        "completed_volume_lots": 14.5,
        "status": "ACTIVE",
        "granted_at": "2026-09-15",
    },
    {
        "bonus_id": "BONUS-4402",
        "user_id": "10099",
        "bonus_type": "Welcome Bonus",
        "amount": 100.00,
        "currency": "USD",
        "required_volume_lots": 5.0,
        "completed_volume_lots": 5.0,
        "status": "COMPLETED",
        "granted_at": "2026-09-01",
    },
]

# ----------------------------------------------------------------------
# 08. DEPOSITS & GATEWAYS
# ----------------------------------------------------------------------
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

MOCK_ADMIN_PAYMENT_LIST: List[Dict[str, Any]] = [
    {
        "payment_id": "PAY-9921",
        "user_id": "10098",
        "amount": 1000.00,
        "gateway": "Stripe Credit Card",
        "status": "COMPLETED",
        "created_at": "2026-10-01 12:00:00",
    },
    {
        "payment_id": "PAY-9922",
        "user_id": "10099",
        "amount": 5000.00,
        "gateway": "Bank Wire Transfer",
        "status": "COMPLETED",
        "created_at": "2026-10-02 14:30:00",
    },
]

MOCK_ADMIN_OXAPAY_LIST: List[Dict[str, Any]] = [
    {
        "track_id": "OXA-5510",
        "order_id": "DEP-7731",
        "crypto_currency": "USDT",
        "network": "TRON (TRC20)",
        "amount": 2500.00,
        "confirmations": 18,
        "tx_hash": "0x7a89b8821fa99c01",
        "status": "CONFIRMED",
    }
]

# ----------------------------------------------------------------------
# 09. WITHDRAWALS
# ----------------------------------------------------------------------
MOCK_ADMIN_WITHDRAW_QUEUE: List[Dict[str, Any]] = [
    {
        "withdrawal_id": "WTH-3310",
        "account_id": "10098",
        "amount": 1200.00,
        "currency": "USD",
        "payout_method": "USDT (TRC-20)",
        "payout_address": "TQ8x7bJb91mYkLmPo821sP...",
        "status": "PENDING",
        "created_at": "2026-10-03 09:15:00",
    },
    {
        "withdrawal_id": "WTH-3311",
        "account_id": "10099",
        "amount": 8500.00,
        "currency": "USD",
        "payout_method": "Bank Wire (SWIFT)",
        "payout_address": "IBAN: GB29XTRM9912001",
        "status": "PENDING",
        "created_at": "2026-10-03 10:45:00",
    },
]

# ----------------------------------------------------------------------
# 10. ORDERS & TRADE MANAGEMENT
# ----------------------------------------------------------------------
MOCK_ADMIN_OPEN_ORDERS: List[Dict[str, Any]] = [
    {
        "ticket": 9001,
        "account_id": "10098",
        "symbol": "EURUSD",
        "type": "BUY",
        "lots": 1.50,
        "open_price": 1.08500,
        "current_price": 1.08620,
        "sl": 1.08100,
        "tp": 1.09200,
        "profit": 180.00,
        "open_time": "2026-10-03 12:30:00",
    },
    {
        "ticket": 9002,
        "account_id": "10099",
        "symbol": "BTCUSD",
        "type": "SELL",
        "lots": 0.50,
        "open_price": 64500.00,
        "current_price": 64150.00,
        "sl": 65500.00,
        "tp": 63000.00,
        "profit": 175.00,
        "open_time": "2026-10-03 13:15:00",
    },
]

MOCK_ADMIN_CLOSED_ORDERS: List[Dict[str, Any]] = [
    {
        "ticket": 8980,
        "account_id": "10098",
        "symbol": "XAUUSD",
        "type": "BUY",
        "lots": 2.00,
        "open_price": 2650.00,
        "close_price": 2665.50,
        "profit": 3100.00,
        "close_time": "2026-10-02 18:00:00",
    }
]

MOCK_ADMIN_ORDER_REPORT: Dict[str, Any] = {
    "total_orders": 342,
    "total_volume_lots": 584.20,
    "gross_profit_usd": 42100.00,
    "gross_loss_usd": -28500.00,
    "net_broker_spread_usd": 13600.00,
}

MOCK_ADMIN_ORDER_EDIT_LOG: List[Dict[str, Any]] = [
    {
        "log_id": "LOG-101",
        "ticket": 9001,
        "modified_field": "STOP_LOSS",
        "old_value": "1.08000",
        "new_value": "1.08100",
        "admin_user": "admin_master",
        "timestamp": "2026-10-03 13:00:00",
    }
]

# ----------------------------------------------------------------------
# 11. RISK MANAGEMENT - A-BOOK & B-BOOK
# ----------------------------------------------------------------------
MOCK_ADMIN_A_BOOK_ORDERS: List[Dict[str, Any]] = [
    {
        "ticket": 9001,
        "lp_name": "LMAX Global",
        "lp_ticket": "LP-881204",
        "symbol": "EURUSD",
        "lots": 1.50,
        "client_fill_price": 1.08500,
        "lp_fill_price": 1.08498,
        "bridge_latency_ms": 14,
        "status": "ROUTED_FILLED",
    }
]

MOCK_ADMIN_B_BOOK_EXPOSURE: Dict[str, Any] = {
    "total_internal_lots": 128.5,
    "net_eurusd_exposure": -42.0,
    "net_btcusd_exposure": 18.5,
    "net_xauusd_exposure": -15.0,
    "unhedged_risk_usd": 48200.00,
}

MOCK_ADMIN_USER_MARGIN: List[Dict[str, Any]] = [
    {
        "account_id": "10098",
        "balance": 15400.00,
        "equity": 15580.00,
        "used_margin": 1627.50,
        "free_margin": 13952.50,
        "margin_level_pct": 957.3,
        "status": "NORMAL",
    }
]

MOCK_ADMIN_BOOK_REPORT: Dict[str, Any] = {
    "a_book_volume_lots": 820.5,
    "b_book_volume_lots": 1450.0,
    "a_book_commission_earned": 4102.50,
    "b_book_realized_pnl": 18450.00,
}

# ----------------------------------------------------------------------
# 12. SYMBOLS & FEEDS
# ----------------------------------------------------------------------
MOCK_ADMIN_SYMBOLS_LIST: List[Dict[str, Any]] = [
    {"symbol": "EURUSD", "category": "Forex Major", "digits": 5, "spread_type": "Floating", "status": "ACTIVE"},
    {"symbol": "XAUUSD", "category": "Commodities", "digits": 2, "spread_type": "Floating", "status": "ACTIVE"},
    {"symbol": "BTCUSD", "category": "Crypto", "digits": 2, "spread_type": "Floating", "status": "ACTIVE"},
]

MOCK_ADMIN_SYMBOL_CONFIG: Dict[str, Any] = {
    "symbol": "EURUSD",
    "contract_size": 100000,
    "digits": 5,
    "pip_value": 10.0,
    "long_swap": -6.4,
    "short_swap": 1.2,
    "trade_mode": "FULL_ACCESS",
    "leverage_multiplier": 1.0,
}

# ----------------------------------------------------------------------
# 13. MANAGERS & SUB-ADMINS
# ----------------------------------------------------------------------
MOCK_ADMIN_MANAGERS_LIST: List[Dict[str, Any]] = [
    {
        "id": "MGR-01",
        "name": "Sarah Connor",
        "email": "sarah.mgr@brokerage.com",
        "department": "Dealing Desk",
        "assigned_clients": 145,
        "status": "ACTIVE",
    },
    {
        "id": "MGR-02",
        "name": "David Miller",
        "email": "david.mgr@brokerage.com",
        "department": "Compliance & KYC",
        "assigned_clients": 320,
        "status": "ACTIVE",
    },
]

# ----------------------------------------------------------------------
# 14. ROLES & PERMISSIONS
# ----------------------------------------------------------------------
MOCK_ADMIN_ROLES_LIST: List[Dict[str, Any]] = [
    {"role_id": "SUPER_ADMIN", "role_name": "Super Administrator", "users_count": 2, "is_system": True},
    {"role_id": "DEALING_DESK", "role_name": "Dealing Desk Manager", "users_count": 4, "is_system": False},
    {"role_id": "COMPLIANCE", "role_name": "Compliance & KYC Officer", "users_count": 3, "is_system": False},
]

# ----------------------------------------------------------------------
# 15. COPY TRADING
# ----------------------------------------------------------------------
MOCK_ADMIN_COPY_PROVIDERS: List[Dict[str, Any]] = [
    {
        "provider_id": "CP-101",
        "strategy_name": "Alpha Trend Rider",
        "master_trader": "trader_sarah",
        "copiers_count": 218,
        "roi_pct": 142.5,
        "drawdown_pct": 8.4,
        "status": "ACTIVE",
    }
]

MOCK_ADMIN_PRIVATE_COPIERS: List[Dict[str, Any]] = [
    {
        "rule_id": "PVT-501",
        "strategy_name": "VIP Private Hedge",
        "master_account": "10099",
        "whitelisted_accounts": ["10098", "10101"],
        "status": "ACTIVE",
    }
]

# ----------------------------------------------------------------------
# 16. PAMM / MAM
# ----------------------------------------------------------------------
MOCK_ADMIN_PAMM_POOLS: List[Dict[str, Any]] = [
    {
        "pool_id": "PAMM-801",
        "pool_name": "Apex Institutional Growth",
        "master_account": "10099",
        "total_equity_usd": 450000.00,
        "investors_count": 34,
        "manager_fee_pct": 20.0,
        "status": "OPEN",
    }
]

MOCK_ADMIN_MAM_CONFIG: Dict[str, Any] = {
    "mam_id": "MAM-201",
    "master_account": "10099",
    "allocation_method": "EQUITY_RATIO",
    "sub_accounts_count": 12,
    "total_allocated_lots": 45.0,
}

# ----------------------------------------------------------------------
# 17. LEADS CRM
# ----------------------------------------------------------------------
MOCK_ADMIN_LEADS_LIST: List[Dict[str, Any]] = [
    {
        "lead_id": "LD-9901",
        "full_name": "Michael Chang",
        "email": "michael.chang@sample.com",
        "country": "Singapore",
        "status": "NEW",
        "assigned_agent": "Unassigned",
        "created_at": "2026-10-03 14:00:00",
    }
]

MOCK_ADMIN_LEADS_REPORT: Dict[str, Any] = {
    "total_leads": 1200,
    "contacted_leads": 840,
    "registered_traders": 320,
    "funded_accounts": 180,
    "overall_conversion_pct": 15.0,
}

# ----------------------------------------------------------------------
# 18. LIQUIDITY PROVIDER CONFIG & LOGS
# ----------------------------------------------------------------------
MOCK_ADMIN_LP_CONFIG: List[Dict[str, Any]] = [
    {
        "lp_id": "LP-LMAX",
        "name": "LMAX Global Liquidity",
        "status": "CONNECTED",
        "ping_latency_ms": 12,
        "primary_routed_symbols": ["EURUSD", "GBPUSD", "USDJPY"],
    },
    {
        "lp_id": "LP-ISPRIME",
        "name": "IS Prime FX",
        "status": "CONNECTED",
        "ping_latency_ms": 16,
        "primary_routed_symbols": ["XAUUSD", "XAGUSD"],
    },
]

MOCK_ADMIN_LP_BALANCE_TX: List[Dict[str, Any]] = [
    {
        "tx_id": "LPTX-801",
        "lp_id": "LP-LMAX",
        "tx_type": "DEPOSIT",
        "amount": 250000.00,
        "balance_after": 1250000.00,
        "timestamp": "2026-10-01 09:00:00",
    }
]

MOCK_ADMIN_LP_COMMISSIONS: List[Dict[str, Any]] = [
    {
        "log_id": "COMM-401",
        "lp_id": "LP-LMAX",
        "traded_ticket": 9001,
        "volume_lots": 1.5,
        "rate_per_lot": 2.50,
        "total_fee_usd": 3.75,
        "timestamp": "2026-10-03 12:30:00",
    }
]

# ----------------------------------------------------------------------
# 19. CRON JOBS
# ----------------------------------------------------------------------
MOCK_ADMIN_CRON_JOBS: List[Dict[str, Any]] = [
    {
        "job_id": "CRON-SWAP",
        "job_name": "Daily Swap Calculation",
        "schedule": "0 0 * * *",
        "last_run": "2026-10-03 00:00:00",
        "next_run": "2026-10-04 00:00:00",
        "status": "ACTIVE",
    },
    {
        "job_id": "CRON-CLEANUP",
        "job_name": "Purge Expired Sessions",
        "schedule": "*/30 * * * *",
        "last_run": "2026-10-03 15:30:00",
        "next_run": "2026-10-03 16:00:00",
        "status": "ACTIVE",
    },
]

# ----------------------------------------------------------------------
# 20. AUDIT LOGS & REFERRAL REPORTS
# ----------------------------------------------------------------------
MOCK_ADMIN_TRANSACTION_LOGS: List[Dict[str, Any]] = [
    {
        "log_id": "AUDIT-9921",
        "actor": "admin_master",
        "action": "CREDIT_BALANCE",
        "target_user": "10098",
        "amount": 500.00,
        "ip": "10.0.0.1",
        "timestamp": "2026-10-03 14:20:00",
    }
]

MOCK_ADMIN_REFER_REPORT: List[Dict[str, Any]] = [
    {
        "ib_id": "IB-881",
        "ib_name": "Global FX Affiliates",
        "tier": "Master IB (Tier 1)",
        "sub_traders_count": 84,
        "traded_lots_month": 412.5,
        "commission_earned_usd": 2062.50,
        "payout_status": "PAID",
    }
]

# ----------------------------------------------------------------------
# 21. GLOBAL PLATFORM SETTINGS
# ----------------------------------------------------------------------
MOCK_ADMIN_GLOBAL_SETTINGS: Dict[str, Any] = {
    "broker_brand_name": "XtremeNext Prime",
    "default_leverage": 100,
    "max_allowed_leverage": 500,
    "maintenance_mode": False,
    "allow_new_registrations": True,
    "support_email": "support@xtremenext.com",
}

# ----------------------------------------------------------------------
# GENERIC SUCCESS & ERROR RESPONSES
# ----------------------------------------------------------------------
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

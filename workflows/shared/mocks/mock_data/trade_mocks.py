"""
Comprehensive Mock Data Payloads for Trade Terminal.
Provides mock ticker quotes, order books, positions, order execution responses,
account balances, multi-account switcher data, trade history, dashboard analytics, charts, profile, settings, support, and API keys.
"""

from typing import Any, Dict, List

MOCK_WATCHLIST_SYMBOLS: List[Dict[str, Any]] = [
    {
        "symbol": "EURUSD",
        "description": "Euro vs US Dollar",
        "bid": 1.08502,
        "ask": 1.08514,
        "spread": 1.2,
        "digits": 5,
        "change_pct": 0.35,
        "high": 1.08920,
        "low": 1.08210,
    },
    {
        "symbol": "GBPUSD",
        "description": "Great British Pound vs US Dollar",
        "bid": 1.29410,
        "ask": 1.29426,
        "spread": 1.6,
        "digits": 5,
        "change_pct": -0.12,
        "high": 1.29800,
        "low": 1.29150,
    },
    {
        "symbol": "BTCUSD",
        "description": "Bitcoin vs US Dollar",
        "bid": 64250.00,
        "ask": 64255.00,
        "spread": 5.0,
        "digits": 2,
        "change_pct": 2.45,
        "high": 65100.00,
        "low": 63800.00,
    },
    {
        "symbol": "XAUUSD",
        "description": "Gold vs US Dollar",
        "bid": 2650.40,
        "ask": 2650.75,
        "spread": 0.35,
        "digits": 2,
        "change_pct": 0.88,
        "high": 2662.00,
        "low": 2640.10,
    },
]

MOCK_WORKSPACE_2_SYMBOLS: List[Dict[str, Any]] = [
    {
        "symbol": "USDJPY",
        "description": "US Dollar vs Japanese Yen",
        "bid": 148.50,
        "ask": 148.52,
        "spread": 2.0,
        "digits": 3,
        "change_pct": 0.15,
        "high": 149.10,
        "low": 147.90,
    },
    {
        "symbol": "AUDUSD",
        "description": "Australian Dollar vs US Dollar",
        "bid": 0.6720,
        "ask": 0.6722,
        "spread": 2.0,
        "digits": 4,
        "change_pct": -0.40,
        "high": 0.6760,
        "low": 0.6705,
    },
]

MOCK_ACCOUNT_METRICS: Dict[str, Any] = {
    "account_id": "10098",
    "currency": "USD",
    "leverage": 100,
    "balance": 25000.00,
    "credit": 0.00,
    "floating_pnl": 450.50,
    "equity": 25450.50,
    "used_margin": 1085.14,
    "free_margin": 24365.36,
    "margin_level_pct": 2345.36,
}

MOCK_ZERO_BALANCE_METRICS: Dict[str, Any] = {
    "account_id": "10098",
    "currency": "USD",
    "leverage": 100,
    "balance": 0.00,
    "credit": 0.00,
    "floating_pnl": 0.00,
    "equity": 0.00,
    "used_margin": 0.00,
    "free_margin": 0.00,
    "margin_level_pct": 0.00,
}

MOCK_MARGIN_CALL_METRICS: Dict[str, Any] = {
    "account_id": "10098",
    "currency": "USD",
    "leverage": 100,
    "balance": 2000.00,
    "credit": 0.00,
    "floating_pnl": -1100.00,
    "equity": 900.00,
    "used_margin": 2000.00,
    "free_margin": -1100.00,
    "margin_level_pct": 45.00,
}

MOCK_USER_ACCOUNTS_LIST: List[Dict[str, Any]] = [
    {
        "account_id": "10098",
        "account_type": "LIVE",
        "account_group": "VIP-RAW",
        "currency": "USD",
        "balance": 25000.00,
        "leverage": 100,
        "is_active": True,
        "server": "XtremeNext-Live-01",
    },
    {
        "account_id": "10099",
        "account_type": "DEMO",
        "account_group": "STANDARD-DEMO",
        "currency": "USD",
        "balance": 10000.00,
        "leverage": 200,
        "is_active": False,
        "server": "XtremeNext-Demo-01",
    },
    {
        "account_id": "10100",
        "account_type": "LIVE",
        "account_group": "ECN-ZERO",
        "currency": "EUR",
        "balance": 5000.00,
        "leverage": 50,
        "is_active": False,
        "server": "XtremeNext-Live-02",
    },
]

MOCK_OPEN_POSITIONS: List[Dict[str, Any]] = [
    {
        "ticket": 9081234,
        "symbol": "EURUSD",
        "type": "BUY",
        "volume": 1.00,
        "open_price": 1.08450,
        "current_price": 1.08502,
        "sl": 1.08000,
        "tp": 1.09000,
        "swap": -1.20,
        "pnl": 52.00,
        "open_time": "2026-10-01 10:15:22",
    },
    {
        "ticket": 9081235,
        "symbol": "XAUUSD",
        "type": "SELL",
        "volume": 0.50,
        "open_price": 2655.00,
        "current_price": 2650.40,
        "sl": 2665.00,
        "tp": 2635.00,
        "swap": 0.00,
        "pnl": 230.00,
        "open_time": "2026-10-01 11:30:00",
    },
    {
        "ticket": 9081236,
        "symbol": "BTCUSD",
        "type": "BUY",
        "volume": 0.10,
        "open_price": 64000.00,
        "current_price": 63800.00,
        "sl": 62000.00,
        "tp": 67000.00,
        "swap": -5.00,
        "pnl": -20.00,
        "open_time": "2026-10-01 12:00:00",
    },
]

MOCK_PENDING_ORDERS: List[Dict[str, Any]] = [
    {
        "ticket": 9081240,
        "symbol": "EURUSD",
        "type": "BUY_LIMIT",
        "volume": 0.50,
        "trigger_price": 1.08200,
        "sl": 1.07800,
        "tp": 1.09200,
        "placed_time": "2026-10-02 08:30:00",
        "status": "PENDING",
    },
    {
        "ticket": 9081241,
        "symbol": "XAUUSD",
        "type": "SELL_STOP",
        "volume": 0.20,
        "trigger_price": 2640.00,
        "sl": 2655.00,
        "tp": 2610.00,
        "placed_time": "2026-10-02 09:15:00",
        "status": "PENDING",
    },
]

MOCK_ORDER_SUCCESS_RESPONSE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "order_id": 9081236,
    "message": "Order placed successfully",
    "details": {
        "ticket": 9081236,
        "symbol": "EURUSD",
        "type": "BUY",
        "volume": 0.10,
        "execution_price": 1.08514,
        "status": "OPEN",
    },
}

MOCK_SELL_ORDER_SUCCESS_RESPONSE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "order_id": 9081237,
    "message": "Sell order placed successfully",
    "details": {
        "ticket": 9081237,
        "symbol": "XAUUSD",
        "type": "SELL",
        "volume": 0.20,
        "execution_price": 2650.40,
        "status": "OPEN",
    },
}

MOCK_LIMIT_ORDER_SUCCESS_RESPONSE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "order_id": 9081238,
    "message": "Limit order placed successfully",
    "details": {
        "ticket": 9081238,
        "symbol": "EURUSD",
        "type": "BUY_LIMIT",
        "volume": 0.05,
        "trigger_price": 1.08200,
        "status": "PENDING",
    },
}

MOCK_STOP_HFT_ORDER_SUCCESS_RESPONSE: Dict[str, Any] = {
    "status": 200,
    "success": True,
    "order_id": 9081239,
    "message": "Stop HFT order placed successfully",
    "details": {
        "ticket": 9081239,
        "symbol": "EURUSD",
        "type": "STOP_HFT",
        "buy_above": 1.09000,
        "sell_below": 1.08000,
        "status": "ACTIVE",
    },
}

MOCK_ORDER_REJECTED_MARGIN: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Not enough money / insufficient margin",
    "message": "Order rejected: Required margin exceeds available free margin.",
    "code": "INSUFFICIENT_MARGIN",
}

MOCK_MARKET_CLOSED_RESPONSE: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Market is closed",
    "message": "Trading for symbol EURUSD is currently halted or outside market trading hours.",
    "code": "MARKET_CLOSED",
}

MOCK_ORDER_SLIPPAGE_ERROR: Dict[str, Any] = {
    "status": 400,
    "success": False,
    "error": "Off quotes / Price changed",
    "message": "Market moved beyond acceptable slippage tolerance. Please retry.",
    "code": "SLIPPAGE_EXCEEDED",
}

MOCK_TRADE_HISTORY_RECORDS: List[Dict[str, Any]] = [
    {
        "id": "9081100",
        "data_id": "9081100",
        "time": "2026-10-01 09:00:15",
        "symbol": "EURUSD",
        "order": "BUY",
        "lot": 1.00,
        "status": "CLOSED",
        "type": "MARKET",
        "sl": 1.08000,
        "tp": 1.09000,
        "entry": 1.08450,
        "exit": 1.08850,
        "commission": -3.50,
        "pnl": 400.00,
        "swap": 0.00,
        "close_time": "2026-10-01 12:30:00",
    },
    {
        "id": "9081101",
        "data_id": "9081101",
        "time": "2026-10-01 14:10:00",
        "symbol": "XAUUSD",
        "order": "SELL",
        "lot": 0.50,
        "status": "CLOSED",
        "type": "MARKET",
        "sl": 2660.00,
        "tp": 2630.00,
        "entry": 2650.00,
        "exit": 2640.00,
        "commission": -5.00,
        "pnl": 500.00,
        "swap": -2.10,
        "close_time": "2026-10-01 16:45:00",
    },
    {
        "id": "9081102",
        "data_id": "9081102",
        "time": "2026-10-02 08:00:00",
        "symbol": "BTCUSD",
        "order": "BUY",
        "lot": 0.10,
        "status": "CLOSED",
        "type": "LIMIT",
        "sl": 63000.00,
        "tp": 66000.00,
        "entry": 63500.00,
        "exit": 64800.00,
        "commission": -10.00,
        "pnl": 130.00,
        "swap": 0.00,
        "close_time": "2026-10-02 11:20:00",
    },
]

MOCK_TRADE_HISTORY_STATS: Dict[str, float] = {
    "balance": 25000.00,
    "deposit": 10000.00,
    "withdraw": 2000.00,
    "commission": -18.50,
    "swap": -2.10,
    "profit": 1030.00,
}

MOCK_DASHBOARD_OVERVIEW: Dict[str, Any] = {
    "account_status": "Verified",
    "account_token": "sec_tok_991823a",
    "balance": 25000.00,
    "free_margin": 24365.36,
    "currency": "USD",
}

MOCK_DASHBOARD_PNL_SERIES: Dict[str, Any] = {
    "daily": {"title": "Daily P/L", "data": [120, -40, 250, 180, -30, 310]},
    "weekly": {"title": "Weekly P/L", "data": [850, 1200, -300, 1450]},
    "monthly": {"title": "Monthly P/L", "data": [3200, 4100, 2900, 5300]},
}

MOCK_DASHBOARD_MOST_TRADED: List[Dict[str, Any]] = [
    {"symbol": "EURUSD", "count": 45, "percentage": 50.0},
    {"symbol": "XAUUSD", "count": 27, "percentage": 30.0},
    {"symbol": "BTCUSD", "count": 18, "percentage": 20.0},
]

MOCK_DASHBOARD_PERFORMANCE_STATS: Dict[str, str] = {
    "avg_win": "$125.50",
    "avg_loss": "-$42.10",
    "profit_factor": "2.98",
    "best_trade": "$500.00",
    "win_ratio": "75%",
    "risk_reward": "1:2.5",
    "max_drawdown": "4.2%",
    "closed_trades": "42",
}

MOCK_CHART_CANDLES_EURUSD: List[Dict[str, Any]] = [
    {"time": 1700000000, "open": 1.0840, "high": 1.0860, "low": 1.0835, "close": 1.0850, "volume": 1250},
    {"time": 1700003600, "open": 1.0850, "high": 1.0875, "low": 1.0845, "close": 1.0870, "volume": 1820},
    {"time": 1700007200, "open": 1.0870, "high": 1.0890, "low": 1.0865, "close": 1.0885, "volume": 2100},
    {"time": 1700010800, "open": 1.0885, "high": 1.0895, "low": 1.0855, "close": 1.0860, "volume": 1540},
]

MOCK_PROFILE_DATA: Dict[str, Any] = {
    "user_id": "usr_9918",
    "name": "Alex Trader",
    "email": "trader.alex@example.com",
    "account_group": "VIP-PRO-RAW",
    "leverage": 100,
    "country": "United Kingdom",
    "kyc_status": "VERIFIED",
}

MOCK_USER_SETTINGS: Dict[str, Any] = {
    "theme": "dark",
    "sound_alerts": True,
    "one_click_trading": True,
    "default_lot": 0.10,
    "chart_type": "candlestick",
}

MOCK_SUPPORT_TICKET_SUCCESS: Dict[str, Any] = {
    "status": 201,
    "success": True,
    "ticket_id": "SUP-9921",
    "message": "Support ticket submitted successfully. Our desk will respond shortly.",
}

MOCK_API_KEYS_LIST: List[Dict[str, Any]] = [
    {
        "id": "key_001",
        "name": "Production Algo Bot",
        "created_at": "2026-09-15",
        "permissions": ["READ", "TRADE"],
        "status": "ACTIVE",
        "masked_key": "ag_live_********************49f2",
    },
    {
        "id": "key_002",
        "name": "Analytics Reporter",
        "created_at": "2026-09-20",
        "permissions": ["READ"],
        "status": "ACTIVE",
        "masked_key": "ag_live_********************11b7",
    },
]

MOCK_API_KEY_CREATED: Dict[str, Any] = {
    "status": 201,
    "success": True,
    "message": "API key generated successfully",
    "key_id": "key_003",
    "name": "Trading Bot Delta",
    "secret_key": "ag_live_sec_7781a9bc901e44f89d31",
}

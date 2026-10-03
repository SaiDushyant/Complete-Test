"""
Mock Data Payloads for Trade Terminal.
Provides mock ticker quotes, order books, positions, order execution responses,
account balances, and trade history.
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

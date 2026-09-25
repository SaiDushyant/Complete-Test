"""
Trade Terminal Test Data Definitions.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class OrderData:
    symbol: str
    order_type: str  # MARKET, LIMIT, STOP
    side: str        # BUY, SELL
    volume: float
    price: float = 0.0


# Standard test instruments
DEFAULT_TRADE_SYMBOL = "EURUSD"
SUPPORTED_TRADE_SYMBOLS: List[str] = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

# Example test orders
SAMPLE_MARKET_BUY_ORDER = OrderData(
    symbol="EURUSD",
    order_type="MARKET",
    side="BUY",
    volume=0.01,
)

SAMPLE_MARKET_SELL_ORDER = OrderData(
    symbol="GBPUSD",
    order_type="MARKET",
    side="SELL",
    volume=0.01,
)

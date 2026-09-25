"""
Shared Test Data Utilities and Generators.
Generates randomized, collision-resistant test data for workflow tests.
"""

import random
import string
import time
from typing import Dict, Any


def generate_unique_email(prefix: str = "testuser") -> str:
    """Generate a unique test email address."""
    timestamp = int(time.time())
    rand_chars = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{timestamp}_{rand_chars}@example.com"


def generate_unique_name(prefix: str = "User") -> str:
    """Generate a unique full name or identifier."""
    rand_suffix = "".join(random.choices(string.digits, k=5))
    return f"{prefix}_{rand_suffix}"


def generate_random_symbol() -> str:
    """Return a representative financial instrument symbol."""
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD", "AAPL", "GOOGL"]
    return random.choice(symbols)


# Common sample data constants
COMMON_TEST_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
COMMON_ORDER_TYPES = ["MARKET", "LIMIT", "STOP"]

"""
Client Portal Helper Utilities.
Maintained by Developer 3 (Client Portal Owner).
"""

import re
from typing import Optional


def format_currency_amount(amount: float, currency: str = "USD") -> str:
    """Format numerical monetary value into standardized display string."""
    return f"${amount:,.2f}" if currency == "USD" else f"{amount:,.2f} {currency}"


def clean_phone_number(phone: str) -> str:
    """Remove spaces, dashes, and parentheses from phone number."""
    return re.sub(r"[\s\-\(\)]", "", phone)

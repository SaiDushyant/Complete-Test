"""
Trade Terminal Helper Utilities.
Maintained by Developer 1 (Trade Terminal Owner).
"""

from typing import Union


def format_lot_size(volume: Union[float, int]) -> str:
    """Format volume into standard two-decimal lot representation."""
    return f"{float(volume):.2f}"


def format_price(price: Union[float, int], precision: int = 5) -> str:
    """Format instrument price according to pip/tick precision."""
    return f"{float(price):.{precision}f}"

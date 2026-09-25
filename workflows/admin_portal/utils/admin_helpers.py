"""
Admin Portal Helper Utilities.
Maintained by Developer 2 (Admin Portal Owner).
"""

from typing import Dict, Any


def format_admin_search_query(term: str) -> str:
    """Format sanitized search query for admin tables."""
    return term.strip()


def parse_admin_metric_value(text: str) -> int:
    """Parse integer counter from metric widgets (e.g. 'Users (42)' -> 42)."""
    import re
    numbers = re.findall(r"\d+", text)
    return int(numbers[0]) if numbers else 0

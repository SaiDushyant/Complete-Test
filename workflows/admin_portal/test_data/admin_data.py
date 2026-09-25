"""
Admin Portal Test Data Definitions.
Maintained by Developer 2 (Admin Portal Owner).
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AdminFilterCriteria:
    role: str
    status: str
    search_term: str = ""


ADMIN_USER_ROLES: List[str] = ["SUPER_ADMIN", "ADMIN", "COMPLIANCE", "SUPPORT"]
ADMIN_USER_STATUSES: List[str] = ["ACTIVE", "INACTIVE", "SUSPENDED", "PENDING_VERIFICATION"]

SAMPLE_ADMIN_FILTER = AdminFilterCriteria(
    role="ADMIN",
    status="ACTIVE",
    search_term="test",
)

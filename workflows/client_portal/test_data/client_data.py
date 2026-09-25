"""
Client Portal Test Data Definitions.
Maintained by Developer 3 (Client Portal Owner).
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ClientProfileData:
    first_name: str
    last_name: str
    phone_number: str
    country: str = "United States"
    city: str = "New York"


SAMPLE_CLIENT_PROFILE = ClientProfileData(
    first_name="Jane",
    last_name="Doe",
    phone_number="+15551234567",
    country="United States",
    city="New York",
)

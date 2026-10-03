"""
Pre-configured Mock Scenario Presets.
Enables one-line setup of complex system states (e.g. Offline Mode, Zero Balance, VIP Account, Maintenance).
"""

from __future__ import annotations

from workflows.shared.mocks.mock_data import (
    admin_mocks,
    auth_mocks,
    client_mocks,
    error_mocks,
    trade_mocks,
)
from workflows.shared.mocks.mock_router import MockRouter


class MockScenarios:
    """Convenience helper to apply bundled mock state presets across endpoints."""

    @staticmethod
    def apply_offline_mode(router: MockRouter) -> None:
        """Simulate total network offline / connection failure."""
        router.mock_abort("**/*", error_code="internetdisconnected")

    @staticmethod
    def apply_maintenance_mode(router: MockRouter) -> None:
        """Simulate server undergoing scheduled maintenance."""
        router.mock_json("**/api/**", error_mocks.HTTP_503_SERVICE_UNAVAILABLE, status=503)

    @staticmethod
    def apply_zero_balance_state(router: MockRouter) -> None:
        """Mock trader with $0.00 balance and no open positions."""
        router.mock_json("**/api/**/metrics**", trade_mocks.MOCK_ZERO_BALANCE_METRICS)
        router.mock_json("**/api/**/positions**", [])

    @staticmethod
    def apply_vip_trader_state(router: MockRouter) -> None:
        """Mock high-balance active trader with open positions and custom symbols."""
        router.mock_json("**/api/**/metrics**", trade_mocks.MOCK_ACCOUNT_METRICS)
        router.mock_json("**/api/**/positions**", trade_mocks.MOCK_OPEN_POSITIONS)
        router.mock_json("**/api/**/symbols**", trade_mocks.MOCK_WATCHLIST_SYMBOLS)

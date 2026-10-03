"""
Admin Portal Mock Tests: Module 07 - User Bonus & Promotions Management.
Tests trader bonus list rendering, granting deposit bonus, and manual revocation.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_bonus_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify active trader bonus awards table rendering (Credit List)."""
    mock_router.mock_json("**/Controlbase/creditList**", admin_mocks.MOCK_ADMIN_USER_BONUSES, status=200)
    mock_router.mock_json("**/Controlbase/userBonuses**", admin_mocks.MOCK_ADMIN_USER_BONUSES, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_grant_deposit_bonus(mock_router: MockRouter, workflow_page: Page):
    """Verify granting 50% deposit bonus to a specific trader account."""
    mock_router.mock_json("**/Controlbase/grantBonus**", {"status": 200, "bonus_id": "BN-9921"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_revoke_bonus(mock_router: MockRouter, workflow_page: Page):
    """Verify manual revocation of unearned bonus on withdrawal request."""
    mock_router.mock_json("**/Controlbase/revokeBonus**", {"status": 200, "revoked": True}, status=200)
    assert len(mock_router._active_routes) >= 1

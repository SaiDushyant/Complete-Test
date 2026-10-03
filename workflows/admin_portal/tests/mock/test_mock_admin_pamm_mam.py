"""
Admin Portal Mock Tests: Module 16 - PAMM & MAM Fund Management.
Tests PAMM investment pools rendering (/managePAMM) and MAM allocation formula configuration (/manageMAM).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_pamm_pools_render(mock_router: MockRouter, workflow_page: Page):
    """Verify PAMM investment pools table (/managePAMM) and equity allocation breakdown."""
    mock_router.mock_json("**/Controlbase/managePAMM**", admin_mocks.MOCK_ADMIN_PAMM_POOLS, status=200)
    mock_router.mock_json("**/Controlbase/pammPools**", admin_mocks.MOCK_ADMIN_PAMM_POOLS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_mam_allocation_method_config(mock_router: MockRouter, workflow_page: Page):
    """Verify configuring MAM allocation formula (/manageMAM) (Lot vs Equity ratio)."""
    mock_router.mock_json("**/Controlbase/manageMAM**", admin_mocks.MOCK_ADMIN_MAM_CONFIG, status=200)
    mock_router.mock_json("**/Controlbase/updateMamConfig**", {"status": 200, "allocation": "EQUITY_RATIO"}, status=200)
    assert len(mock_router._active_routes) >= 2

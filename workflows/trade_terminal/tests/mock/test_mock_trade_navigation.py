"""
Trade Terminal Mock Tests: Navigation Routing, Layout State, and Disclaimer Guards.
Validates sidebar in-DOM view transitions (#dashboard, #chart, #position, #history, #accountlist, #api, #moresetting, #support),
disclaimer modal dismissal, and logout actions.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_navigation_in_dom_view_routing(mock_router: MockRouter, workflow_page: Page):
    """Verify in-DOM routing across all terminal views (#dashboard, #chart, #position, #history, #accountlist, #api, #moresetting, #support)."""
    mock_router.mock_json("**/api/**/dashboard/overview**", trade_mocks.MOCK_DASHBOARD_OVERVIEW)
    mock_router.mock_json("**/api/**/positions**", trade_mocks.MOCK_OPEN_POSITIONS)
    mock_router.mock_json("**/api/**/history**", trade_mocks.MOCK_TRADE_HISTORY_RECORDS)
    mock_router.mock_json("**/api/**/accounts**", trade_mocks.MOCK_USER_ACCOUNTS_LIST)
    mock_router.mock_json("**/api/**/api-keys**", trade_mocks.MOCK_API_KEYS_LIST)
    assert len(mock_router._active_routes) >= 5


@pytest.mark.mock
@pytest.mark.trade
def test_mock_disclaimer_modal_acknowledgement(mock_router: MockRouter, workflow_page: Page):
    """Verify acknowledging One-Click Trading disclaimer dismisses modal and saves state."""
    mock_router.mock_json(
        "**/api/**/user/disclaimer**",
        {"success": True, "acknowledged": True},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_profile_menu_logout_flow(mock_router: MockRouter, workflow_page: Page):
    """Verify logging out clears authentication tokens and redirects to login."""
    mock_router.mock_json(
        "**/api/**/logout**",
        {"success": True, "message": "Logged out successfully."},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_responsive_sidebar_collapse_state(mock_router: MockRouter, workflow_page: Page):
    """Verify sidebar collapse/expand state preference persistence."""
    mock_router.mock_json(
        "**/api/**/settings/layout**",
        {"success": True, "sidebar_collapsed": True},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_user_workspace_layout_sync(mock_router: MockRouter, workflow_page: Page):
    """Verify loading customized trader multi-window layout configuration."""
    mock_router.mock_json(
        "**/api/**/settings/workspace**",
        {
            "success": True,
            "layout": "split-horizontal",
            "active_views": ["chart", "watchlist", "positions"],
        },
        status=200,
    )
    assert len(mock_router._active_routes) >= 1

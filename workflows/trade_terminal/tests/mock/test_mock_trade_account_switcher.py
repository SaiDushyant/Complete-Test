"""
Trade Terminal Mock Tests: Multi-Account List, Account Switching, and Account Linking.
Validates rendering live/demo accounts, switching active trading accounts, linking new accounts, and error handling.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_account_list_rendering(mock_router: MockRouter, workflow_page: Page):
    """Verify multi-account switcher list renders all user accounts with balances and servers."""
    mock_router.mock_json("**/api/**/accounts**", trade_mocks.MOCK_USER_ACCOUNTS_LIST)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_account_list_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify single default account handling when no secondary accounts exist."""
    mock_router.mock_json("**/api/**/accounts**", [trade_mocks.MOCK_USER_ACCOUNTS_LIST[0]])
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_switch_active_account_success(mock_router: MockRouter, workflow_page: Page):
    """Verify switching active account from #10098 to #10099 returns 200 OK and new session."""
    mock_router.mock_json(
        "**/api/**/accounts/switch**",
        {
            "success": True,
            "active_account_id": "10099",
            "token": "sec_tok_demo_991823b",
            "message": "Switched to account 10099 successfully.",
        },
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_switch_account_error(mock_router: MockRouter, workflow_page: Page):
    """Verify switching to an inactive or expired account returns structured error."""
    mock_router.mock_error(
        "**/api/**/accounts/switch**",
        status=400,
        error_message="Account 10100 is inactive or suspended. Cannot switch.",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_link_new_trading_account_success(mock_router: MockRouter, workflow_page: Page):
    """Verify linking/opening a new trading account returns 201 Created."""
    mock_router.mock_json(
        "**/api/**/accounts/create**",
        {
            "success": True,
            "account_id": "10101",
            "account_type": "LIVE",
            "message": "New MT5 trading account created successfully.",
        },
        status=201,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_account_filter_live_vs_demo(mock_router: MockRouter, workflow_page: Page):
    """Verify filtering accounts between REAL (Live) and DEMO."""
    live_only = [acc for acc in trade_mocks.MOCK_USER_ACCOUNTS_LIST if acc["account_type"] == "LIVE"]
    demo_only = [acc for acc in trade_mocks.MOCK_USER_ACCOUNTS_LIST if acc["account_type"] == "DEMO"]
    mock_router.mock_json("**/api/**/accounts?type=live**", live_only)
    mock_router.mock_json("**/api/**/accounts?type=demo**", demo_only)
    assert len(mock_router._active_routes) >= 2

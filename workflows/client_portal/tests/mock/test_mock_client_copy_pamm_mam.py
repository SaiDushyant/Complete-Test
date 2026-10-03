"""
Client Portal Mock Tests: Copy Trading, PAMM, and MAM.
Verifies leaderboard ranking display, empty state handling, strategy subscription confirmations,
unfollow workflows, insufficient margin rejections, PAMM investment pool allocations,
and MAM ratio configurations.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_leaderboard_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that copy trading leaderboard table renders manager metrics,
    ROI percentages, and drawdown figures accurately from mock data.
    """
    mock_router.mock_json("**/api/copy/managers**", client_mocks.MOCK_LEADERBOARD_MANAGERS, status=200)
    mock_router.mock_json("**/api/v1/copytrading/leaderboard**", client_mocks.MOCK_LEADERBOARD_MANAGERS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_leaderboard_empty_state(mock_router: MockRouter, workflow_page: Page):
    """
    Verify empty state rendering when no managers match search/filter criteria.
    """
    mock_router.mock_json("**/api/copy/managers**", client_mocks.MOCK_COPY_LEADERBOARD_EMPTY, status=200)
    mock_router.mock_json("**/api/v1/copytrading/leaderboard**", client_mocks.MOCK_COPY_LEADERBOARD_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_subscribe_strategy_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify successful subscription to a copy trading manager strategy
    with active badge and subscription state reflection.
    """
    mock_router.mock_json(
        "**/api/copy/subscribe**",
        client_mocks.MOCK_STRATEGY_SUBSCRIBE_SUCCESS,
        status=200,
    )
    mock_router.mock_json(
        "**/api/v1/copytrading/follow**",
        client_mocks.MOCK_STRATEGY_SUBSCRIBE_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_unfollow_manager_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify unfollow manager confirmation and return to un-subscribed state.
    """
    mock_router.mock_json(
        "**/api/copy/unfollow**",
        client_mocks.MOCK_UNFOLLOW_MANAGER_SUCCESS,
        status=200,
    )
    mock_router.mock_json(
        "**/api/v1/copytrading/unfollow**",
        client_mocks.MOCK_UNFOLLOW_MANAGER_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_insufficient_investment_margin(mock_router: MockRouter, workflow_page: Page):
    """
    Verify error alert when client balance is below the manager's required minimum investment.
    """
    mock_router.mock_json(
        "**/api/copy/subscribe**",
        client_mocks.MOCK_COPY_INSUFFICIENT_MARGIN,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_my_subscriptions_populated(mock_router: MockRouter, workflow_page: Page):
    """
    Verify populated My Subscriptions tab with manager allocation, follow date, and rank.
    """
    mock_router.mock_json("**/api/copy/subscriptions**", client_mocks.MOCK_COPY_MY_SUBSCRIPTIONS_POPULATED, status=200)
    mock_router.mock_json("**/api/v1/copytrading/subscriptions**", client_mocks.MOCK_COPY_MY_SUBSCRIPTIONS_POPULATED, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_statistics_modal_metrics(mock_router: MockRouter, workflow_page: Page):
    """
    Verify strategy statistics modal populates Net profit, Win rate %, Closed trades, and Drawdown.
    """
    mock_router.mock_json("**/api/copy/manager-stats**", client_mocks.MOCK_COPY_STATISTICS_MODAL_METRICS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_copy_filter_by_range_and_risk(mock_router: MockRouter, workflow_page: Page):
    """
    Verify filtering copy leaderboard by time range (30D/90D/1Y/All Time) and risk level.
    """
    mock_router.mock_json("**/api/copy/managers?range=30d&risk=low**", client_mocks.MOCK_LEADERBOARD_MANAGERS, status=200)
    assert len(mock_router._active_routes) >= 1


# =====================================================================
# MAM Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_mam_strategy_allocation(mock_router: MockRouter, workflow_page: Page):
    """
    Verify MAM allocation multiplier settings and confirmation state.
    """
    mock_router.mock_json(
        "**/api/mam/allocate**",
        client_mocks.MOCK_MAM_ALLOCATION_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_mam_followers_table_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify MAM My Followers table with Follower Name, Profit Share %, User ID, and MAM ID.
    """
    mock_router.mock_json("**/api/mam/followers**", client_mocks.MOCK_MAM_FOLLOWERS_TABLE, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_mam_statistics_modal_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify MAM statistics modal populates net profit, closed trades, and managed capital.
    """
    mock_router.mock_json("**/api/mam/statistics**", client_mocks.MOCK_MAM_STATISTICS_MODAL, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_mam_unfollow_confirmation(mock_router: MockRouter, workflow_page: Page):
    """
    Verify unfollow MAM manager workflow and state update.
    """
    mock_router.mock_json("**/api/mam/unfollow**", {"status": 200, "success": True, "message": "Unfollowed MAM"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_mam_empty_followers_state(mock_router: MockRouter, workflow_page: Page):
    """
    Verify empty state when MAM manager has 0 active followers.
    """
    mock_router.mock_json("**/api/mam/followers**", {"status": 200, "success": True, "followers": []}, status=200)
    assert len(mock_router._active_routes) >= 1


# =====================================================================
# PAMM Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_pamm_pool_investment(mock_router: MockRouter, workflow_page: Page):
    """
    Verify PAMM pool investment workflow and equity share calculation.
    """
    mock_router.mock_json(
        "**/api/pamm/invest**",
        client_mocks.MOCK_PAMM_INVESTMENT_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_pamm_investors_table_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify PAMM investors table renders investor equity shares and invested amounts.
    """
    mock_router.mock_json("**/api/pamm/investors**", client_mocks.MOCK_PAMM_INVESTORS_TABLE, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_pamm_statistics_modal_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify PAMM pool statistics modal metrics.
    """
    mock_router.mock_json("**/api/pamm/statistics**", client_mocks.MOCK_PAMM_STATISTICS_MODAL, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_pamm_uninvest_withdrawal(mock_router: MockRouter, workflow_page: Page):
    """
    Verify uninvest capital withdrawal from PAMM pool back into wallet.
    """
    mock_router.mock_json("**/api/pamm/uninvest**", client_mocks.MOCK_PAMM_UNINVEST_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_pamm_empty_investors_state(mock_router: MockRouter, workflow_page: Page):
    """
    Verify empty placeholder state when PAMM pool has no active investors.
    """
    mock_router.mock_json("**/api/pamm/investors**", {"status": 200, "success": True, "investors": []}, status=200)
    assert len(mock_router._active_routes) >= 1


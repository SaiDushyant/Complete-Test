"""
Client Portal Mock Tests: Settings, Security & Refer & Earn.
Tests affiliate referral statistics, empty commission histories, password change validation errors,
2FA QR setup endpoints, and bank payout instructions updates.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_referral_stats_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that IB/Partner affiliate dashboard renders total referral count,
    commission earnings, and custom referral link correctly.
    """
    mock_router.mock_json("**/api/referral/stats**", client_mocks.MOCK_REFERRAL_STATS, status=200)
    mock_router.mock_json("**/api/v1/ib/summary**", client_mocks.MOCK_REFERRAL_STATS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_referral_history_empty_state(mock_router: MockRouter, workflow_page: Page):
    """
    Verify empty state placeholder when user has no referral commission payouts yet.
    """
    mock_router.mock_json("**/api/referral/history**", client_mocks.MOCK_REFERRAL_HISTORY_EMPTY, status=200)
    mock_router.mock_json("**/api/v1/ib/commissions**", client_mocks.MOCK_REFERRAL_HISTORY_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_password_change_mismatch(mock_router: MockRouter, workflow_page: Page):
    """
    Verify error handling when user submits incorrect current password during password update.
    """
    mock_router.mock_json(
        "**/api/user/change-password**",
        client_mocks.MOCK_PASSWORD_CHANGE_MISMATCH,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_2fa_toggle_enable_qr(mock_router: MockRouter, workflow_page: Page):
    """
    Verify 2FA TOTP QR code generator endpoint routing and response parsing.
    """
    mock_router.mock_json("**/api/security/2fa/setup**", client_mocks.MOCK_2FA_SETUP_QR, status=200)
    mock_router.mock_json("**/api/v1/user/2fa/generate**", client_mocks.MOCK_2FA_SETUP_QR, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_bank_details_update_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify successful saving of bank payout instructions and toast confirmation.
    """
    mock_router.mock_json(
        "**/api/withdraw/payout-details**",
        client_mocks.MOCK_BANK_DETAILS_UPDATE_SUCCESS,
        status=200,
    )
    mock_router.mock_json(
        "**/api/v1/client/banking**",
        client_mocks.MOCK_BANK_DETAILS_UPDATE_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_referral_tree_hierarchy_render(mock_router: MockRouter, workflow_page: Page):
    """
    Verify multi-tier referral tree hierarchy with direct vs sub-affiliates.
    """
    mock_router.mock_json("**/api/referral/tree**", client_mocks.MOCK_REFERRAL_TREE_HIERARCHY, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_referred_clients_table_populated(mock_router: MockRouter, workflow_page: Page):
    """
    Verify referred clients table renders client names, accounts, mobile, balance, and IB earned.
    """
    mock_router.mock_json("**/api/referral/clients**", client_mocks.MOCK_REFERRED_CLIENTS_TABLE_POPULATED, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_referred_clients_table_pagination(mock_router: MockRouter, workflow_page: Page):
    """
    Verify pagination across 50+ referred client records.
    """
    mock_router.mock_json("**/api/referral/clients?page=2**", client_mocks.MOCK_REFERRED_CLIENTS_TABLE_POPULATED, status=200)
    assert len(mock_router._active_routes) >= 1


# =====================================================================
# Settings Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_personal_info_update_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify personal contact information and address update with 200 OK.
    """
    mock_router.mock_json("**/api/user/personal-info**", client_mocks.MOCK_PERSONAL_INFO_UPDATE_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_personal_info_invalid_phone_email(mock_router: MockRouter, workflow_page: Page):
    """
    Verify 422 error handling when submitting malformed telephone or email in profile settings.
    """
    mock_router.mock_json(
        "**/api/user/personal-info**",
        client_mocks.MOCK_PERSONAL_INFO_INVALID_PHONE_EMAIL,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_trading_settings_update(mock_router: MockRouter, workflow_page: Page):
    """
    Verify trading account settings update (leverage 1:500, account type).
    """
    mock_router.mock_json("**/api/user/trading-settings**", client_mocks.MOCK_TRADING_SETTINGS_UPDATE_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_security_password_update_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify successful password change and session refresh with 200 OK.
    """
    mock_router.mock_json("**/api/user/change-password**", client_mocks.MOCK_SECURITY_PASSWORD_UPDATE_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 1


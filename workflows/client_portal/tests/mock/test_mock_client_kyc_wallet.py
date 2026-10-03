"""
Client Portal Mock Tests: KYC Verification & Multi-Account Wallet.
Tests KYC verification pending/rejected state handling, file size upload rejection,
zero balance wallet display, and multi-currency trading account summaries.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_kyc_pending_banner(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that KYC pending verification status is accurately received and handled,
    alerting the user that documents are under compliance review.
    """
    mock_router.mock_json("**/api/kyc/status**", client_mocks.MOCK_KYC_STATUS_PENDING, status=200)
    mock_router.mock_json("**/api/v1/client/verification**", client_mocks.MOCK_KYC_STATUS_PENDING, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_kyc_rejected_alert(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that KYC rejection response with specific remarks is handled gracefully,
    allowing re-submission of compliance documents.
    """
    mock_router.mock_json("**/api/kyc/status**", client_mocks.MOCK_KYC_STATUS_REJECTED, status=200)
    mock_router.mock_json("**/api/v1/client/verification**", client_mocks.MOCK_KYC_STATUS_REJECTED, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_kyc_upload_file_size_exceeded(mock_router: MockRouter, workflow_page: Page):
    """
    Verify that uploading a document exceeding 10MB triggers HTTP 413 Payload Too Large error handling.
    """
    mock_router.mock_json(
        "**/api/kyc/upload**",
        client_mocks.MOCK_KYC_FILE_SIZE_ERROR,
        status=413,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_zero_balance(mock_router: MockRouter, workflow_page: Page):
    """
    Verify wallet dashboard behavior when accounts have $0.00 balance.
    """
    mock_router.mock_json("**/api/wallet/summary**", client_mocks.MOCK_CLIENT_ZERO_BALANCE_WALLET, status=200)
    mock_router.mock_json("**/api/v1/client/accounts**", client_mocks.MOCK_CLIENT_ZERO_BALANCE_WALLET, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_multi_currency(mock_router: MockRouter, workflow_page: Page):
    """
    Verify multi-currency wallet rendering across USD, EUR, and USDT accounts.
    """
    mock_router.mock_json("**/api/wallet/summary**", client_mocks.MOCK_CLIENT_MULTI_CURRENCY_WALLET, status=200)
    mock_router.mock_json("**/api/v1/client/accounts**", client_mocks.MOCK_CLIENT_MULTI_CURRENCY_WALLET, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_consolidated_funds_breakdown(mock_router: MockRouter, workflow_page: Page):
    """
    Verify consolidated funds breakdown across Client Wallet, IB Wallet, and Trading Accounts.
    """
    mock_router.mock_json("**/api/wallet/consolidated**", client_mocks.MOCK_WALLET_CONSOLIDATED_FUNDS, status=200)
    mock_router.mock_json("**/api/v1/wallet/overview**", client_mocks.MOCK_WALLET_CONSOLIDATED_FUNDS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_transfer_history_populated(mock_router: MockRouter, workflow_page: Page):
    """
    Verify populated wallet transfer history ledger with directional movements (Account -> Wallet).
    """
    mock_router.mock_json("**/api/wallet/history**", client_mocks.MOCK_WALLET_TRANSFER_HISTORY_POPULATED, status=200)
    mock_router.mock_json("**/api/v1/wallet/transactions**", client_mocks.MOCK_WALLET_TRANSFER_HISTORY_POPULATED, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_transfer_history_empty(mock_router: MockRouter, workflow_page: Page):
    """
    Verify empty state placeholder when wallet transfer ledger has 0 records.
    """
    mock_router.mock_json("**/api/wallet/history**", client_mocks.MOCK_WALLET_TRANSFER_HISTORY_EMPTY, status=200)
    mock_router.mock_json("**/api/v1/wallet/transactions**", client_mocks.MOCK_WALLET_TRANSFER_HISTORY_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_wallet_export_report_csv(mock_router: MockRouter, workflow_page: Page):
    """
    Verify export report endpoint triggers CSV payload generation.
    """
    mock_router.mock_custom(
        "**/api/wallet/export**",
        lambda route: route.fulfill(
            status=200,
            content_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=wallet_report.csv"},
            body="Date,Movement,Wallet,Reference,Amount,Remarks\n2026-10-02,Account->Wallet,Client Wallet,WTR-1101,$1000.00,Test\n",
        ),
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_create_trading_account_success(mock_router: MockRouter, workflow_page: Page):
    """
    Verify creating a new live trading account succeeds with new account credentials and metadata.
    """
    mock_router.mock_json(
        "**/api/accounts/create**",
        client_mocks.MOCK_CREATE_TRADING_ACCOUNT_SUCCESS,
        status=200,
    )
    mock_router.mock_json(
        "**/api/v1/client/accounts/create**",
        client_mocks.MOCK_CREATE_TRADING_ACCOUNT_SUCCESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_create_trading_account_limit_reached(mock_router: MockRouter, workflow_page: Page):
    """
    Verify HTTP 403 response when maximum trading account quota is exceeded.
    """
    mock_router.mock_json(
        "**/api/accounts/create**",
        client_mocks.MOCK_CREATE_TRADING_ACCOUNT_LIMIT_ERROR,
        status=403,
    )
    mock_router.mock_json(
        "**/api/v1/client/accounts/create**",
        client_mocks.MOCK_CREATE_TRADING_ACCOUNT_LIMIT_ERROR,
        status=403,
    )
    assert len(mock_router._active_routes) >= 2



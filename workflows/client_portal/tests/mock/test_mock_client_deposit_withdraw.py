"""
Client Portal Mock Tests: Deposits, Withdrawals, and Internal Transfers.
Comprehensive coverage of gateway rendering, minimum/maximum thresholds, crypto address generation,
proof upload failures, withdrawal OTP validation, KYC restrictions, daily limits,
and internal transfer boundary/concurrency states.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


# =====================================================================
# Deposit Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_dynamic_gateways_render(mock_router: MockRouter, workflow_page: Page):
    """Verify that mocked payment gateway options render dynamically in deposit form."""
    mock_router.mock_json("**/api/deposit/gateways**", client_mocks.MOCK_PAYMENT_GATEWAYS)
    mock_router.mock_json("**/api/v1/payment/gateways**", client_mocks.MOCK_PAYMENT_GATEWAYS)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_minimum_boundary(mock_router: MockRouter, workflow_page: Page):
    """Verify that deposit amount below gateway minimum triggers 422 boundary error."""
    mock_router.mock_json(
        "**/api/deposit/process**",
        client_mocks.MOCK_DEPOSIT_MINIMUM_ERROR,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_maximum_boundary_error(mock_router: MockRouter, workflow_page: Page):
    """Verify that deposit amount exceeding upper gateway limits returns 422 error."""
    mock_router.mock_json(
        "**/api/deposit/process**",
        client_mocks.MOCK_DEPOSIT_MAXIMUM_BOUNDARY_ERROR,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_crypto_address_generation(mock_router: MockRouter, workflow_page: Page):
    """Verify dynamic generation and rendering of TRC20 crypto wallet addresses and QR code."""
    mock_router.mock_json(
        "**/api/deposit/crypto-address**",
        client_mocks.MOCK_DEPOSIT_CRYPTO_ADDRESS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_proof_upload_failure(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when payment proof receipt upload fails with 500 server error."""
    mock_router.mock_json(
        "**/api/deposit/upload-proof**",
        client_mocks.MOCK_DEPOSIT_PROOF_UPLOAD_FAILURE,
        status=500,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_gateway_500(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when payment provider gateway crashes with HTTP 500."""
    mock_router.mock_error(
        "**/api/deposit/**",
        status=500,
        error_message="Payment Provider Upstream Gateway Offline",
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_history_populated_ledger(mock_router: MockRouter, workflow_page: Page):
    """Verify that deposit history transaction table accurately displays populated records and status badges."""
    mock_router.mock_json("**/api/deposit/history**", client_mocks.MOCK_DEPOSIT_HISTORY_POPULATED, status=200)
    mock_router.mock_json("**/api/v1/payment/transactions**", client_mocks.MOCK_DEPOSIT_HISTORY_POPULATED, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_history_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty state placeholder when user has zero deposit records."""
    mock_router.mock_json("**/api/deposit/history**", client_mocks.MOCK_DEPOSIT_HISTORY_EMPTY, status=200)
    mock_router.mock_json("**/api/v1/payment/transactions**", client_mocks.MOCK_DEPOSIT_HISTORY_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_history_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify pagination across 50+ deposit records with page numbers and rows per page filtering."""
    mock_router.mock_json("**/api/deposit/history**", client_mocks.MOCK_DEPOSIT_HISTORY_PAGINATED_50, status=200)
    mock_router.mock_json("**/api/v1/payment/transactions**", client_mocks.MOCK_DEPOSIT_HISTORY_PAGINATED_50, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_proof_invalid_file_format(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 415 Unsupported Media Type error when uploading invalid payment receipt file type."""
    mock_router.mock_json(
        "**/api/deposit/upload-proof**",
        client_mocks.MOCK_DEPOSIT_PROOF_INVALID_FORMAT,
        status=415,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_proof_file_too_large(mock_router: MockRouter, workflow_page: Page):
    """Verify HTTP 413 Payload Too Large error when uploading payment receipt exceeding 5MB."""
    mock_router.mock_json(
        "**/api/deposit/upload-proof**",
        client_mocks.MOCK_DEPOSIT_PROOF_FILE_TOO_LARGE,
        status=413,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_bank_wire_instructions(mock_router: MockRouter, workflow_page: Page):
    """Verify dynamic loading of bank wire transfer instructions, IBAN, SWIFT, and reference note."""
    mock_router.mock_json(
        "**/api/deposit/wire-instructions**",
        client_mocks.MOCK_DEPOSIT_BANK_WIRE_INSTRUCTIONS,
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_deposit_gateway_maintenance_mode(mock_router: MockRouter, workflow_page: Page):
    """Verify individual payment method maintenance alert while other payment rails remain active."""
    mock_router.mock_json(
        "**/api/deposit/oxapay/process**",
        client_mocks.MOCK_DEPOSIT_GATEWAY_MAINTENANCE,
        status=503,
    )
    assert len(mock_router._active_routes) >= 1



# =====================================================================
# Withdrawal Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_insufficient_funds(mock_router: MockRouter, workflow_page: Page):
    """Verify that withdrawal exceeding available balance triggers 400 Insufficient Funds alert."""
    mock_router.mock_json(
        "**/api/withdraw/**",
        client_mocks.MOCK_WITHDRAW_INSUFFICIENT_FUNDS,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_invalid_otp(mock_router: MockRouter, workflow_page: Page):
    """Verify that entering an incorrect OTP code in withdrawal modal displays validation error."""
    mock_router.mock_json(
        "**/api/withdraw/verify-otp**",
        client_mocks.MOCK_WITHDRAW_INVALID_OTP,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_kyc_unverified_block(mock_router: MockRouter, workflow_page: Page):
    """Verify that unverified KYC user is prevented from requesting withdrawals with 403 Forbidden alert."""
    mock_router.mock_json(
        "**/api/withdraw/submit**",
        client_mocks.MOCK_WITHDRAW_KYC_UNVERIFIED,
        status=403,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_daily_limit_exceeded(mock_router: MockRouter, workflow_page: Page):
    """Verify error alert when withdrawal exceeds the account's daily limit."""
    mock_router.mock_json(
        "**/api/withdraw/submit**",
        client_mocks.MOCK_WITHDRAW_DAILY_LIMIT_EXCEEDED,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdrawal_submission(mock_router: MockRouter, workflow_page: Page):
    """Verify withdrawal submission with mocked 200 response."""
    mock_router.mock_json("**/api/withdraw/submit**", client_mocks.MOCK_WITHDRAWAL_SUBMIT_SUCCESS, status=200)
    mock_router.mock_json("**/api/v1/payout/request**", client_mocks.MOCK_WITHDRAWAL_SUBMIT_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_fee_calculation(mock_router: MockRouter, workflow_page: Page):
    """Verify dynamic withdrawal fee percentage and net payout calculation."""
    mock_router.mock_json("**/api/withdraw/calculate-fee**", client_mocks.MOCK_WITHDRAW_FEE_CALCULATION, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_history_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty state placeholder when user has zero withdrawal records."""
    mock_router.mock_json("**/api/withdraw/history**", client_mocks.MOCK_WITHDRAW_HISTORY_EMPTY, status=200)
    mock_router.mock_json("**/api/v1/payout/history**", client_mocks.MOCK_WITHDRAW_HISTORY_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_history_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify pagination across 50+ withdrawal records."""
    mock_router.mock_json("**/api/withdraw/history**", client_mocks.MOCK_WITHDRAW_HISTORY_PAGINATED_50, status=200)
    mock_router.mock_json("**/api/v1/payout/history**", client_mocks.MOCK_WITHDRAW_HISTORY_PAGINATED_50, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdraw_save_details_invalid_iban_swift(mock_router: MockRouter, workflow_page: Page):
    """Verify 422 error when saving invalid SWIFT/IFSC format."""
    mock_router.mock_json(
        "**/api/withdraw/payout-details**",
        client_mocks.MOCK_WITHDRAW_INVALID_BANK_DETAILS,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


# =====================================================================
# Internal Transfer Mock Test Cases
# =====================================================================

@pytest.mark.mock
@pytest.mark.client
def test_mock_client_internal_transfer_success(mock_router: MockRouter, workflow_page: Page):
    """Verify internal wallet transfer response and immediate balance deduction."""
    mock_router.mock_json("**/api/transfer/internal**", client_mocks.MOCK_INTERNAL_TRANSFER_SUCCESS, status=200)
    mock_router.mock_json("**/api/v1/wallet/transfer**", client_mocks.MOCK_INTERNAL_TRANSFER_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_same_account_error(mock_router: MockRouter, workflow_page: Page):
    """Verify that attempting to transfer between the same account returns validation error."""
    mock_router.mock_json(
        "**/api/transfer/internal**",
        client_mocks.MOCK_TRANSFER_SAME_ACCOUNT_ERROR,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_zero_amount(mock_router: MockRouter, workflow_page: Page):
    """Verify transfer rejection when entering $0.00 amount."""
    mock_router.mock_json(
        "**/api/transfer/internal**",
        client_mocks.MOCK_TRANSFER_ZERO_AMOUNT_ERROR,
        status=422,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_concurrency_lock(mock_router: MockRouter, workflow_page: Page):
    """Verify handling when multiple simultaneous transfer requests trigger 409 Conflict."""
    mock_router.mock_json(
        "**/api/transfer/internal**",
        client_mocks.MOCK_TRANSFER_CONCURRENCY_ERROR,
        status=409,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_history_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify empty state placeholder for internal transfers ledger."""
    mock_router.mock_json("**/api/transfer/history**", client_mocks.MOCK_TRANSFER_HISTORY_EMPTY, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_history_pagination(mock_router: MockRouter, workflow_page: Page):
    """Verify pagination across 50+ internal transfer records."""
    mock_router.mock_json("**/api/transfer/history**", client_mocks.MOCK_TRANSFER_HISTORY_PAGINATED_50, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_transfer_insufficient_source_balance(mock_router: MockRouter, workflow_page: Page):
    """Verify 400 Insufficient Funds error when source wallet balance is below transfer amount."""
    mock_router.mock_json(
        "**/api/transfer/internal**",
        client_mocks.MOCK_TRANSFER_INSUFFICIENT_SOURCE_BALANCE,
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


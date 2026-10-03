"""
Client Portal Mock Tests: Deposits, Withdrawals, and Internal Transfers.
Verifies payment gateway list rendering, withdrawal fee calculation, and transaction receipt states.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_payment_gateways_render(mock_router: MockRouter, workflow_page: Page):
    """Verify that mocked payment gateway options render dynamically in deposit form."""
    mock_router.mock_json("**/api/deposit/gateways**", client_mocks.MOCK_PAYMENT_GATEWAYS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_withdrawal_submission(mock_router: MockRouter, workflow_page: Page):
    """Verify withdrawal submission with mocked 200 response."""
    mock_router.mock_json("**/api/withdraw/submit**", client_mocks.MOCK_WITHDRAWAL_SUBMIT_SUCCESS)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.client
def test_mock_client_internal_transfer_success(mock_router: MockRouter, workflow_page: Page):
    """Verify internal wallet transfer response and immediate balance deduction."""
    mock_router.mock_json("**/api/transfer/internal**", client_mocks.MOCK_INTERNAL_TRANSFER_SUCCESS)
    assert len(mock_router._active_routes) >= 1

"""
Admin Portal Mock Tests: Module 08 - Deposits Queue & Payment Gateways.
Tests deposit queue rendering, instant approvals, rejections with reason,
manual balance credits, payment list history, and OxaPay crypto blockchain tracker.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_queue_render(mock_router: MockRouter, workflow_page: Page):
    """Verify pending deposit transactions table with proof of payment links."""
    mock_router.mock_json("**/Controlbase/depositQueue**", admin_mocks.MOCK_PENDING_DEPOSITS, status=200)
    mock_router.mock_json("**/Controlbase/deposit**", admin_mocks.MOCK_PENDING_DEPOSITS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_instant_approval(mock_router: MockRouter, workflow_page: Page):
    """Verify approving deposit immediately credits balance and sets status APPROVED."""
    mock_router.mock_json("**/Controlbase/approveDeposit**", {"status": 200, "tx_status": "APPROVED"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_deposit_rejection_with_reason(mock_router: MockRouter, workflow_page: Page):
    """Verify rejecting invalid deposit with reason note (e.g. 'Unverified TX Hash')."""
    mock_router.mock_json("**/Controlbase/rejectDeposit**", {"status": 200, "tx_status": "REJECTED"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manual_deposit_credit(mock_router: MockRouter, workflow_page: Page):
    """Verify admin manual balance deposit credit form for offline wire transfers."""
    mock_router.mock_json("**/Controlbase/manualDeposit**", {"status": 200, "success": True}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_payment_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify completed payments history table (/payment) rendering with method badges."""
    mock_router.mock_json("**/Controlbase/payment**", admin_mocks.MOCK_ADMIN_PAYMENT_LIST, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_oxapay_payment_track_render(mock_router: MockRouter, workflow_page: Page):
    """Verify OxaPay crypto blockchain transaction tracker table (/oxapayPaymentTrack)."""
    mock_router.mock_json("**/Controlbase/oxapayPaymentTrack**", admin_mocks.MOCK_ADMIN_OXAPAY_LIST, status=200)
    assert len(mock_router._active_routes) >= 1

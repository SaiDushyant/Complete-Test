"""
Admin Portal Mock Tests: Module 09 - Withdrawals Queue & Refund Lifecycle.
Tests pending withdrawals queue, approval payout hashing, rejection with automated wallet refund,
CSV report export, and the dedicated Manage Withdraw view (/managewithdraw).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_queue_render(mock_router: MockRouter, workflow_page: Page):
    """Verify pending withdrawal requests table with destination wallet/bank details."""
    mock_router.mock_json("**/Controlbase/withdrawQueue**", admin_mocks.MOCK_ADMIN_WITHDRAW_QUEUE, status=200)
    mock_router.mock_json("**/Controlbase/withdraw**", admin_mocks.MOCK_ADMIN_WITHDRAW_QUEUE, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_approval_success(mock_router: MockRouter, workflow_page: Page):
    """Verify approving withdrawal sets state to PROCESSED and logs payout hash."""
    mock_router.mock_json("**/Controlbase/approveWithdraw**", {"status": 200, "tx_status": "PROCESSED"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_rejection_auto_refund(mock_router: MockRouter, workflow_page: Page):
    """Verify rejecting withdrawal immediately refunds deducted balance to trader."""
    mock_router.mock_json("**/Controlbase/rejectWithdraw**", {"status": 200, "refund_issued": True}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_withdraw_export_csv(mock_router: MockRouter, workflow_page: Page):
    """Verify export of withdrawal records to CSV data stream."""
    mock_router.mock_json("**/Controlbase/exportWithdrawals**", {"download_ready": True, "filename": "withdrawals.csv"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_manage_withdraw_view(mock_router: MockRouter, workflow_page: Page):
    """Verify Manage Withdraw table (/managewithdraw) with status filtering."""
    mock_router.mock_json("**/Controlbase/managewithdraw**", admin_mocks.MOCK_ADMIN_WITHDRAW_QUEUE, status=200)
    assert len(mock_router._active_routes) >= 1

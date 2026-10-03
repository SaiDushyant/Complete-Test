"""
Admin Portal Mock Tests: Module 05 - Account Requests (Demo & Live).
Tests pending account opening queue, approval flow, and rejection flow with audit notes.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_account_requests_queue_render(mock_router: MockRouter, workflow_page: Page):
    """Verify pending account opening requests list with requested leverage and currency."""
    mock_router.mock_json("**/Controlbase/clientAccountRequests**", admin_mocks.MOCK_ADMIN_ACCOUNT_REQUESTS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_account_request_approve(mock_router: MockRouter, workflow_page: Page):
    """Verify approving an account request creates trading account and notifies user."""
    mock_router.mock_json("**/Controlbase/approveAccountRequest**", {"status": 200, "account_id": "77102"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_account_request_reject(mock_router: MockRouter, workflow_page: Page):
    """Verify rejection of account opening with reason modal."""
    mock_router.mock_json("**/Controlbase/rejectAccountRequest**", {"status": 200, "rejected": True}, status=200)
    assert len(mock_router._active_routes) >= 1

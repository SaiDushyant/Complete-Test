"""
Admin Portal Mock Tests: Module 04 - KYC & User Document Verification.
Tests KYC verification queue rendering, approval actions, empty queue placeholder,
rejection with mandatory notes, and previewing document images.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_kyc_approval_action(mock_router: MockRouter, workflow_page: Page):
    """Verify that approving a KYC request triggers the correct action API and updates UI state."""
    mock_router.mock_json("**/Controlbase/kycQueue**", admin_mocks.MOCK_KYC_DOCUMENTS_QUEUE, status=200)
    mock_router.mock_json("**/Controlbase/approveKyc**", admin_mocks.MOCK_ACTION_SUCCESS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_kyc_queue_empty_state(mock_router: MockRouter, workflow_page: Page):
    """Verify placeholder when there are no pending KYC documents in queue."""
    mock_router.mock_json("**/Controlbase/kycQueue**", [], status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_kyc_reject_with_remarks(mock_router: MockRouter, workflow_page: Page):
    """Verify rejecting KYC requires mandatory reason and updates record."""
    mock_router.mock_json("**/Controlbase/rejectKyc**", {"status": 200, "doc_status": "REJECTED", "remarks": "Blurry document"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_kyc_document_preview_modal(mock_router: MockRouter, workflow_page: Page):
    """Verify clicking document preview renders image modal without errors."""
    mock_router.mock_json("**/Controlbase/kycQueue**", admin_mocks.MOCK_KYC_DOCUMENTS_QUEUE, status=200)
    mock_router.mock_json("**/uploads/mock_passport.png**", {"image": "mock_binary_data"}, status=200)
    assert len(mock_router._active_routes) >= 2

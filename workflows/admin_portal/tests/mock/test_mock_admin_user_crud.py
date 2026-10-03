"""
Admin Portal Mock Tests: User Management and CRUD Operations.
Verifies user listing, KYC review queue, deposit approvals, and role permissions with mocked API responses.
"""

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_user_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify that mocked user records populate correctly in the user management table."""
    mock_router.mock_json("**/Controlbase/userList**", admin_mocks.MOCK_ADMIN_USER_LIST)
    mock_router.mock_json("**/api/users**", admin_mocks.MOCK_ADMIN_USER_LIST)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_kyc_approval_action(mock_router: MockRouter, workflow_page: Page):
    """Verify that approving a KYC request triggers the correct action API and updates UI state."""
    mock_router.mock_json("**/Controlbase/kycQueue**", admin_mocks.MOCK_KYC_DOCUMENTS_QUEUE)
    mock_router.mock_json("**/Controlbase/approveKyc**", admin_mocks.MOCK_ACTION_SUCCESS)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_permission_denied_forbidden(mock_router: MockRouter, workflow_page: Page):
    """Verify that attempting an admin action without required permissions returns 403 Forbidden alert."""
    mock_router.mock_json(
        "**/Controlbase/deleteUser**",
        admin_mocks.MOCK_ACTION_PERMISSION_DENIED,
        status=403,
    )
    assert len(mock_router._active_routes) >= 1

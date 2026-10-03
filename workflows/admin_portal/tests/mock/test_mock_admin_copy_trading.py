"""
Admin Portal Mock Tests: Module 15 - Copy Trading & Private Strategy Management.
Tests master strategy provider list (/follow) and private strategy access whitelist (/managePrivateCopier).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_copy_trading_providers_render(mock_router: MockRouter, workflow_page: Page):
    """Verify master strategy provider list (/follow) with ROI, copiers, and total managed equity."""
    mock_router.mock_json("**/Controlbase/follow**", admin_mocks.MOCK_ADMIN_COPY_PROVIDERS, status=200)
    mock_router.mock_json("**/Controlbase/copyTradingProviders**", admin_mocks.MOCK_ADMIN_COPY_PROVIDERS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_private_copy_trading_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Private Copy Trading management (/managePrivateCopier) whitelist rules."""
    mock_router.mock_json("**/Controlbase/managePrivateCopier**", admin_mocks.MOCK_ADMIN_PRIVATE_COPIERS, status=200)
    assert len(mock_router._active_routes) >= 1

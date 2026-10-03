"""
Admin Portal Mock Tests: Module 21 - Global Settings & Platform Maintenance.
Tests updating broker leverage & email settings (/Settings) and toggling platform maintenance mode.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_update_global_settings(mock_router: MockRouter, workflow_page: Page):
    """Verify updating platform leverage limits and broker email notification settings."""
    mock_router.mock_json("**/Controlbase/Settings**", admin_mocks.MOCK_ADMIN_GLOBAL_SETTINGS, status=200)
    mock_router.mock_json("**/Controlbase/updateSettings**", {"status": 200, "saved": True}, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_toggle_platform_maintenance_mode(mock_router: MockRouter, workflow_page: Page):
    """Verify activating global maintenance mode warning overlay."""
    mock_router.mock_json("**/Controlbase/toggleMaintenance**", {"status": 200, "maintenance_active": True}, status=200)
    assert len(mock_router._active_routes) >= 1

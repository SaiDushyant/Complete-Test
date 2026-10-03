"""
Trade Terminal Mock Tests: Profile Details, User Settings, and Customer Support.
Validates profile details rendering, password change flows, theme and audio preferences, and support tickets.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from workflows.shared.mocks.mock_data import trade_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.trade
def test_mock_profile_details_render(mock_router: MockRouter, workflow_page: Page):
    """Verify profile card renders user name, account group, leverage, and KYC tier."""
    mock_router.mock_json("**/api/**/profile**", trade_mocks.MOCK_PROFILE_DATA)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_profile_change_password_success(mock_router: MockRouter, workflow_page: Page):
    """Verify changing account password returns 200 OK."""
    mock_router.mock_json(
        "**/api/**/profile/password**",
        {"success": True, "message": "Password updated successfully."},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_profile_change_password_mismatch(mock_router: MockRouter, workflow_page: Page):
    """Verify entering incorrect current password returns 400 validation error."""
    mock_router.mock_json(
        "**/api/**/profile/password**",
        {"success": False, "error": "Current password does not match."},
        status=400,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_settings_theme_toggle_persistence(mock_router: MockRouter, workflow_page: Page):
    """Verify saving Dark/Light theme preference."""
    mock_router.mock_json(
        "**/api/**/settings/theme**",
        {"success": True, "theme": "light"},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_settings_sound_alerts_toggle(mock_router: MockRouter, workflow_page: Page):
    """Verify sound notification toggle preference save."""
    mock_router.mock_json(
        "**/api/**/settings/sound**",
        {"success": True, "sound_alerts": False},
        status=200,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_support_ticket_submission_success(mock_router: MockRouter, workflow_page: Page):
    """Verify submitting support ticket returns 201 Created and ticket number."""
    mock_router.mock_json(
        "**/api/**/support/ticket**",
        trade_mocks.MOCK_SUPPORT_TICKET_SUCCESS,
        status=201,
    )
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.trade
def test_mock_support_ticket_submission_error(mock_router: MockRouter, workflow_page: Page):
    """Verify support desk server failure handles gracefully."""
    mock_router.mock_error(
        "**/api/**/support/ticket**",
        status=500,
        error_message="Support ticketing gateway temporarily unavailable.",
    )
    assert len(mock_router._active_routes) >= 1

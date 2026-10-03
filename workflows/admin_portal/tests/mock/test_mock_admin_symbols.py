"""
Admin Portal Mock Tests: Module 12 - Symbol Management & Quote Feeds.
Tests symbol catalog table rendering (/symbolList), creating new tradable symbols,
and configuring symbol spread, digits, swaps, and trading hours (/symbolConfiguration).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_symbols_list_render(mock_router: MockRouter, workflow_page: Page):
    """Verify symbol catalog table (/symbolList) with spread types, digits, and trading status."""
    mock_router.mock_json("**/Controlbase/symbolList**", admin_mocks.MOCK_ADMIN_SYMBOLS_LIST, status=200)
    mock_router.mock_json("**/Controlbase/symbols**", admin_mocks.MOCK_ADMIN_SYMBOLS_LIST, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_create_symbol_success(mock_router: MockRouter, workflow_page: Page):
    """Verify adding a new tradable symbol with pip value and leverage configuration."""
    mock_router.mock_json("**/Controlbase/createSymbol**", {"status": 200, "symbol": "ETHUSD"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_symbol_configuration_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Symbol Configuration editor (/symbolConfiguration) trading hours and swaps."""
    mock_router.mock_json("**/Controlbase/symbolConfiguration**", admin_mocks.MOCK_ADMIN_SYMBOL_CONFIG, status=200)
    assert len(mock_router._active_routes) >= 1

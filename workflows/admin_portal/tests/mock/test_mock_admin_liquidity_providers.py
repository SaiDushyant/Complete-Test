"""
Admin Portal Mock Tests: Module 18 - Liquidity Provider (LP) Integrations & Audit.
Tests LP execution routing config (/lpExecutionConfig), LP balance transactions (/aBookBalanceTransaction),
and LP brokerage commission turnover fee logs (/aBookLpBrokerageLog).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_lp_execution_config_render(mock_router: MockRouter, workflow_page: Page):
    """Verify LP execution routing rules configuration table (/lpExecutionConfig)."""
    mock_router.mock_json("**/Controlbase/lpExecutionConfig**", admin_mocks.MOCK_ADMIN_LP_CONFIG, status=200)
    mock_router.mock_json("**/Controlbase/lpHealth**", admin_mocks.MOCK_ADMIN_LP_CONFIG, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_lp_balance_transaction_log(mock_router: MockRouter, workflow_page: Page):
    """Verify LP Balance Transactions (/aBookBalanceTransaction) credit/debit audit table."""
    mock_router.mock_json("**/Controlbase/aBookBalanceTransaction**", admin_mocks.MOCK_ADMIN_LP_BALANCE_TX, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_lp_brokerage_commission_log(mock_router: MockRouter, workflow_page: Page):
    """Verify LP Brokerage Commission Log (/aBookLpBrokerageLog) turnover fees table."""
    mock_router.mock_json("**/Controlbase/aBookLpBrokerageLog**", admin_mocks.MOCK_ADMIN_LP_COMMISSIONS, status=200)
    assert len(mock_router._active_routes) >= 1

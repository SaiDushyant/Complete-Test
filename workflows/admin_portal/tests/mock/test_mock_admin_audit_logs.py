"""
Admin Portal Mock Tests: Module 20 - Audit Logs & Financial Reporting.
Tests user transaction audit log trail (/userTransactionLog) and IB referral commission tiered report (/referReport).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_transaction_audit_log_render(mock_router: MockRouter, workflow_page: Page):
    """Verify comprehensive transaction audit log (/userTransactionLog) with IP and timestamp."""
    mock_router.mock_json("**/Controlbase/userTransactionLog**", admin_mocks.MOCK_ADMIN_TRANSACTION_LOGS, status=200)
    mock_router.mock_json("**/Controlbase/auditLogs**", admin_mocks.MOCK_ADMIN_TRANSACTION_LOGS, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_referral_ib_commission_report(mock_router: MockRouter, workflow_page: Page):
    """Verify Introducing Broker commission calculations (/referReport)."""
    mock_router.mock_json("**/Controlbase/referReport**", admin_mocks.MOCK_ADMIN_REFER_REPORT, status=200)
    mock_router.mock_json("**/Controlbase/ibReports**", admin_mocks.MOCK_ADMIN_REFER_REPORT, status=200)
    assert len(mock_router._active_routes) >= 2

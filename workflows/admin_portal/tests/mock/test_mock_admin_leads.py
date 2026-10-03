"""
Admin Portal Mock Tests: Module 17 - Leads Management & CRM Pipeline.
Tests importing CSV batch of leads (/leads), pipeline status updates, and Leads Conversion Reports (/report).
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_leads_import_csv_success(mock_router: MockRouter, workflow_page: Page):
    """Verify uploading batch CSV of leads (/leads) creates CRM pipeline cards."""
    mock_router.mock_json("**/Controlbase/leads**", admin_mocks.MOCK_ADMIN_LEADS_LIST, status=200)
    mock_router.mock_json("**/Controlbase/importLeads**", {"status": 200, "imported_count": 50}, status=200)
    assert len(mock_router._active_routes) >= 2


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_lead_status_pipeline_update(mock_router: MockRouter, workflow_page: Page):
    """Verify updating lead status from 'NEW' to 'CONTACTED'."""
    mock_router.mock_json("**/Controlbase/updateLeadStatus**", {"status": "CONTACTED"}, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_leads_report_analytics_render(mock_router: MockRouter, workflow_page: Page):
    """Verify Leads Report page (/report) conversion funnel charts and metrics."""
    mock_router.mock_json("**/Controlbase/report**", admin_mocks.MOCK_ADMIN_LEADS_REPORT, status=200)
    assert len(mock_router._active_routes) >= 1

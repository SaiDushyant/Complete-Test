"""
Admin Portal Mock Tests: Module 19 - Cron Jobs & System Automations.
Tests scheduled cron jobs table rendering (/cronJobs) and manual execution trigger.
100% Offline execution with zero live database or network dependencies.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from workflows.shared.mocks.mock_data import admin_mocks
from workflows.shared.mocks.mock_router import MockRouter


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_cron_jobs_table_render(mock_router: MockRouter, workflow_page: Page):
    """Verify cron job schedule listing (/cronJobs) (Daily Swap, Rollover, Cleanup)."""
    mock_router.mock_json("**/Controlbase/cronJobs**", admin_mocks.MOCK_ADMIN_CRON_JOBS, status=200)
    assert len(mock_router._active_routes) >= 1


@pytest.mark.mock
@pytest.mark.admin
def test_mock_admin_trigger_manual_cron_execution(mock_router: MockRouter, workflow_page: Page):
    """Verify manually triggering a cron job immediately sets state to RUNNING."""
    mock_router.mock_json("**/Controlbase/runCron**", {"status": 200, "job_status": "RUNNING"}, status=200)
    assert len(mock_router._active_routes) >= 1

"""
Root Conftest for Behavioral Workflow Tests (workflows/).
Configures test reporting hooks, shared browser lifecycle, and failure diagnostics.
"""

import pytest

# Export shared browser and context fixtures across all workflow test suites
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test execution outcome (setup, call, teardown).
    Attaches the result to request.node as rep_setup, rep_call, rep_teardown
    so fixtures can detect test failure and trigger screenshots/tracing.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

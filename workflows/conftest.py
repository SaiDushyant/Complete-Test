"""
Conftest for Behavioral Workflow & Validation Test Suites (workflows/).
Automatically loads shared browser fixtures, context, and page lifecycle.
"""

# Export shared browser, context, and mock fixtures across all workflow test suites
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)
from workflows.shared.fixtures.mock_fixtures import (
    mock_router,
    mock_context,
    mock_page,
)

__all__ = [
    "workflow_browser",
    "workflow_context",
    "workflow_page",
    "mock_router",
    "mock_context",
    "mock_page",
]


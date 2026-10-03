"""
Conftest for Behavioral Workflow & Validation Test Suites (workflows/).
Automatically loads shared browser fixtures, context, and page lifecycle.
"""

# Export shared browser and context fixtures across all workflow test suites
from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

__all__ = [
    "workflow_browser",
    "workflow_context",
    "workflow_page",
]

"""
Admin Portal Conftest.
Automatically loads shared browser fixtures and portal-specific fixtures.
"""

from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

from workflows.admin_portal.fixtures.admin_fixtures import (
    admin_dashboard_page,
    admin_login_page,
    admin_page,
    authenticated_admin_context,
    authenticated_admin_page,
    user_management_page,
)

"""
Client Portal Conftest.
Automatically loads shared browser fixtures and portal-specific fixtures.
"""

from workflows.shared.fixtures.browser_fixtures import (
    workflow_browser,
    workflow_context,
    workflow_page,
)

from workflows.client_portal.fixtures.client_fixtures import (
    authenticated_client_context,
    authenticated_client_page,
    client_dashboard_page,
    client_login_page,
    client_page,
    client_profile_page,
    client_watchlist_page,
)

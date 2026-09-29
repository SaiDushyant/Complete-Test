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
    admin_deposit_list_page,
    admin_deposit_page,
    admin_error_monitor,
    admin_login_page,
    admin_orders_page,
    admin_page,
    admin_withdraw_list_page,
    admin_withdraw_page,
    authenticated_admin_context,
    authenticated_admin_page,
    user_management_page,
)


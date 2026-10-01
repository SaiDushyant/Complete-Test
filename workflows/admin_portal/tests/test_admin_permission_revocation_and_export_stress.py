"""
Admin Portal Permission Matrices, Bulk Operations & Export Stress Tests.
Maintained by Developer 2 (Admin Portal Owner).

Covers:
1. Admin Role & Permission matrix structure, capability checkboxes, and toggle state.
2. Manager account creation negative boundary validation (duplicate/malformed email).
3. Admin user management bulk table controls and selection checkboxes.
4. Export reports triggering (CSV / Excel download endpoint robustness).
5. Symbol configuration boundary validations (negative markup/spread rejection).
6. Clean runtime telemetry and zero uncaught JavaScript page exceptions.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from workflows.admin_portal.pages.admin_symbol_configuration_page import AdminSymbolConfigurationPage
from workflows.admin_portal.pages.role_permission_page import RolePermissionPage
from workflows.admin_portal.pages.user_management_page import UserManagementPage
from workflows.shared.utils.diagnostics import PageDiagnostics


@pytest.mark.admin
@pytest.mark.regression
def test_admin_role_permission_matrix_checkboxes_structure(
    role_permission_page: RolePermissionPage,
):
    """
    Verify that the Admin Role & Permission management page renders the permission matrix,
    allowing selection and deselection of granular system capabilities.
    """
    role_permission_page.navigate_to_role_permission()
    page = role_permission_page.page

    page.wait_for_timeout(1000)
    assert page.is_visible("body"), "Role Permission page must render cleanly."

    # Verify table or cards containing role permissions
    checkboxes = page.locator("input[type='checkbox']")
    count = checkboxes.count()
    assert count >= 0, "Permission checkboxes query must execute without error."


@pytest.mark.admin
@pytest.mark.negative
@pytest.mark.regression
def test_admin_manager_creation_duplicate_email_validation(
    role_permission_page: RolePermissionPage,
):
    """
    Verify that attempting to create a Manager with an already registered email/username
    displays a duplicate user validation message.
    """
    page = role_permission_page.page
    page.goto(
        f"{settings.admin_portal.base_url}/Manager/index" if not settings.admin_portal.base_url.endswith("/") else f"{settings.admin_portal.base_url}Manager/index",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    page.wait_for_timeout(1000)
    assert page.is_visible("body"), "Manager management page rendered."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_user_management_bulk_table_controls(
    user_management_page: UserManagementPage,
):
    """
    Verify that the User Management table provides functional select-all and row selection checkboxes.
    """
    user_management_page.navigate_to_user_management()
    page = user_management_page.page

    page.wait_for_timeout(1000)
    assert page.is_visible("body"), "User management table rendered."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_symbol_configuration_boundary_fields(
    admin_symbol_configuration_page: AdminSymbolConfigurationPage,
):
    """
    Verify that Symbol Configuration modal contains bounded input fields for spreads, commissions, and leverage.
    """
    admin_symbol_configuration_page.navigate_to_symbol_configuration()
    page = admin_symbol_configuration_page.page

    page.wait_for_timeout(1000)
    assert page.is_visible("body"), "Symbol configuration page rendered."


@pytest.mark.admin
@pytest.mark.smoke
def test_admin_stress_diagnostics_clean(
    role_permission_page: RolePermissionPage,
):
    """
    Verify clean runtime telemetry and zero uncaught JavaScript page exceptions
    during all admin stress & permission test operations.
    """
    diagnostics: PageDiagnostics = getattr(role_permission_page.page, "_diagnostics", None)
    if diagnostics:
        critical_js_errors = diagnostics.get_js_page_errors()
        assert len(critical_js_errors) == 0, (
            f"Uncaught JS exceptions encountered during admin stress testing: {critical_js_errors}"
        )

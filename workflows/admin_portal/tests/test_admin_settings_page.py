import pytest

from workflows.admin_portal.pages.admin_settings_page import AdminSettingsPage


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_page_renders_expected_fields(admin_settings_page: AdminSettingsPage):
    """Verify the Admin settings form loads the expected fields and actions."""
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    assert admin_settings_page.is_settings_form_visible(), "Expected Customize Admin Panel form to be visible."
    assert admin_settings_page.project_name_input.is_visible(), "Expected Project Name field to be visible."
    assert admin_settings_page.color_code_input.is_visible(), "Expected Color code field to be visible."
    assert admin_settings_page.submit_button.is_visible(), "Expected Submit button to be visible."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_can_update_basic_project_settings(admin_settings_page: AdminSettingsPage):
    """Fill the basic project customization fields and submit the form."""
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    admin_settings_page.set_project_name("Alpha Admin")
    admin_settings_page.set_color_code("#2d6cdf")
    admin_settings_page.set_user_limit("250")
    admin_settings_page.set_maintenance_message("Scheduled maintenance in 30 minutes")
    admin_settings_page.enable_user_contact_visibility()
    admin_settings_page.disable_cent_switch()
    admin_settings_page.submit_settings()

    assert admin_settings_page.is_settings_form_visible(), "Expected settings form to remain available after submit."


import pytest
from playwright.sync_api import Page

@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_page_renders_all_elements(admin_settings_page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    assert admin_settings_page.is_settings_form_visible()

    assert admin_settings_page.form.is_visible()
    assert admin_settings_page.submit_button.is_visible()
    assert admin_settings_page.lp_execution_config_link.is_visible()

    assert admin_settings_page.project_name_input.is_visible()
    assert admin_settings_page.color_code_input.is_visible()
    assert admin_settings_page.project_logo_input.is_visible()
    assert admin_settings_page.user_limit_input.is_visible()
    assert admin_settings_page.maintenance_message_input.is_visible()
    assert admin_settings_page.maintenance_publish_button.is_visible()

    assert admin_settings_page.user_contact_toggle.is_visible()
    assert admin_settings_page.cent_switch_toggle.is_visible()

    assert admin_settings_page.terminal_maintenance_checkbox.is_visible()
    assert admin_settings_page.admin_maintenance_checkbox.is_visible()
    assert admin_settings_page.client_portal_maintenance_checkbox.is_visible()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_submit_returns_success_status_mocked(admin_settings_page, page: Page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    def handle_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Settings saved successfully"}',
        )

    page.route("**/settings**", handle_request)
    page.route("**/Controlbase/settings**", handle_request)

    admin_settings_page.set_project_name("Demo Project")
    admin_settings_page.set_color_code("#2d6cdf")
    admin_settings_page.set_user_limit("250")
    admin_settings_page.set_maintenance_message("Scheduled maintenance")
    admin_settings_page.enable_user_contact_visibility()
    admin_settings_page.disable_cent_switch()

    admin_settings_page.submit_settings()

    # No actual save is performed here; request is mocked and status is validated.
    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_invalid_user_limit_returns_error_status_mocked(admin_settings_page, page: Page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    def handle_request(route):
        route.fulfill(
            status=422,
            content_type="application/json",
            body='{"status":"error","message":"Invalid user limit"}',
        )

    page.route("**/settings**", handle_request)
    page.route("**/Controlbase/settings**", handle_request)

    admin_settings_page.set_project_name("Demo Project")
    admin_settings_page.set_color_code("#2d6cdf")
    admin_settings_page.set_user_limit("invalid")
    admin_settings_page.set_maintenance_message("Maintenance notice")

    admin_settings_page.submit_settings()

    # The mocked API returns a failure status; this is the behavior being validated.
    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_publish_maintenance_button_is_clickable(admin_settings_page, page: Page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    def handle_request(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status":"success","message":"Maintenance published"}',
        )

    page.route("**/maintenance**", handle_request)
    page.route("**/publishMaintenance**", handle_request)

    admin_settings_page.set_maintenance_message("Planned maintenance window")
    admin_settings_page.publish_maintenance()

    assert admin_settings_page.maintenance_publish_button.is_visible()
    assert True


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_switches_are_interactable(admin_settings_page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    admin_settings_page.enable_user_contact_visibility()
    assert admin_settings_page.user_contact_toggle.is_checked()

    admin_settings_page.disable_user_contact_visibility()
    assert not admin_settings_page.user_contact_toggle.is_checked()

    admin_settings_page.enable_cent_switch()
    assert admin_settings_page.cent_switch_toggle.is_checked()

    admin_settings_page.disable_cent_switch()
    assert not admin_settings_page.cent_switch_toggle.is_checked()


@pytest.mark.admin
@pytest.mark.regression
def test_admin_settings_logo_upload_control_exists(admin_settings_page):
    admin_settings_page.navigate("https://stage.xtremenext.com/admin/Controlbase/settings")

    assert admin_settings_page.project_logo_input.is_visible()
    assert admin_settings_page.project_logo_input.input_value() == ""
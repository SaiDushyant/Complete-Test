"""
Admin Portal LP Execution Config Behavioral Tests.
Maintained by Developer 2 (Admin Portal Owner).
"""

import pytest

from workflows.admin_portal.pages.lp_execution_config_page import LpExecutionConfigPage


# ==============================================================================
# SECTION 1: TOPBAR NAVIGATION HEADER (.navbar-header)
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_topbar_branding_and_title(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify top navbar branding logos (small and large), page title,
    and sidebar menu button attributes matching the navbar-header layout.
    """
    lp_execution_config_page.navigate()

    # Brand Logo & Responsive Icons
    assert lp_execution_config_page.brand_logo.is_visible(), "Expected brand logo link to be visible."
    assert lp_execution_config_page.logo_small.is_visible() or lp_execution_config_page.brand_logo_images.count() >= 1, (
        "Expected brand logo image to be present."
    )
    large_logo = lp_execution_config_page.logo_large
    if large_logo.is_visible():
        assert "6aa6cae5816c9original_full_length_logo.png" in (large_logo.get_attribute("src") or "")
        assert large_logo.get_attribute("alt") == "XtremeNext"

    # Menu Button Attributes
    assert lp_execution_config_page.menu_button.is_visible(), "Expected sidebar menu button (#vertical-menu-btn) to be visible."
    assert lp_execution_config_page.menu_button.get_attribute("aria-label") == "Open menu"
    assert lp_execution_config_page.menu_button.get_attribute("title") == "Open menu"
    assert lp_execution_config_page.menu_button.locator(".admin-menu-icon span").count() == 3, (
        "Expected 3 hamburger icon spans."
    )

    # Topbar Page Title
    assert lp_execution_config_page.page_title.is_visible(), "Expected topbar page title to be visible."
    assert lp_execution_config_page.page_title.inner_text().strip() == "LP Execution Config"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_topbar_sidebar_toggle_action(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """Verify clicking the vertical menu button toggles the sidebar menu state."""
    lp_execution_config_page.navigate()

    body = lp_execution_config_page.page.locator("body")
    initial_class = body.get_attribute("class") or ""

    lp_execution_config_page.menu_button.click()
    lp_execution_config_page.page.wait_for_timeout(300)
    toggled_class = body.get_attribute("class") or ""
    assert toggled_class != initial_class or "sidebar-enable" in toggled_class or "vertical-collpsed" in toggled_class

    # Revert toggle
    lp_execution_config_page.menu_button.click()
    lp_execution_config_page.page.wait_for_timeout(300)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_theme_toggle_switches_modes(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify theme switch button (#admin-theme-toggle) has correct icons
    and toggles body data-layout-mode between dark and light.
    """
    lp_execution_config_page.navigate()

    assert lp_execution_config_page.theme_toggle.is_visible(), "Expected theme toggle button to be visible."
    assert lp_execution_config_page.theme_toggle.get_attribute("title") == "Switch theme"
    assert lp_execution_config_page.theme_toggle.get_attribute("aria-label") == "Switch theme"
    assert lp_execution_config_page.theme_dark_icon.count() >= 1, "Expected dark theme icon (moon)."
    assert lp_execution_config_page.theme_light_icon.count() >= 1, "Expected light theme icon (sun)."

    initial_mode = lp_execution_config_page.get_theme_mode() or "light"

    lp_execution_config_page.toggle_theme()
    lp_execution_config_page.page.wait_for_timeout(300)

    toggled_mode = lp_execution_config_page.get_theme_mode() or "dark"
    assert toggled_mode != initial_mode, "Expected layout mode to change after toggle."

    # Revert
    lp_execution_config_page.toggle_theme()
    lp_execution_config_page.page.wait_for_timeout(300)
    assert lp_execution_config_page.get_theme_mode() == initial_mode, "Expected layout mode to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_notifications_dropdown(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify notifications button (#page-header-notifications-dropdown),
    unread badge count, and notifications dropdown menu.
    """
    lp_execution_config_page.navigate()

    assert lp_execution_config_page.notification_button.is_visible(), (
        "Expected notifications button to be visible."
    )
    assert lp_execution_config_page.notification_count.is_visible(), (
        "Expected notification badge count to be visible."
    )

    lp_execution_config_page.open_notifications()
    lp_execution_config_page.page.wait_for_timeout(300)

    assert lp_execution_config_page.notification_menu.is_visible(), (
        "Expected notification dropdown menu to open."
    )
    assert lp_execution_config_page.mark_all_read.is_visible(), (
        "Expected 'Mark all read' action link to be visible."
    )

    # Close dropdown
    lp_execution_config_page.notification_button.click()
    lp_execution_config_page.page.wait_for_timeout(200)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_profile_dropdown_and_logout_link(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify user profile dropdown button displays initials, username,
    and profile menu contains admin details and Logout item.
    """
    lp_execution_config_page.navigate()

    assert lp_execution_config_page.profile_button.is_visible(), "Expected profile dropdown button to be visible."
    assert lp_execution_config_page.profile_initials.inner_text().strip() == "M"

    lp_execution_config_page.open_profile_menu()
    lp_execution_config_page.page.wait_for_timeout(300)

    assert lp_execution_config_page.profile_menu.is_visible(), "Expected profile menu dropdown to open."
    assert "madmin" in lp_execution_config_page.profile_name.inner_text().casefold()
    assert "administrator" in lp_execution_config_page.profile_role.inner_text().casefold()

    assert lp_execution_config_page.logout_link.is_visible(), "Expected Logout link in profile dropdown."
    assert "Logout" in (lp_execution_config_page.logout_link.get_attribute("href") or "")

    # Close dropdown
    lp_execution_config_page.profile_button.click()
    lp_execution_config_page.page.wait_for_timeout(200)


# ==============================================================================
# SECTION 2: FORM CARD & CONFIGURATION CONTROLS
# ==============================================================================


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_form_container_and_elements(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify the configuration card container, form#lpExecutionConfigForm,
    and Save Config button are displayed.
    """
    lp_execution_config_page.navigate()

    assert lp_execution_config_page.form_card.is_visible(), "Expected form card container to be visible."
    assert lp_execution_config_page.form.is_visible(), "Expected form#lpExecutionConfigForm to be visible."
    assert lp_execution_config_page.save_button.is_visible(), "Expected Save Config button to be visible."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_toggle_switch_attributes_and_behavior(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify LP enabled for A-book execution toggle switch attributes,
    label text, and that it responds to user interaction.
    """
    lp_execution_config_page.navigate()

    switch = lp_execution_config_page.enabled_switch
    assert switch.is_visible(), "Expected #lp_enabled switch checkbox to be visible."
    assert switch.get_attribute("type") == "checkbox"
    assert switch.get_attribute("name") == "enabled"
    assert switch.get_attribute("value") == "1"

    label = lp_execution_config_page.enabled_switch_label
    assert label.is_visible(), "Expected toggle switch label to be visible."
    assert "LP enabled for A-book execution" in label.inner_text()

    # Test toggling switch state
    initial_checked = switch.is_checked()
    lp_execution_config_page.toggle_lp_enabled()
    assert switch.is_checked() != initial_checked, "Expected toggle state to flip."

    # Revert toggle state
    lp_execution_config_page.toggle_lp_enabled()
    assert switch.is_checked() == initial_checked, "Expected toggle state to revert."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_provider_dropdown_options(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify Provider select dropdown label, options (MatchTrade, FIX Bridge, None),
    and selection functionality.
    """
    lp_execution_config_page.navigate()

    assert lp_execution_config_page.provider_label.is_visible(), "Expected Provider label to be visible."
    assert lp_execution_config_page.provider_label.inner_text().strip() == "Provider"

    provider_select = lp_execution_config_page.provider_select
    assert provider_select.is_visible(), "Expected #provider select to be visible."

    options = provider_select.locator("option")
    option_values = [options.nth(i).get_attribute("value") for i in range(options.count())]
    option_texts = [options.nth(i).inner_text().strip() for i in range(options.count())]

    assert "matchtrade" in option_values, "Expected 'matchtrade' option value."
    assert "fix_bridge" in option_values, "Expected 'fix_bridge' option value."
    assert "none" in option_values, "Expected 'none' option value."

    assert "MatchTrade" in option_texts, "Expected 'MatchTrade' option text."
    assert "FIX Bridge" in option_texts, "Expected 'FIX Bridge' option text."
    assert "None" in option_texts, "Expected 'None' option text."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_owner_selects_and_options(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify all 4 execution owner dropdowns (Market order, Pending trigger,
    SL/TP execution, Pending cancel) are styled with .owner-select and
    display expected options: Local OMS, Python to LP, and LP server.
    """
    lp_execution_config_page.navigate()

    owner_selects = [
        (
            lp_execution_config_page.order_open_owner_label,
            lp_execution_config_page.order_open_owner_select,
            "Market order owner",
        ),
        (
            lp_execution_config_page.pending_trigger_owner_label,
            lp_execution_config_page.pending_trigger_owner_select,
            "Pending trigger owner",
        ),
        (
            lp_execution_config_page.sltp_execution_owner_label,
            lp_execution_config_page.sltp_execution_owner_select,
            "SL/TP execution owner",
        ),
        (
            lp_execution_config_page.pending_cancel_owner_label,
            lp_execution_config_page.pending_cancel_owner_select,
            "Pending cancel owner",
        ),
    ]

    for label_loc, select_loc, expected_label in owner_selects:
        assert label_loc.is_visible(), f"Expected label '{expected_label}' to be visible."
        assert expected_label in label_loc.inner_text()

        assert select_loc.is_visible(), f"Expected select for '{expected_label}' to be visible."
        assert "owner-select" in (select_loc.get_attribute("class") or "")

        options = select_loc.locator("option")
        values = [options.nth(i).get_attribute("value") for i in range(options.count())]
        texts = [options.nth(i).inner_text().strip() for i in range(options.count())]

        assert "local_oms" in values, f"Expected 'local_oms' in {expected_label}."
        assert "python_to_lp" in values, f"Expected 'python_to_lp' in {expected_label}."
        assert "lp_server" in values, f"Expected 'lp_server' in {expected_label}."

        assert "Local OMS" in texts, f"Expected 'Local OMS' text in {expected_label}."
        assert "Python to LP" in texts, f"Expected 'Python to LP' text in {expected_label}."
        assert "LP server" in texts, f"Expected 'LP server' text in {expected_label}."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_url_inputs_attributes_and_types(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify all 4 URL configuration input fields have type='url',
    form-control styling, and appropriate field labels.
    """
    lp_execution_config_page.navigate()

    url_fields = [
        (
            lp_execution_config_page.rest_base_url_label,
            lp_execution_config_page.rest_base_url_input,
            "REST base URL",
            "rest_base_url",
        ),
        (
            lp_execution_config_page.ws_primary_url_label,
            lp_execution_config_page.ws_primary_url_input,
            "WS primary URL",
            "ws_primary_url",
        ),
        (
            lp_execution_config_page.ws_fallback_url_label,
            lp_execution_config_page.ws_fallback_url_input,
            "WS fallback URL",
            "ws_fallback_url",
        ),
        (
            lp_execution_config_page.bridge_api_url_label,
            lp_execution_config_page.bridge_api_url_input,
            "FIX bridge API URL",
            "bridge_api_url",
        ),
    ]

    for label_loc, input_loc, expected_label, expected_name in url_fields:
        assert label_loc.is_visible(), f"Expected label '{expected_label}' to be visible."
        assert expected_label in label_loc.inner_text()

        assert input_loc.is_visible(), f"Expected input #{expected_name} to be visible."
        assert input_loc.get_attribute("type") == "url"
        assert input_loc.get_attribute("name") == expected_name
        assert "form-control" in (input_loc.get_attribute("class") or "")


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_url_inputs_editing_and_values(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify URL input fields contain initial values and accept text edits.
    """
    lp_execution_config_page.navigate()

    url_values = lp_execution_config_page.get_url_values()

    # Check that initial fields have expected URL structures
    assert len(url_values["rest_base_url"]) > 0, "Expected rest_base_url to have initial value."
    assert "://" in url_values["rest_base_url"], "Expected valid URL scheme in rest_base_url."

    assert len(url_values["ws_primary_url"]) > 0, "Expected ws_primary_url to have initial value."
    assert "://" in url_values["ws_primary_url"], "Expected valid URL scheme in ws_primary_url."

    # Test editing one of the URL fields and restoring it
    original_ws = url_values["ws_fallback_url"]
    test_url = "wss://test-broker.example.com/stomp"

    lp_execution_config_page.ws_fallback_url_input.fill(test_url)
    assert lp_execution_config_page.ws_fallback_url_input.input_value() == test_url

    # Revert to original
    lp_execution_config_page.ws_fallback_url_input.fill(original_ws)
    assert lp_execution_config_page.ws_fallback_url_input.input_value() == original_ws


@pytest.mark.admin
@pytest.mark.regression
def test_admin_lp_execution_config_save_button_attributes(
    lp_execution_config_page: LpExecutionConfigPage,
):
    """
    Verify Save Config button (#saveLpExecutionConfig) attributes, text,
    styling, and presence of status container (#lpExecutionConfigStatus).
    """
    lp_execution_config_page.navigate()

    save_btn = lp_execution_config_page.save_button
    assert save_btn.is_visible(), "Expected Save Config button to be visible."
    assert save_btn.get_attribute("type") == "button"
    assert "Save Config" in save_btn.inner_text()
    assert "btn-primary" in (save_btn.get_attribute("class") or "")

    # Status message span
    status_el = lp_execution_config_page.status_message
    assert status_el.count() >= 1, "Expected #lpExecutionConfigStatus element to exist in DOM."

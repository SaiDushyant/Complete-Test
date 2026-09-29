import json

import pytest
from playwright.sync_api import expect
from urllib.parse import urlsplit
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from workflows.admin_portal.pages.admin_lp_execution_config_page import (
    AdminLpExecutionConfigPage,
)


LP_CONFIG_URL = (
    "https://stage.xtremenext.com/admin/Controlbase/lpExecutionConfig"
)


@pytest.mark.admin
@pytest.mark.regression
def test_lp_config_page_displays_controls(
    admin_lp_execution_config_page: AdminLpExecutionConfigPage,
):
    """Check the real LP Execution Config page and its controls."""
    page = admin_lp_execution_config_page
    page.navigate(LP_CONFIG_URL)

    expect(page.page_title).to_have_text("LP Execution Config")
    expect(page.form).to_be_visible()

    for control in (
        page.enabled,
        page.provider,
        page.order_open_owner,
        page.pending_trigger_owner,
        page.sltp_execution_owner,
        page.pending_cancel_owner,
        page.rest_base_url,
        page.ws_primary_url,
        page.ws_fallback_url,
        page.bridge_api_url,
        page.save_button,
       
    ):
        expect(control).to_be_visible()
        expect(page.status).to_be_attached()

    assert page.provider.locator("option").all_text_contents() == [
        "MatchTrade",
        "FIX Bridge",
        "None",
    ]

    expected_owners = ["Local OMS", "Python to LP", "LP server"]
    for owner_select in (
        page.order_open_owner,
        page.pending_trigger_owner,
        page.sltp_execution_owner,
        page.pending_cancel_owner,
    ):
        assert owner_select.locator("option").all_text_contents() == expected_owners

    for dropdown in (
        page.provider,
        page.order_open_owner,
        page.pending_trigger_owner,
        page.sltp_execution_owner,
        page.pending_cancel_owner,
    ):
        original_value = dropdown.input_value()
        for option in dropdown.locator("option").all():
            value = option.get_attribute("value")
            if value is not None:
                dropdown.select_option(value)
                expect(dropdown).to_have_value(value)
        dropdown.select_option(original_value)

    for url_field in (
        page.rest_base_url,
        page.ws_primary_url,
        page.ws_fallback_url,
        page.bridge_api_url,
    ):
        expect(url_field).to_have_attribute("type", "url")


@pytest.mark.admin
@pytest.mark.regression
def test_lp_config_enabled_switch_can_be_toggled_without_saving(
    admin_lp_execution_config_page: AdminLpExecutionConfigPage,
):
    """Check the enabled switch locally without submitting the form."""
    page = admin_lp_execution_config_page
    page.navigate(LP_CONFIG_URL)

    original_value = page.enabled.is_checked()
    try:
        page.enabled.set_checked(not original_value)
        assert page.enabled.is_checked() is not original_value
    finally:
        page.enabled.set_checked(original_value)

@pytest.mark.admin
@pytest.mark.regression
def test_lp_config_url_fields_validate_without_saving(
    admin_lp_execution_config_page: AdminLpExecutionConfigPage,
):
    """Check URL fields using dummy values without saving configuration."""
    page = admin_lp_execution_config_page
    page.navigate(LP_CONFIG_URL)

    url_fields = (
        page.rest_base_url,
        page.ws_primary_url,
        page.ws_fallback_url,
        page.bridge_api_url,
    )
    original_values = [field.input_value() for field in url_fields]

    try:
        for field in url_fields:
            field.fill("https://example.test/lp")
            expect(field).to_have_value("https://example.test/lp")
            assert field.evaluate("(element) => element.checkValidity()")

            field.fill("not-a-valid-url")
            assert not field.evaluate("(element) => element.checkValidity()")
    finally:
        for field, original_value in zip(url_fields, original_values):
            field.fill(original_value)

@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("mock_status", "mock_body"),
    [
        (
            200,
            '{"status":"success","message":"Mocked LP config response"}',
        ),
        (
            400,
            '{"status":"error","message":"Mocked LP config validation error"}',
        ),
    ],
)
def test_lp_config_save_uses_mock_response(
    admin_lp_execution_config_page: AdminLpExecutionConfigPage,
    mock_status: int,
    mock_body: str,
):
    """Check mocked save responses without changing real LP configuration."""
    page_object = admin_lp_execution_config_page
    page_object.navigate(LP_CONFIG_URL)

    page = page_object.page
    save_path = "/admin/Controlbase/saveLpExecutionConfig"
    intercepted_write_paths = []

    def mock_save_or_block_other_writes(route):
        request = route.request
        path = urlsplit(request.url).path
        method = request.method.upper()

        if method in {"POST", "PUT", "PATCH", "DELETE"}:
            intercepted_write_paths.append(f"{method} {path}")

            if method == "POST" and path.rstrip("/").lower() == save_path.lower():
                route.fulfill(
                    status=mock_status,
                    content_type="application/json",
                    body=mock_body,
                )
            else:
                route.abort()
        else:
            route.continue_()

    page.route("**/*", mock_save_or_block_other_writes)

    try:
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and urlsplit(response.url).path.rstrip("/").lower()
                == save_path.lower()
            ),
            timeout=10_000,
        ) as response_info:
            page_object.save_button.click()
    except PlaywrightTimeoutError:
        pytest.fail(
            "No response from the expected LP save endpoint. "
            f"Write request paths seen: {intercepted_write_paths}"
        )

    response = response_info.value
    assert response.status == mock_status
    assert response.json() == json.loads(mock_body)
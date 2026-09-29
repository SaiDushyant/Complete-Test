import pytest
from playwright.sync_api import expect

from workflows.admin_portal.pages.admin_cron_jobs_page import AdminCronJobsPage


CRON_JOBS_URL = "https://stage.xtremenext.com/admin/Controlbase/cronJobs"


@pytest.mark.admin
@pytest.mark.regression
def test_admin_cron_jobs_page_renders_table_and_columns(
    admin_cron_jobs_page: AdminCronJobsPage,
):
    """Check that the Cron Jobs page displays its table and expected columns."""
    admin_cron_jobs_page.navigate(CRON_JOBS_URL)

    expect(admin_cron_jobs_page.page_title).to_have_text("Cron Jobs")
    expect(admin_cron_jobs_page.table).to_be_visible()
    expect(admin_cron_jobs_page.search_input).to_be_visible()

    expected_headers = [
        "S.No", "Job", "Status", "Schedule", "Options",
        "Next Run", "Last Run", "Last Status", "Action",
    ]
    actual_headers = [
        header.strip()
        for header in admin_cron_jobs_page.table.locator("thead th").all_inner_texts()
    ]

    for header in expected_headers:
        assert header in actual_headers, f"Expected table column '{header}'."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_cron_jobs_modal_displays_fields(
    admin_cron_jobs_page: AdminCronJobsPage,
):
    """Check the edit modal fields without changing any Cron Job settings."""
    admin_cron_jobs_page.navigate(CRON_JOBS_URL)
    admin_cron_jobs_page.open_first_cron_job()

    for locator in (
        admin_cron_jobs_page.modal_title,
        admin_cron_jobs_page.job_name,
        admin_cron_jobs_page.enabled_select,
        admin_cron_jobs_page.schedule_type_select,
        admin_cron_jobs_page.run_time_input,
        admin_cron_jobs_page.timezone_input,
        admin_cron_jobs_page.send_mail_select,
        admin_cron_jobs_page.bbook_enabled_select,
        admin_cron_jobs_page.swap_enabled_select,
        admin_cron_jobs_page.from_email_input,
        admin_cron_jobs_page.from_name_input,
        admin_cron_jobs_page.trigger_mode_select,
        admin_cron_jobs_page.close_button,
        admin_cron_jobs_page.save_button,
    ):
        expect(locator).to_be_visible()


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("status", "response_body"),
    [
        (200, '{"status":"success","message":"Mocked Cron Job response"}'),
        (400, '{"status":"error","message":"Mocked Cron Job validation error"}'),
    ],
)
def test_admin_cron_jobs_save_uses_mock_response(
    admin_cron_jobs_page: AdminCronJobsPage,
    status: int,
    response_body: str,
):
    """Check the mocked Cron Job save response without sending a live save request."""
    admin_cron_jobs_page.navigate(CRON_JOBS_URL)
    admin_cron_jobs_page.open_first_cron_job()

    intercepted_requests = []

    def mock_request(route):
        intercepted_requests.append(route.request.url)
        route.fulfill(
            status=status,
            content_type="application/json",
            body=response_body,
        )

    admin_cron_jobs_page.page.route("**/*", mock_request)
    admin_cron_jobs_page.click_save()

    assert intercepted_requests, "Expected the save action to produce a mocked request."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_cron_jobs_table_controls_and_rows(
    admin_cron_jobs_page: AdminCronJobsPage,
):
    """Check the Cron Jobs table controls, records, and edit actions."""
    admin_cron_jobs_page.navigate(CRON_JOBS_URL)

    entries = admin_cron_jobs_page.page.locator(
        "select[name='datatable_length']"
    )
    expect(entries).to_be_visible()
    assert entries.locator("option").all_text_contents() == [
        "10", "25", "50", "100"
    ]

    rows = admin_cron_jobs_page.table_rows
    expect(rows).to_have_count(4)

    expected_jobs = [
        "Manager Wise Swap",
        "Copy Trading Renewal",
        "IB Commission Queue",
        "Trade Stuck Order Recovery",
    ]
    for job_name in expected_jobs:
        expect(admin_cron_jobs_page.table.get_by_text(job_name, exact=True)).to_be_visible()

    expect(admin_cron_jobs_page.page.locator("#datatable_info")).to_contain_text(
        "Showing 1 to 4 of 4 entries"
    )
    expect(admin_cron_jobs_page.page.locator("#datatable_paginate")).to_be_visible()
    expect(admin_cron_jobs_page.edit_buttons).to_have_count(4)

    admin_cron_jobs_page.search_input.fill("Manager Wise Swap")
    expect(rows).to_have_count(1)

    admin_cron_jobs_page.search_input.clear()
    expect(rows).to_have_count(4)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_cron_jobs_modal_details_and_schedule_visibility(
    admin_cron_jobs_page: AdminCronJobsPage,
):
    """Check modal metadata, validation placeholders, and schedule-dependent fields without saving."""
    admin_cron_jobs_page.navigate(CRON_JOBS_URL)
    admin_cron_jobs_page.open_first_cron_job()

    expect(admin_cron_jobs_page.hidden_id).not_to_have_value("")
    expect(admin_cron_jobs_page.job_key).not_to_have_value("")
    expect(admin_cron_jobs_page.job_name).to_have_attribute("readonly", "")
    expect(admin_cron_jobs_page.interval_input).to_have_attribute("min", "10")
    expect(admin_cron_jobs_page.timezone_input).to_have_attribute(
        "placeholder", "Etc/UTC"
    )
    expect(admin_cron_jobs_page.from_email_input).to_have_attribute("type", "email")
    expect(admin_cron_jobs_page.page.get_by_text(
        "Mailjet keys are configured from production_file only.",
        exact=True,
    )).to_be_visible()

    expect(admin_cron_jobs_page.page.locator(
        "#cronModal .invalid-feedback.run_time"
    )).to_be_hidden()
    expect(admin_cron_jobs_page.page.locator(
        "#cronModal .invalid-feedback.interval_seconds"
    )).to_be_hidden()

    original_schedule = admin_cron_jobs_page.schedule_type_select.input_value()
    try:
        admin_cron_jobs_page.schedule_type_select.select_option("daily")
        expect(admin_cron_jobs_page.run_time_input).to_be_visible()
        expect(admin_cron_jobs_page.interval_input).to_be_hidden()

        admin_cron_jobs_page.schedule_type_select.select_option("interval")
        expect(admin_cron_jobs_page.interval_input).to_be_visible()
        expect(admin_cron_jobs_page.run_time_input).to_be_hidden()
    finally:
        admin_cron_jobs_page.schedule_type_select.select_option(original_schedule)
@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    ("status", "response_body"),
    [
        (200, '{"status":"success","message":"Mocked Cron Job response"}'),
        (400, '{"status":"error","message":"Mocked Cron Job validation error"}'),
    ],
)
def test_admin_cron_jobs_save_uses_mock_response(
    admin_cron_jobs_page: AdminCronJobsPage,
    status: int,
    response_body: str,
):
    """Verify the mocked save response without changing Cron Job data."""
    import json

    admin_cron_jobs_page.navigate(CRON_JOBS_URL)
    admin_cron_jobs_page.open_first_cron_job()

    mocked_requests = []

    def mock_request(route):
        mocked_requests.append(route.request.url)
        route.fulfill(
            status=status,
            content_type="application/json",
            body=response_body,
        )

    page = admin_cron_jobs_page.page
    page.route("**/*", mock_request)

    with page.expect_response(
        lambda response: response.request.method not in {"GET", "HEAD", "OPTIONS"},
        timeout=10_000,
    ) as response_info:
        admin_cron_jobs_page.click_save()

    response = response_info.value
    assert mocked_requests, "Expected the save request to be intercepted."
    assert response.status == status
    assert response.json() == json.loads(response_body)
import re

import pytest

from workflows.admin_portal.pages.admin_dashboard_page import (
    AdminDashboardPage,
)


@pytest.mark.admin
@pytest.mark.regression
def test_admin_dashboard_heading_is_displayed(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the Admin Dashboard heading is displayed."""
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.dashboard_title.first.is_visible()
    assert admin_dashboard_page.dashboard_title.first.inner_text().strip() == (
        "Dashboard"
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_dashboard_main_kpi_cards_are_displayed(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that the main Dashboard KPI cards are displayed."""
    admin_dashboard_page.navigate()

    expected_labels = {
        "total deposit",
        "total withdrawal",
        "pending withdrawal",
        "active user",
        "verified user",
        "total users",
    }

    actual_labels = {
        label.strip().casefold()
        for label in admin_dashboard_page.kpi_labels.all_inner_texts()
    }

    assert expected_labels.issubset(actual_labels), (
        "Expected all main Dashboard KPI labels to be displayed."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_dashboard_kpi_values_are_numeric(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that Dashboard KPI values are numeric."""
    admin_dashboard_page.navigate()

    values = admin_dashboard_page.kpi_values.all_inner_texts()

    assert values, "Expected Dashboard KPI values to be present."

    for value in values:
        normalized_value = value.strip().replace(",", "")

        assert re.fullmatch(
            r"-?\d+(?:\.\d+)?",
            normalized_value,
        ), f"Expected numeric value but found '{value}'."


@pytest.mark.admin
@pytest.mark.regression
def test_admin_dashboard_book_sections_are_displayed(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that A-Book and B-Book sections are displayed."""
    admin_dashboard_page.navigate()

    headings = {
        heading.strip().casefold()
        for heading in admin_dashboard_page.book_headings.all_inner_texts()
    }

    assert {"a-book", "b-book"}.issubset(headings), (
        "Expected both A-Book and B-Book sections to be displayed."
    )


@pytest.mark.admin
@pytest.mark.regression
def test_admin_dashboard_charts_are_rendered(
    admin_dashboard_page: AdminDashboardPage,
):
    """Verify that both Dashboard charts are rendered."""
    admin_dashboard_page.navigate()

    assert admin_dashboard_page.deposit_withdraw_chart.is_visible(), (
        "Expected the Deposits vs Withdrawals chart to be visible."
    )
    assert admin_dashboard_page.book_compare_chart.is_visible(), (
        "Expected the A-Book vs B-Book chart to be visible."
    )

    legends = {
        text.strip().casefold()
        for text in admin_dashboard_page.chart_legend_text.all_inner_texts()
    }

    assert {"deposits", "withdrawals"}.issubset(legends), (
        "Expected Deposits and Withdrawals legends."
    )
    assert {"a-book", "b-book"}.issubset(legends), (
        "Expected A-Book and B-Book legends."
    )
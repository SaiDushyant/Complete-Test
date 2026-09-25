import pytest

from workflows.admin_portal.pages.admin_dashboard_page import (
    AdminDashboardPage,
)


SIDEBAR_TITLES = [
    "Dashboard",
    "Orders",
    "Manage User",
    "Deposit/WDL",
    "Fund Managers",
    "Leads",
    "Manager/Group",
    "Liquidity",
    "Reports/Logs",
    "Payment Gateway",
    "Settings",
    "LP Execution Config",
    "Cron Jobs",
]


@pytest.mark.admin
@pytest.mark.regression
@pytest.mark.parametrize(
    "title",
    SIDEBAR_TITLES,
    ids=SIDEBAR_TITLES,
)
def test_admin_sidebar_title_is_visible(
    admin_dashboard_page: AdminDashboardPage,
    title: str,
):
    """Verify that each top-level sidebar title is visible."""
    admin_dashboard_page.navigate()

    sidebar = admin_dashboard_page.page.locator("#sidebar-menu")

    if not sidebar.is_visible():
        admin_dashboard_page.page.locator(
            "#vertical-menu-btn"
        ).click()

    sidebar.wait_for(state="visible", timeout=5000)

    candidates = sidebar.locator("span[data-key]").filter(
        has_text=title
    )

    for index in range(candidates.count()):
        candidate = candidates.nth(index)

        if candidate.is_visible():
            assert title.casefold() in (
                candidate.inner_text().strip().casefold()
            )
            return

    pytest.fail(
        f"Sidebar title '{title}' was not visible."
    )
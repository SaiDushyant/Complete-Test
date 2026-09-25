"""Client Portal Page Objects."""
from workflows.client_portal.pages.client_dashboard_page import ClientDashboardPage
from workflows.client_portal.pages.client_login_page import ClientLoginPage
from workflows.client_portal.pages.client_refer_earn_page import ClientReferEarnPage
from workflows.client_portal.pages.client_settings_page import ClientSettingsPage
from workflows.client_portal.pages.profile_page import ClientProfilePage

__all__ = [
    "ClientDashboardPage",
    "ClientLoginPage",
    "ClientProfilePage",
    "ClientReferEarnPage",
    "ClientSettingsPage",
]

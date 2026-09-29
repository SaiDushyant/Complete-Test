"""
Client Portal Settings Page Object.
Comprehensive encapsulation of all 4 sub-tabs and controls:
- Personal Information
- Trading Account
- Documents
- Security
Maintained by Developer 3 (Client Portal Owner).
"""

from __future__ import annotations

import re
from typing import List
from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.client_portal.pages.components.client_header import ClientHeaderComponent
from workflows.client_portal.pages.components.client_sidebar import ClientSidebarComponent
from workflows.shared.pages.base_page import BasePage


class ClientSettingsPage(BasePage):
    """Page object for Client Portal account settings and profile updates."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.header = ClientHeaderComponent(page)
        self.sidebar = ClientSidebarComponent(page)

        # Main Page Heading
        self.heading = page.locator("main h1, main h2, main h3").filter(has_text="Account Settings")

        # 4 Sub-Tabs
        self.personal_info_tab = page.locator("main button").filter(has_text="Personal Information").first
        self.trading_account_tab = page.locator("main button").filter(has_text="Trading Account").first
        self.documents_tab = page.locator("main button").filter(has_text="Documents").first
        self.security_tab = page.locator("main button").filter(has_text="Security").first

        # =====================================================================
        # 1. Personal Information Form
        # =====================================================================
        self.personal_info_heading = page.locator("main h2").filter(has_text="Personal Information")
        self.full_name_input = page.locator("main div").filter(has=page.locator("label:has-text('FULL NAME')")).locator("input")
        self.email_input = page.locator("main input[type='email']")
        self.phone_input = page.locator("main input[type='tel']")
        self.address_input = page.locator("main div").filter(has=page.locator("label:has-text('ADDRESS')")).locator("input").first
        self.city_input = page.locator("main div").filter(has=page.locator("label:has-text('CITY')")).locator("input")
        self.state_input = page.locator("main div").filter(has=page.locator("label:has-text('STATE')")).locator("input")
        self.zip_input = page.locator("main div").filter(has=page.locator("label:has-text('ZIP')")).locator("input")
        self.country_input = page.locator("main div").filter(has=page.locator("label:has-text('COUNTRY')")).locator("input")
        self.save_button = page.locator("main button:has-text('SAVE CHANGES')")
        self.cancel_button = page.locator("main button:has-text('Cancel')")

        # =====================================================================
        # 2. Trading Account Settings
        # =====================================================================
        self.trading_account_heading = page.locator("main h2").filter(has_text="Trading Account")
        # Trading controls (comboboxes / selects)
        self.account_select = page.locator("main [role='combobox'], main select").nth(0)
        self.account_type_select = page.locator("main [role='combobox'], main select").nth(1)
        self.leverage_select = page.locator("main [role='combobox'], main select").nth(2)
        self.save_trading_settings_button = page.locator("main button:has-text('SAVE TRADING SETTINGS')")

        # =====================================================================
        # 3. Documents / KYC
        # =====================================================================
        self.documents_heading = page.locator("main h2").filter(has_text="Documents")
        self.document_status_badge = page.locator("main div, main span, main p, main strong").filter(has_text=re.compile(r"Verified|Pending|Under Review|Unverified|Rejected", re.I))
        self.account_status_container = page.locator("main").filter(has_text=re.compile(r"Account Status", re.I))
        self.document_links = page.locator("main a[href*='/info/'], main a:has(img)")
        self.document_cards = page.locator("main div").filter(has_text=re.compile(r"Address Proof|National ID|Bank Statement", re.I))

        # =====================================================================
        # 4. Security / Change Password
        # =====================================================================
        self.security_heading = page.locator("main h2").filter(has_text=re.compile(r"Change Password|Security", re.I))
        self.current_password_input = page.locator("main input[type='password']").nth(0)
        self.new_password_input = page.locator("main input[type='password']").nth(1)
        self.confirm_password_input = page.locator("main input[type='password']").nth(2)
        self.send_otp_button = page.locator("main button").filter(has_text=re.compile(r"Send OTP|Change Password|Update Password", re.I))

    def navigate(self) -> None:
        """Navigate to Client Settings view via sidebar."""
        target_url = f"{settings.client_portal.base_url.rstrip('/')}/client-portal"
        if "/client-portal" not in self.page.url:
            self.goto(target_url)
        self.sidebar.navigate_to_settings()
        expect(self.header.title_heading.first).to_have_text("Settings", timeout=15000)

    def open_subtab(self, tab_name: str) -> None:
        """Switch between Settings sub-tabs and verify header remains consistent."""
        tab_lower = tab_name.lower()
        if "personal" in tab_lower:
            self.personal_info_tab.click()
            expect(self.personal_info_heading.first).to_be_visible(timeout=5000)
        elif "trading" in tab_lower:
            self.trading_account_tab.click()
            expect(self.trading_account_heading.first).to_be_visible(timeout=5000)
        elif "document" in tab_lower:
            self.documents_tab.click()
            expect(self.documents_heading.first).to_be_visible(timeout=5000)
        elif "security" in tab_lower:
            self.security_tab.click()
            expect(self.security_heading.first).to_be_visible(timeout=5000)
        else:
            raise ValueError(f"Unknown settings tab '{tab_name}'")

    def get_uploaded_document_count(self) -> int:
        """Return total count of visible uploaded KYC documents."""
        return self.document_links.count()

    def get_uploaded_document_urls(self) -> List[str]:
        """Return all uploaded KYC document URLs."""
        urls = []
        for i in range(self.document_links.count()):
            href = self.document_links.nth(i).get_attribute("href")
            if href:
                urls.append(href)
        return urls

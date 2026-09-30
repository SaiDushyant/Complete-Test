"""
Mailinator Public Inbox Page Object.
Encapsulates public disposable email lookup, email reception, and link extraction for automated verification flows.
Maintained by Developer 3 (Shared / Client Portal Integrations).
"""

from __future__ import annotations

import time
from typing import List, Optional
from playwright.sync_api import Locator, Page, expect

from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("mailinator_page")


class MailinatorPage(BasePage):
    """
    Page Object Model representing the Mailinator public email client.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.inbox_table: Locator = page.locator("table.table-striped, table")
        self.email_rows: Locator = page.locator("table tbody tr")
        self.msg_iframe_locator = page.frame_locator("#html_msg_body")
        self._current_inbox: Optional[str] = None
        self._current_msg_id: Optional[str] = None

    def open_inbox(self, inbox_name: str) -> None:
        """
        Navigate to a specific Mailinator public inbox by name.
        Example: inbox_name='user_1234' -> https://www.mailinator.com/v4/public/inboxes.jsp?to=user_1234
        """
        self._current_inbox = inbox_name
        url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox_name}"
        logger.info(f"Opening Mailinator inbox UI: {url}")
        self.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_email(
        self,
        inbox_name: str,
        sender_or_subject: str = "XtremeNext",
        timeout_sec: int = 50,
        poll_interval_sec: int = 3,
    ) -> Optional[str]:
        """
        Poll the Mailinator inbox until an email arrives or timeout expires.
        Returns the message ID when found, or None.
        """
        self._current_inbox = inbox_name
        logger.info(f"Waiting for email matching '{sender_or_subject}' in inbox '{inbox_name}' (timeout: {timeout_sec}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout_sec:
            # 1. Check via Mailinator Public API
            try:
                api_res = self.page.request.get(f"https://www.mailinator.com/api/v2/domains/public/inboxes/{inbox_name}")
                if api_res.status == 200:
                    data = api_res.json()
                    msgs = data.get("msgs", [])
                    for m in msgs:
                        m_from = m.get("from", "")
                        m_subj = m.get("subject", "")
                        if (
                            sender_or_subject.lower() in m_from.lower()
                            or sender_or_subject.lower() in m_subj.lower()
                            or "wavex" in m_subj.lower()
                            or "verify" in m_subj.lower()
                        ):
                            msg_id = m.get("id")
                            self._current_msg_id = msg_id
                            logger.info(f"Found matching message in Mailinator API: id='{msg_id}', subject='{m_subj}'")
                            return msg_id
            except Exception as e:
                logger.debug(f"Mailinator API poll error: {e}")

            # 2. Check via UI table rows
            matching_rows = self.page.locator(f"table tbody tr:has-text('{sender_or_subject}')")
            if matching_rows.count() > 0 and matching_rows.first.is_visible():
                logger.info("Matching email found in Mailinator UI table!")
                self._current_msg_id = "ui_visible"
                return "ui_visible"

            self.page.wait_for_timeout(poll_interval_sec * 1000)

        logger.warning(f"Timeout waiting for email matching '{sender_or_subject}' in inbox '{inbox_name}'.")
        return None

    def open_email(self, inbox_name: str, msg_id: Optional[str] = None, sender_or_subject: str = "XtremeNext") -> None:
        """Open the email message view."""
        self._current_inbox = inbox_name
        if msg_id:
            self._current_msg_id = msg_id

        actual_msg_id = msg_id or self._current_msg_id

        if actual_msg_id and actual_msg_id != "ui_visible":
            msg_url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox_name}&msgid={actual_msg_id}"
            logger.info(f"Navigating to message view: {msg_url}")
            self.goto(msg_url)
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)
        else:
            row = self.page.locator(f"table tbody tr:has-text('{sender_or_subject}')").first
            expect(row).to_be_visible(timeout=10000)
            logger.info(f"Clicking email row in UI: {row.inner_text().strip()}")
            row.click()
            self.page.wait_for_timeout(3000)

    @staticmethod
    def _is_verification_link(url: str) -> bool:
        """Helper to determine if a URL points to email verification."""
        import base64
        if not url:
            return False
        
        lowered = url.lower()
        if "verify_user.php" in lowered or ("stage.xtremenext.com/verify" in lowered and "secret" in lowered):
            return True

        if "mjt.lu" in lowered:
            parts = url.rstrip("/").split("/")
            for seg in [parts[-1]] + parts:
                try:
                    padded = seg + "=" * ((4 - len(seg) % 4) % 4)
                    decoded = base64.urlsafe_b64decode(padded.encode()).decode("utf-8", errors="ignore")
                    if "verify" in decoded.lower() or "verify_user" in decoded.lower():
                        return True
                except Exception:
                    pass

        return False

    def extract_verification_link(
        self,
        inbox_name: Optional[str] = None,
        msg_id: Optional[str] = None,
        timeout_sec: int = 15,
    ) -> Optional[str]:
        """
        Extract the registration verification URL from the email message body.
        Attempts both direct API inspection and UI DOM/iframe analysis.
        """
        import re

        inbox = inbox_name or self._current_inbox
        msg = msg_id or self._current_msg_id

        # Strategy 1: Extract directly via Mailinator public API message details
        if inbox and msg and msg != "ui_visible":
            try:
                api_url = f"https://www.mailinator.com/api/v2/domains/public/inboxes/{inbox}/messages/{msg}"
                logger.info(f"Querying Mailinator API for message parts: {api_url}")
                res = self.page.request.get(api_url)
                if res.status == 200:
                    data = res.json()
                    parts = data.get("parts", [])
                    for part in parts:
                        body = part.get("body", "")
                        raw_links = re.findall(r'href=["\'](http[^"\']+)["\']', body)
                        for href in raw_links:
                            if self._is_verification_link(href):
                                logger.info(f"Successfully extracted verification link via API: {href}")
                                return href
            except Exception as e:
                logger.debug(f"API link extraction error: {e}")

        # Strategy 2: Extract via UI (iframe & LINKS tab)
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            # Check LINKS tab in Mailinator UI
            try:
                links_tab = self.page.locator("a:has-text('LINKS'), #pills-links-tab, button:has-text('LINKS')").first
                if links_tab.is_visible():
                    links_tab.click()
                    self.page.wait_for_timeout(500)
                    tab_links = self.page.locator("#pills-links a, .tab-pane.active a").all()
                    for tl in tab_links:
                        href = tl.get_attribute("href") or ""
                        if self._is_verification_link(href):
                            logger.info(f"Identified verification link from LINKS tab: {href}")
                            return href
            except Exception:
                pass

            # Check iframe #html_msg_body
            frame = self.page.frame(name="html_msg_body")
            links: List[Locator] = []

            if frame:
                try:
                    frame.locator("body").wait_for(timeout=2000)
                    links = frame.locator("a").all()
                except Exception:
                    pass
            else:
                try:
                    links = self.msg_iframe_locator.locator("a").all()
                except Exception:
                    pass

            for link in links:
                try:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    if "complete registration" in text.lower():
                        logger.info(f"Identified verification link from button text: {href}")
                        return href
                    if self._is_verification_link(href):
                        logger.info(f"Identified verification link from link attribute: {href}")
                        return href
                except Exception:
                    pass

            self.page.wait_for_timeout(1000)

        return None


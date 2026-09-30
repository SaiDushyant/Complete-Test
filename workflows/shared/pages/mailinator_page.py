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

    def open_inbox(self, inbox_name: str) -> None:
        """
        Navigate to a specific Mailinator public inbox by name.
        Example: inbox_name='user_1234' -> https://www.mailinator.com/v4/public/inboxes.jsp?to=user_1234
        """
        url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox_name}"
        logger.info(f"Opening Mailinator inbox UI: {url}")
        self.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def wait_for_email(
        self,
        inbox_name: str,
        sender_or_subject: str = "XtremeNext",
        timeout_sec: int = 45,
        poll_interval_sec: int = 3,
    ) -> Optional[str]:
        """
        Poll the Mailinator inbox until an email arrives or timeout expires.
        Returns the message ID when found, or None.
        """
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
                            logger.info(f"Found matching message in Mailinator API: id='{msg_id}', subject='{m_subj}'")
                            return msg_id
            except Exception as e:
                logger.debug(f"Mailinator API poll error: {e}")

            # 2. Check via UI table rows
            matching_rows = self.page.locator(f"table tbody tr:has-text('{sender_or_subject}')")
            if matching_rows.count() > 0 and matching_rows.first.is_visible():
                logger.info(f"Matching email found in Mailinator UI table!")
                return "ui_visible"

            self.page.wait_for_timeout(poll_interval_sec * 1000)

        logger.warning(f"Timeout waiting for email matching '{sender_or_subject}' in inbox '{inbox_name}'.")
        return None

    def open_email(self, inbox_name: str, msg_id: Optional[str] = None, sender_or_subject: str = "XtremeNext") -> None:
        """Open the email message view."""
        if msg_id and msg_id != "ui_visible":
            msg_url = f"https://www.mailinator.com/v4/public/inboxes.jsp?to={inbox_name}&msgid={msg_id}"
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

    def extract_verification_link(self, timeout_sec: int = 15) -> Optional[str]:
        """
        Extract the registration verification URL from the email message body iframe.
        """
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            frame = self.page.frame(name="html_msg_body")
            links: List[Locator] = []

            if frame:
                try:
                    frame.locator("body").wait_for(timeout=3000)
                    links = frame.locator("a").all()
                except Exception:
                    pass
            else:
                try:
                    links = self.msg_iframe_locator.locator("a").all()
                except Exception:
                    pass

            logger.info(f"Scanning {len(links)} links inside email body...")
            # First pass: look specifically for button with text 'complete registration' or 'confirm' or 'verify'
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip()
                    logger.info(f"  Email Link found: text='{text}', href='{href}'")

                    if href and (
                        "complete registration" in text.lower()
                        or "confirm your email" in text.lower()
                        or "verify your email" in text.lower()
                        or "verify_user.php" in href.lower()
                    ):
                        logger.info(f"Identified verification link (text/target match): {href}")
                        return href
                except Exception:
                    pass

            # Second pass: check base64 encoded mjt.lu targets for verify_user
            for link in links:
                try:
                    href = link.get_attribute("href") or ""
                    if "mjt.lu" in href:
                        import base64
                        parts = href.rstrip("/").split("/")
                        last_part = parts[-1]
                        try:
                            padded = last_part + "=" * ((4 - len(last_part) % 4) % 4)
                            decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
                            if "verify" in decoded.lower():
                                logger.info(f"Identified verification link from decoded payload: {href}")
                                return href
                        except Exception:
                            pass
                except Exception:
                    pass

            self.page.wait_for_timeout(1000)

        return None

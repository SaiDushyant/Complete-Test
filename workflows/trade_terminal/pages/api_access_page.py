"""
Trade Terminal API Access Page Object.
Encapsulates all elements and user interactions on the API Access page:
  Page container: div.page[data-page="api"]
  JS path: document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(2)")
  Unique wrapper: div.api-access-page
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, Optional
from pathlib import Path

from playwright.sync_api import Download, Locator, Page, expect

from config.settings import settings
from workflows.shared.pages.base_page import BasePage
from workflows.shared.utils.logger import get_logger

logger = get_logger("api_access_page")
TIMEOUT_DEFAULT = 15000


class ApiAccessPage(BasePage):
    """
    Page Object for the Trade Terminal API Access page.
    Contains:
      - YOUR API SECRET section  (#apiSecretText, copy button)
      - YOUR API LINK section    (#apitext readonly input, copy button)
      - QUICK START guide        (ol.api-steps, 5 numbered steps)
      - SYMBOLS REFERENCE card   (#csvbtn download link)
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # ── Navigation & Container ────────────────────────────────────────────
        # The API icon in the left sidebar (data-nav='api')
        self.api_nav_icon: Locator = page.locator(
            ".leftlist .lefticons[data-nav='api'], "
            ".lefticons[data-tooltip='API'], "
            ".lefticons[data-nav='api']"
        ).first
        # Page container (div.page with data-page="api")
        self.api_page_container: Locator = page.locator("div.page[data-page='api']")
        # Inner unique wrapper
        self.api_access_wrapper: Locator = page.locator("div.api-access-page")

        # ── Hero / Header ─────────────────────────────────────────────────────
        self.api_hero: Locator = self.api_access_wrapper.locator("div.api-hero")
        self.api_hero_heading: Locator = self.api_hero.locator("h3")
        self.api_hero_subtitle: Locator = self.api_hero.locator("p")

        # ── API Secret Card ───────────────────────────────────────────────────
        # code#apiSecretText holds the actual token value
        self.api_secret_text: Locator = page.locator("#apiSecretText")
        # Copy button for the token: data-copy-target="#apiSecretText"
        self.api_secret_copy_btn: Locator = page.locator(
            "button.api-copy-btn[data-copy-target='#apiSecretText']"
        )

        # ── API Link Card ─────────────────────────────────────────────────────
        # input#apitext is a readonly field containing the full API URL
        self.api_link_input: Locator = page.locator("#apitext")
        # Copy button for the link: data-copy-target="#apitext"
        self.api_link_copy_btn: Locator = page.locator(
            "button.api-copy-btn[data-copy-target='#apitext']"
        )
        # The url field container
        self.api_field_url: Locator = page.locator("div.api-field.api-field-url")

        # ── Quick Start Guide ─────────────────────────────────────────────────
        self.quick_start_steps: Locator = page.locator("ol.api-steps")
        self.quick_start_step_items: Locator = self.quick_start_steps.locator("li")

        # ── Symbols Reference / CSV Download ─────────────────────────────────
        self.symbols_resource_card: Locator = page.locator("div.api-card.api-resource-card")
        self.symbols_resource_text: Locator = page.locator("div.api-resource-text")
        self.csv_download_btn: Locator = page.locator("#csvbtn")

    # =========================================================================
    # Navigation & Activation
    # =========================================================================

    def navigate_to_api_page(self, url: Optional[str] = None) -> None:
        """
        Navigate to the dashboard and activate the API Access page
        via the left sidebar icon (data-nav='api').
        The API page is reached either directly through a left-nav item
        or via the 'More Settings' submenu — the DOM has data-nav='api'
        in both paths, so we attempt the direct icon first.
        """
        if "/dashboard" not in self.page.url:
            target_url = url or f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
            logger.info(f"Navigating to Trade Terminal dashboard: {target_url}")
            self.goto(target_url)
            self.page.wait_for_timeout(1000)

        self._dismiss_disclaimer_if_present()

        if not self.is_api_page_active():
            logger.info("Activating API Access page via sidebar icon [data-nav='api']...")
            # Use JS to click all matching data-nav='api' links (handles submenu items)
            self.page.evaluate("""() => {
                const el = document.querySelector(
                    ".lefticons[data-nav='api'], [data-nav='api']"
                );
                if (el) el.click();
            }""")
            self.page.wait_for_timeout(1200)

        expect(self.api_access_wrapper).to_be_visible(timeout=TIMEOUT_DEFAULT)
        self._dismiss_disclaimer_if_present()

    def is_api_page_active(self) -> bool:
        """Return True if the API page container is visible and not hidden."""
        if not self.api_access_wrapper.is_visible():
            return False
        classes = self.api_page_container.get_attribute("class") or ""
        return "hidden" not in classes.split()

    def _dismiss_disclaimer_if_present(self) -> None:
        """Dismiss One Click Trading disclaimer modal and backdrop if present."""
        try:
            self.page.evaluate("""() => {
                const modal = document.querySelector("#disclaimer");
                if (modal && (modal.classList.contains("show") ||
                    window.getComputedStyle(modal).display !== "none")) {
                    const btn = modal.querySelector("#acceptButton") ||
                                modal.querySelector("#close-disclaimer") ||
                                modal.querySelector(".close");
                    if (btn) btn.click();
                    modal.style.display = "none";
                    modal.classList.remove("show");
                    document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
                    document.body.classList.remove("modal-open");
                }
            }""")
            self.page.wait_for_timeout(200)
        except Exception:
            pass

    # =========================================================================
    # API Secret Token
    # =========================================================================

    def get_api_secret_token(self) -> str:
        """
        Return the raw text of the API secret token from #apiSecretText.
        The token is injected by inline JS from localStorage['token'].
        """
        expect(self.api_secret_text).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.api_secret_text.inner_text().strip()

    def click_copy_secret(self) -> str:
        """
        Click the Copy button for the API Secret, then return the
        token text that was (or should have been) copied.
        """
        token = self.get_api_secret_token()
        logger.info(f"Clicking Copy for API Secret token: '{token}'")
        expect(self.api_secret_copy_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        assert self.api_secret_copy_btn.is_enabled(), "Expected API Secret Copy button to be enabled"
        self.api_secret_copy_btn.click()
        self.page.wait_for_timeout(500)
        return token

    def get_clipboard_text(self) -> str:
        """
        Read text from the system clipboard via JS (works in Chromium
        headless / headed when the Clipboard API is available).
        Falls back to empty string if clipboard access is denied.
        """
        try:
            return self.page.evaluate("() => navigator.clipboard.readText()")
        except Exception:
            return ""

    # =========================================================================
    # API Link URL
    # =========================================================================

    def get_api_link_url(self) -> str:
        """
        Return the full API link URL from the readonly #apitext input.
        The URL is built by inline JS and contains the real token and fingerprint.
        """
        expect(self.api_link_input).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.api_link_input.input_value().strip()

    def click_copy_link(self) -> str:
        """
        Click the Copy button for the API Link, then return the URL value.
        """
        link_url = self.get_api_link_url()
        logger.info(f"Clicking Copy for API Link URL (length {len(link_url)})")
        expect(self.api_link_copy_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        assert self.api_link_copy_btn.is_enabled(), "Expected API Link Copy button to be enabled"
        self.api_link_copy_btn.click()
        self.page.wait_for_timeout(500)
        return link_url

    def get_api_link_url_parsed(self) -> Dict[str, str]:
        """
        Parse the API link URL and return its query-string parameters
        as a dict: {type, bs, lot, sl, target, symbol, token, fingerprint, ...}
        """
        raw = self.get_api_link_url()
        params: Dict[str, str] = {}
        if "?" in raw:
            qs = raw.split("?", 1)[1]
            for pair in qs.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
        return params

    # =========================================================================
    # Place Order via API Link
    # =========================================================================

    def place_order_via_api_link(
        self,
        symbol: str | None = None,
        side: str = "buy",
        lot: float = 0.01,
        sl: int = 0,
        target: int = 0,
    ) -> Dict[str, Any]:
        """
        Build a live placeorder URL from the template in #apitext, substitute
        XXXXXXXXXX with the real token from #apiSecretText, override
        symbol/lot/side/sl/target, open the URL in a new tab, and return
        the JSON response body.

        The #apitext input is intentionally a TEMPLATE — its token field reads
        'XXXXXXXXXX' (so users know to replace it). We read the live token from
        #apiSecretText and inject it before firing the request.

        Returns:
            dict with 'url' (the constructed URL) and 'response_text'
            (raw body of the API response — typically JSON).
        """
        import urllib.parse

        raw_url = self.get_api_link_url()
        assert "placeorder" in raw_url, (
            f"Expected API link URL to contain 'placeorder', got: '{raw_url[:100]}'"
        )

        # Get the REAL token from #apiSecretText (not from the URL template)
        real_token = self.get_api_secret_token()
        assert len(real_token) > 0 and real_token != "XXXXX", (
            f"Real API token from #apiSecretText is empty or placeholder: '{real_token}'"
        )

        # Parse URL into components
        parsed = urllib.parse.urlparse(raw_url)
        qs_dict = dict(urllib.parse.parse_qsl(parsed.query))

        # Substitute the live token (replaces XXXXXXXXXX placeholder)
        qs_dict["token"] = real_token

        # Override order parameters
        qs_dict["bs"] = side.lower()
        qs_dict["lot"] = str(lot)
        qs_dict["sl"] = str(sl)
        qs_dict["target"] = str(target)
        qs_dict["clicked"] = "yes"

        # Symbol: if None, keep whatever the template already has (e.g. X:BTCUSD).
        # If explicitly supplied, add X: prefix only when the caller omitted it.
        if symbol is not None:
            qs_dict["symbol"] = symbol if ":" in symbol else f"X:{symbol}"

        # Encode query string — safe=':' preserves the colon in X:EURUSD
        new_qs = urllib.parse.urlencode(qs_dict, quote_via=urllib.parse.quote, safe=":")
        order_url = urllib.parse.urlunparse(parsed._replace(query=new_qs))

        logger.info(f"Placing order via API URL (token injected): {order_url}")

        # Open a new tab so the dashboard page stays intact
        new_page = self.page.context.new_page()
        response_text = ""
        try:
            new_page.goto(order_url, timeout=20000)
            new_page.wait_for_timeout(2000)
            response_text = new_page.locator("body").inner_text().strip()
            logger.info(f"API order response: {response_text[:300]}")
        finally:
            new_page.close()

        return {
            "url": order_url,
            "response_text": response_text,
        }


    # =========================================================================
    # Quick Start Guide
    # =========================================================================

    def get_quick_start_step_count(self) -> int:
        """Return the number of <li> items in the ol.api-steps list."""
        expect(self.quick_start_steps).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.quick_start_step_items.count()

    def get_quick_start_steps_text(self) -> list[str]:
        """Return a list of step text strings from the Quick Start numbered list."""
        count = self.get_quick_start_step_count()
        return [
            self.quick_start_step_items.nth(i).inner_text().strip()
            for i in range(count)
        ]

    # =========================================================================
    # Symbols CSV Download
    # =========================================================================

    def get_csv_download_href(self) -> str:
        """Return the href attribute of the #csvbtn download anchor."""
        expect(self.csv_download_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        return self.csv_download_btn.get_attribute("href") or ""

    def download_symbols_csv(self, timeout: int = 20000) -> Download:
        """
        Click the 'Symbols with Sector' download button and capture the
        file download event. Returns the Playwright Download object so
        callers can save or inspect it.
        """
        logger.info("Initiating 'Symbols with Sector' CSV download...")
        expect(self.csv_download_btn).to_be_visible(timeout=TIMEOUT_DEFAULT)
        assert self.csv_download_btn.is_enabled(), "Expected CSV download button to be enabled"

        with self.page.expect_download(timeout=timeout) as dl_info:
            self.csv_download_btn.click()

        download = dl_info.value
        logger.info(
            f"Download triggered: suggested_filename='{download.suggested_filename}'"
        )
        return download

"""
Base Page Object Model Class.
Serves as the foundation for all portal page objects (Trade Terminal, Admin, Client).
Wraps Playwright Page interactions with built-in logging, dynamic waiting,
and consistent error handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from playwright.sync_api import Locator, Page, expect

from config.settings import settings
from workflows.shared.constants.timeouts import (
    TIMEOUT_DEFAULT,
    TIMEOUT_NETWORK_IDLE,
    TIMEOUT_PAGE_LOAD,
    TIMEOUT_SHORT,
)
from workflows.shared.utils.diagnostics import PageDiagnostics
from workflows.shared.utils.logger import get_logger
from workflows.shared.utils.screenshot import capture_screenshot

logger = get_logger("base_page")


class BasePage:
    """
    Core Page Object Model foundation.
    Provides encapsulated, resilient Playwright interactions.
    """

    def __init__(self, page: Page):
        self.page = page
        if not hasattr(page, "_diagnostics"):
            page._diagnostics = PageDiagnostics(page)

    @property
    def diagnostics(self) -> PageDiagnostics:
        """Access the runtime error diagnostics monitor for this page."""
        if not hasattr(self.page, "_diagnostics"):
            self.page._diagnostics = PageDiagnostics(self.page)
        return self.page._diagnostics

    def assert_no_javascript_errors(self) -> None:
        """Assert that zero unhandled JavaScript runtime exceptions occurred."""
        self.diagnostics.assert_no_javascript_errors()

    def assert_no_console_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert that zero console.error calls were issued on page."""
        self.diagnostics.assert_no_console_errors(ignored_patterns=ignored_patterns)

    def assert_no_failed_network_requests(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert that zero network requests failed or aborted."""
        self.diagnostics.assert_no_failed_requests(ignored_patterns=ignored_patterns)

    def assert_no_http_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert that zero HTTP 4xx/5xx responses were received."""
        self.diagnostics.assert_no_http_errors(ignored_patterns=ignored_patterns)

    def assert_clean_runtime(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert that JavaScript, console, and network requests are all error-free."""
        self.diagnostics.assert_clean_diagnostics(ignored_patterns=ignored_patterns)

    # =========================================================================
    # Navigation & URL Properties
    # =========================================================================

    def goto(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: int = TIMEOUT_PAGE_LOAD,
    ) -> None:
        """Navigate to a target URL with resilient retry on transient timeouts."""
        logger.info(f"Navigating to: {url} (wait_until={wait_until})")
        for attempt in range(2):
            try:
                self.page.goto(url, wait_until=wait_until, timeout=timeout)
                return
            except Exception as e:
                err_str = str(e).lower()
                if attempt == 0 and ("timeout" in err_str or "net::" in err_str):
                    logger.warning(f"Navigation timed out on {url}, retrying once: {e}")
                    self.page.wait_for_timeout(1000)
                    continue
                raise


    @property
    def current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    @property
    def title(self) -> str:
        """Get the current page document title."""
        return self.page.title()

    def wait_for_url(self, pattern: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Wait until page URL matches the specified glob or regex pattern."""
        logger.info(f"Waiting for URL pattern: {pattern}")
        self.page.wait_for_url(pattern, timeout=timeout)

    def reload(self, wait_until: str = "domcontentloaded") -> None:
        """Reload the current page."""
        logger.info("Reloading page")
        self.page.reload(wait_until=wait_until)

    # =========================================================================
    # Element Locators & Waiting
    # =========================================================================

    def locator(self, selector: str) -> Locator:
        """Return a Playwright Locator for the given selector."""
        return self.page.locator(selector)

    def wait_for_element(
        self,
        selector: str,
        state: str = "visible",
        timeout: int = TIMEOUT_DEFAULT,
    ) -> Locator:
        """
        Wait for an element to reach the specified state ('visible', 'attached', 'hidden', 'detached').
        Returns the Locator.
        """
        loc = self.page.locator(selector).first
        loc.wait_for(state=state, timeout=timeout)
        return loc

    # =========================================================================
    # User Interactions
    # =========================================================================

    def click(
        self,
        selector: str,
        timeout: int = TIMEOUT_DEFAULT,
        force: bool = False,
    ) -> None:
        """Click an element after ensuring visibility and clickability."""
        logger.debug(f"Clicking selector: {selector}")
        self.page.locator(selector).first.click(timeout=timeout, force=force)

    def fill(
        self,
        selector: str,
        text: str,
        timeout: int = TIMEOUT_DEFAULT,
    ) -> None:
        """Fill an input or textarea with text."""
        logger.debug(f"Filling selector: {selector}")
        self.page.locator(selector).first.fill(text, timeout=timeout)

    def clear_and_fill(
        self,
        selector: str,
        text: str,
        timeout: int = TIMEOUT_DEFAULT,
    ) -> None:
        """Clear an existing field and fill with new text."""
        loc = self.page.locator(selector).first
        loc.clear(timeout=timeout)
        loc.fill(text, timeout=timeout)

    def check(self, selector: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Check a checkbox or radio button."""
        self.page.locator(selector).first.check(timeout=timeout)

    def uncheck(self, selector: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Uncheck a checkbox."""
        self.page.locator(selector).first.uncheck(timeout=timeout)

    def select_option(
        self,
        selector: str,
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
        timeout: int = TIMEOUT_DEFAULT,
    ) -> List[str]:
        """Select option from a <select> element by value, label, or index."""
        loc = self.page.locator(selector).first
        if value is not None:
            return loc.select_option(value=value, timeout=timeout)
        if label is not None:
            return loc.select_option(label=label, timeout=timeout)
        if index is not None:
            return loc.select_option(index=index, timeout=timeout)
        raise ValueError("Must provide value, label, or index to select_option")

    # =========================================================================
    # State Inspection & Queries
    # =========================================================================

    def get_text(self, selector: str, timeout: int = TIMEOUT_SHORT) -> str:
        """Retrieve inner text from an element."""
        return self.page.locator(selector).first.inner_text(timeout=timeout).strip()

    def get_input_value(self, selector: str, timeout: int = TIMEOUT_SHORT) -> str:
        """Retrieve value from an input or textarea."""
        return self.page.locator(selector).first.input_value(timeout=timeout)

    def get_attribute(
        self,
        selector: str,
        attribute_name: str,
        timeout: int = TIMEOUT_SHORT,
    ) -> Optional[str]:
        """Retrieve the value of a specific attribute."""
        return self.page.locator(selector).first.get_attribute(attribute_name, timeout=timeout)

    def is_visible(self, selector: str, timeout: int = TIMEOUT_SHORT) -> bool:
        """Check if an element is currently visible."""
        try:
            return self.page.locator(selector).first.is_visible(timeout=timeout)
        except Exception:
            return False

    def is_enabled(self, selector: str, timeout: int = TIMEOUT_SHORT) -> bool:
        """Check if an element is enabled."""
        try:
            return self.page.locator(selector).first.is_enabled(timeout=timeout)
        except Exception:
            return False

    def is_checked(self, selector: str, timeout: int = TIMEOUT_SHORT) -> bool:
        """Check if a checkbox or radio element is checked."""
        try:
            return self.page.locator(selector).first.is_checked(timeout=timeout)
        except Exception:
            return False

    def element_count(self, selector: str) -> int:
        """Return the count of elements matching selector."""
        return self.page.locator(selector).count()

    # =========================================================================
    # Fluent Expect Assertions
    # =========================================================================

    def expect_visible(self, selector: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Assert that the element is visible on page."""
        expect(self.page.locator(selector).first).to_be_visible(timeout=timeout)

    def expect_hidden(self, selector: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Assert that the element is hidden or detached."""
        expect(self.page.locator(selector).first).to_be_hidden(timeout=timeout)

    def expect_text_contains(self, selector: str, expected_text: str, timeout: int = TIMEOUT_DEFAULT) -> None:
        """Assert that the element text contains expected string."""
        expect(self.page.locator(selector).first).to_contain_text(expected_text, timeout=timeout)

    # =========================================================================
    # Synchronization & Screenshots
    # =========================================================================

    def wait_for_network_idle(self, timeout: int = TIMEOUT_NETWORK_IDLE) -> None:
        """Wait for network to become idle."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"Network idle wait timed out ({timeout}ms): {e}")

    def take_screenshot(self, name: str, full_page: bool = True) -> Path:
        """Capture a named screenshot."""
        return capture_screenshot(self.page, test_name=name, suffix="manual", full_page=full_page)

    # =========================================================================
    # Runtime Diagnostics & Invisible Error Assertions
    # =========================================================================

    @property
    def diagnostics(self) -> PageDiagnostics:
        """
        Return the PageDiagnostics monitor tracking JS errors, console logs,
        and network failures on this page.
        """
        diag = getattr(self.page, "_diagnostics", None)
        if diag is None:
            diag = PageDiagnostics(self.page)
            self.page._diagnostics = diag
        return diag

    def assert_no_javascript_errors(self) -> None:
        """Assert zero unhandled JavaScript runtime exceptions occurred on this page."""
        self.diagnostics.assert_no_javascript_errors()

    def assert_no_console_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert zero console.error logs were emitted, excluding optional allowed patterns."""
        self.diagnostics.assert_no_console_errors(ignored_patterns=ignored_patterns)

    def assert_no_failed_network_requests(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert zero network requests failed or dropped (DNS, aborted, refused)."""
        self.diagnostics.assert_no_failed_requests(ignored_patterns=ignored_patterns)

    def assert_no_http_errors(self, ignored_patterns: Optional[List[str]] = None) -> None:
        """Assert zero network responses returned HTTP 4xx or 5xx status codes."""
        self.diagnostics.assert_no_http_errors(ignored_patterns=ignored_patterns)

    def assert_clean_diagnostics(
        self,
        check_js_errors: bool = True,
        check_console_errors: bool = True,
        check_failed_requests: bool = True,
        check_http_errors: bool = True,
        ignored_patterns: Optional[List[str]] = None,
    ) -> None:
        """
        Assert all unseen runtime layers (JS errors, console errors, failed requests, HTTP 4xx/5xx)
        are completely clean and free of errors.
        """
        if check_js_errors:
            self.assert_no_javascript_errors()
        if check_console_errors:
            self.assert_no_console_errors(ignored_patterns=ignored_patterns)
        if check_failed_requests:
            self.assert_no_failed_network_requests(ignored_patterns=ignored_patterns)
        if check_http_errors:
            self.assert_no_http_errors(ignored_patterns=ignored_patterns)

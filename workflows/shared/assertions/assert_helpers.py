"""
Custom Assertion Helpers for Behavioral Workflow Tests.
Provides human-readable, actionable failure messages when expectations fail.
"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Locator, Page, expect

from workflows.shared.constants.timeouts import TIMEOUT_DEFAULT


def assert_element_is_visible(
    locator: Locator,
    element_name: str = "Element",
    timeout: int = TIMEOUT_DEFAULT,
) -> None:
    """
    Assert that the locator resolves to a visible DOM element.
    """
    try:
        expect(locator).to_be_visible(timeout=timeout)
    except AssertionError as e:
        raise AssertionError(f"Expected {element_name} to be visible, but it was not. Details: {e}") from e


def assert_element_has_text(
    locator: Locator,
    expected_text: str,
    element_name: str = "Element",
    timeout: int = TIMEOUT_DEFAULT,
) -> None:
    """
    Assert that the locator contains expected text.
    """
    try:
        expect(locator).to_contain_text(expected_text, timeout=timeout)
    except AssertionError as e:
        actual_text = locator.inner_text() if locator.is_visible() else "<hidden or missing>"
        raise AssertionError(
            f"Expected {element_name} to contain '{expected_text}', but found '{actual_text}'."
        ) from e


def assert_url_contains(
    page: Page,
    expected_substring: str,
    timeout: int = TIMEOUT_DEFAULT,
) -> None:
    """
    Assert that current page URL contains the expected substring.
    """
    current_url = page.url
    if expected_substring not in current_url:
        # Wait briefly for client-side navigation to settle
        try:
            page.wait_for_url(f"**{expected_substring}**", timeout=timeout)
        except Exception:
            raise AssertionError(
                f"Expected URL to contain '{expected_substring}', but current URL is '{page.url}'."
            )


def assert_field_value_equals(
    locator: Locator,
    expected_value: str,
    field_name: str = "Field",
    timeout: int = TIMEOUT_DEFAULT,
) -> None:
    """
    Assert that an input field value equals expected string.
    """
    try:
        expect(locator).to_have_value(expected_value, timeout=timeout)
    except AssertionError as e:
        actual_value = locator.input_value()
        raise AssertionError(
            f"Expected {field_name} value to be '{expected_value}', but found '{actual_value}'."
        ) from e

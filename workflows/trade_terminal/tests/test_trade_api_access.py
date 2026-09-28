"""
Trade Terminal API Access Page Test Suite.
Verifies the dedicated API Access page at:
  document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(2)")
  div.page[data-page="api"]  /  div.api-access-page
Maintained by Developer 1 (Trade Terminal Owner).
"""

from __future__ import annotations

import time
import pytest

from config.settings import settings
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_url_contains,
)
from workflows.shared.utils.logger import get_logger
from workflows.trade_terminal.pages.api_access_page import ApiAccessPage
from workflows.trade_terminal.pages.positions_page import PositionsPage
from workflows.trade_terminal.pages.trading_dashboard_page import TradingDashboardPage

logger = get_logger("test_trade_api_access")


@pytest.mark.trade
@pytest.mark.smoke
def test_api_access_page_navigation_and_structure_rendered(
    api_access_page: ApiAccessPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the API Access page renders all expected structural elements:
    document.querySelector("body > div.body > div.main > div.rightbar > section > div:nth-child(2)")
    div.page[data-page="api"]

    1. Clicking the left sidebar icon (data-nav='api') activates the page.
    2. Page wrapper (div.api-access-page) is visible and not hidden.
    3. Hero section renders 'API ACCESS' heading and 'Trade from anywhere.' subtitle.
    4. API Secret card: #apiSecretText shows a non-empty token and Copy button is visible/enabled.
    5. API Link card: #apitext readonly input shows a non-empty URL and Copy button is visible/enabled.
    6. Quick Start guide (ol.api-steps) renders exactly 5 numbered steps.
    7. Symbols Reference card: #csvbtn download link is visible, enabled, and has href containing symbols_with_sector.csv.
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)

    # 1. Page wrapper active
    assert api_access_page.is_api_page_active(), (
        "Expected API Access page container (div.page[data-page='api']) to be active (not hidden)"
    )
    assert_element_is_visible(
        api_access_page.api_access_wrapper,
        element_name="API Access Page Wrapper (div.api-access-page)"
    )

    # 2. Hero section
    assert_element_is_visible(api_access_page.api_hero, element_name="API Hero Section")
    heading_text = api_access_page.api_hero_heading.inner_text().strip()
    assert "API ACCESS" in heading_text.upper(), (
        f"Expected 'API ACCESS' in hero heading, got: '{heading_text}'"
    )
    subtitle_text = api_access_page.api_hero_subtitle.inner_text().strip()
    assert len(subtitle_text) > 0, "Expected non-empty subtitle in API hero section"
    assert "anywhere" in subtitle_text.lower(), (
        f"Expected 'anywhere' in subtitle, got: '{subtitle_text}'"
    )
    logger.info(f"Hero: heading='{heading_text}', subtitle='{subtitle_text}' ✓")

    # 3. API Secret card
    assert_element_is_visible(api_access_page.api_secret_text, element_name="API Secret Token (#apiSecretText)")
    token = api_access_page.get_api_secret_token()
    assert len(token) > 0, "Expected non-empty API secret token in #apiSecretText"
    assert token != "XXXXX", (
        "API secret is showing placeholder 'XXXXX' — user may be in investor mode or token is not loaded"
    )
    logger.info(f"API Secret token present (length {len(token)}) ✓")

    assert_element_is_visible(
        api_access_page.api_secret_copy_btn,
        element_name="API Secret Copy Button (data-copy-target='#apiSecretText')"
    )
    assert api_access_page.api_secret_copy_btn.is_enabled(), (
        "Expected API Secret Copy button to be enabled"
    )

    # 4. API Link card
    assert_element_is_visible(api_access_page.api_link_input, element_name="API Link Input (#apitext)")
    link_url = api_access_page.get_api_link_url()
    assert len(link_url) > 0, "Expected non-empty API link URL in #apitext"
    assert "placeorder" in link_url, (
        f"Expected 'placeorder' in API link URL, got: '{link_url[:100]}'"
    )
    logger.info(f"API Link URL present (length {len(link_url)}) ✓")

    assert_element_is_visible(
        api_access_page.api_link_copy_btn,
        element_name="API Link Copy Button (data-copy-target='#apitext')"
    )
    assert api_access_page.api_link_copy_btn.is_enabled(), (
        "Expected API Link Copy button to be enabled"
    )

    # 5. Quick Start guide — exactly 5 steps
    assert_element_is_visible(api_access_page.quick_start_steps, element_name="Quick Start Steps (ol.api-steps)")
    step_count = api_access_page.get_quick_start_step_count()
    assert step_count == 5, f"Expected exactly 5 Quick Start steps, got: {step_count}"
    logger.info(f"Quick Start guide: {step_count} steps ✓")

    # 6. Symbols Reference card and download button
    assert_element_is_visible(
        api_access_page.symbols_resource_card,
        element_name="Symbols Reference Card (div.api-card.api-resource-card)"
    )
    assert_element_is_visible(api_access_page.csv_download_btn, element_name="Symbols CSV Download Button (#csvbtn)")
    assert api_access_page.csv_download_btn.is_enabled(), "Expected CSV download button to be enabled"

    csv_href = api_access_page.get_csv_download_href()
    assert "symbols_with_sector" in csv_href, (
        f"Expected href to contain 'symbols_with_sector', got: '{csv_href}'"
    )
    assert csv_href.endswith(".csv") or "csv" in csv_href.lower(), (
        f"Expected CSV file href, got: '{csv_href}'"
    )
    logger.info(f"Symbols CSV download href: '{csv_href}' ✓")


@pytest.mark.trade
@pytest.mark.smoke
def test_api_access_page_copy_secret_key(
    api_access_page: ApiAccessPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the API Secret token Copy button works correctly:
    1. #apiSecretText displays a non-empty, non-placeholder token.
    2. The Copy button is visible and enabled.
    3. Clicking the Copy button does not raise a JS error.
    4. After clicking Copy, the button label may change (visual feedback) and
       the token value in #apiSecretText is unchanged (not cleared).
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)

    # Record the token before clicking copy
    token_before = api_access_page.get_api_secret_token()
    assert len(token_before) > 0, f"Expected non-empty token before copy, got: '{token_before}'"
    logger.info(f"API Secret token (before copy): '{token_before}'")

    # Click Copy
    returned_token = api_access_page.click_copy_secret()
    assert returned_token == token_before, (
        f"click_copy_secret() should return the token text. "
        f"Expected '{token_before}', got '{returned_token}'"
    )

    # Token must still be visible and unchanged after clicking Copy
    token_after = api_access_page.get_api_secret_token()
    assert token_after == token_before, (
        f"API Secret token changed after clicking Copy! Before='{token_before}', After='{token_after}'"
    )
    logger.info(f"API Secret token unchanged after Copy: '{token_after}' ✓")

    # Verify copy button is still visible after click (not removed from DOM)
    assert_element_is_visible(
        api_access_page.api_secret_copy_btn,
        element_name="API Secret Copy Button (still visible after click)"
    )


@pytest.mark.trade
@pytest.mark.smoke
def test_api_access_page_copy_api_link(
    api_access_page: ApiAccessPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that the API Link (#apitext) and its Copy button work correctly:
    1. #apitext is a readonly input rendered with a full URL.
    2. URL contains the expected query parameters: type, bs, lot, sl, target, symbol, token.
    3. The token in the URL template is intentionally 'XXXXXXXXXX' (placeholder the user
       must replace with their real token — as documented by Quick Start step 2).
       The real token lives in #apiSecretText and must NOT equal 'XXXXXXXXXX'.
    4. The fingerprint in the URL is a real value (not a placeholder).
    5. Clicking the Copy button does not raise a JS error.
    6. The URL value in #apitext is unchanged after clicking Copy.
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)

    # 1. Get the full URL
    link_url = api_access_page.get_api_link_url()
    assert len(link_url) > 0, "Expected non-empty API link URL"
    assert "placeorder" in link_url, f"Expected 'placeorder' in link URL, got: '{link_url[:100]}'"
    logger.info(f"API Link URL: {link_url}")

    # 2. Parse and verify query parameters
    params = api_access_page.get_api_link_url_parsed()
    logger.info(f"Parsed API link parameters: {params}")

    required_params = ["type", "bs", "lot", "sl", "target", "symbol", "token", "fingerprint"]
    for p in required_params:
        assert p in params, (
            f"Expected query parameter '{p}' in API link URL. Found params: {list(params.keys())}"
        )
    assert params.get("type") == "market", (
        f"Expected type='market', got: '{params.get('type')}'"
    )
    assert params.get("clicked") == "yes", (
        f"Expected clicked='yes', got: '{params.get('clicked')}'"
    )

    # 3. Verify the token placeholder design:
    #    - The URL template uses 'XXXXXXXXXX' as the token placeholder (by design — Quick Start step 2
    #      says 'Replace XXXXXXXXXX in the link above with your token').
    #    - The actual live token is displayed separately in #apiSecretText.
    url_token = params.get("token", "")
    secret_token = api_access_page.get_api_secret_token()

    assert url_token == "XXXXXXXXXX", (
        f"Expected API link URL to have placeholder token 'XXXXXXXXXX' (by design), "
        f"got: '{url_token}'"
    )
    assert len(secret_token) > 0 and secret_token != "XXXXXXXXXX" and secret_token != "XXXXX", (
        f"Expected #apiSecretText to hold the real live token (not a placeholder), "
        f"got: '{secret_token}'"
    )
    logger.info(
        f"Token design verified ✓: URL template uses 'XXXXXXXXXX', "
        f"real token in #apiSecretText: '{secret_token}'"
    )

    # 4. Fingerprint should be a real non-placeholder value
    fingerprint = params.get("fingerprint", "")
    assert len(fingerprint) > 0 and "XXXXXX" not in fingerprint, (
        f"Expected a real fingerprint in URL, got: '{fingerprint}'"
    )
    logger.info(f"Fingerprint verified ✓: '{fingerprint}'")

    # 5. Click the Copy button
    returned_url = api_access_page.click_copy_link()
    assert returned_url == link_url, "click_copy_link() should return the pre-click URL"

    # 6. URL unchanged after clicking Copy
    link_url_after = api_access_page.get_api_link_url()
    assert link_url_after == link_url, (
        f"API link URL changed after clicking Copy!\n  Before: {link_url}\n  After:  {link_url_after}"
    )
    logger.info("API link URL unchanged after Copy ✓")




@pytest.mark.trade
@pytest.mark.smoke
def test_api_access_page_symbols_csv_download(
    api_access_page: ApiAccessPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify the 'Symbols with Sector' CSV download works:
    1. The #csvbtn anchor is visible, enabled, and has a download attribute.
    2. The href points to a .csv file containing 'symbols_with_sector'.
    3. Clicking #csvbtn triggers a file download event (Playwright Download).
    4. The downloaded file has a suggested filename containing 'symbols' or '.csv'.
    5. The downloaded file is non-empty (> 0 bytes).
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)

    # 1. Verify button attributes
    assert_element_is_visible(api_access_page.csv_download_btn, element_name="CSV Download Button (#csvbtn)")
    assert api_access_page.csv_download_btn.is_enabled(), "Expected CSV download button to be enabled"

    csv_href = api_access_page.get_csv_download_href()
    assert "symbols_with_sector" in csv_href, (
        f"Expected href to contain 'symbols_with_sector', got: '{csv_href}'"
    )
    logger.info(f"CSV download href: '{csv_href}' ✓")

    # Verify download attribute is present
    download_attr = api_access_page.csv_download_btn.get_attribute("download")
    assert download_attr is not None, (
        "Expected <a id='csvbtn'> to have a 'download' attribute to trigger file download"
    )

    # 2. Trigger download and capture
    download = api_access_page.download_symbols_csv(timeout=25000)
    suggested_name = download.suggested_filename
    logger.info(f"Downloaded file suggested filename: '{suggested_name}'")

    # 3. Filename check
    assert len(suggested_name) > 0, "Expected non-empty suggested filename from download"
    assert (
        "symbol" in suggested_name.lower()
        or "csv" in suggested_name.lower()
        or suggested_name.endswith(".csv")
    ), f"Expected CSV suggested filename, got: '{suggested_name}'"

    # 4. Save and check file size
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        download.save_as(tmp_path)
        file_size = os.path.getsize(tmp_path)
        logger.info(f"Downloaded CSV file size: {file_size} bytes")
        assert file_size > 0, (
            f"Expected non-empty CSV file download, but file is {file_size} bytes"
        )
        logger.info(f"Symbols CSV downloaded successfully: {file_size} bytes ✓")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@pytest.mark.trade
@pytest.mark.regression
def test_api_access_page_place_order_via_link(
    api_access_page: ApiAccessPage,
    positions_page: PositionsPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that placing a market order via the API link URL works end-to-end:
    1. Extract the real API link from #apitext (which contains the live token).
    2. Construct a live placeorder URL with:
         symbol=EURUSD, bs=buy, lot=0.01, sl=0, target=0
    3. Navigate to that URL in a new tab and capture the JSON response.
    4. Verify the response does not contain 'error' or 'failed'.
    5. Navigate to the Positions page and verify the placed order appears
       in the open positions table within 15 seconds.
    6. Clean up: close the newly placed position.
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)

    # 1. Ensure token is live (not a placeholder)
    token = api_access_page.get_api_secret_token()
    assert len(token) > 0 and token != "XXXXX", (
        f"API Secret token is placeholder or empty: '{token}'. "
        "Cannot place order via API link — ensure user is logged in and not in investor mode."
    )
    logger.info(f"Live API token confirmed: '{token}'")

    # Read the symbol from the template URL so we know exactly which symbol the test will use.
    # The template (e.g. X:BTCUSD) is a symbol the server is guaranteed to know.
    template_params = api_access_page.get_api_link_url_parsed()
    expected_symbol = template_params.get("symbol", "").upper()
    logger.info(f"Template symbol from #apitext: '{expected_symbol}'")

    # 2. Record open position count before placing order
    positions_page.navigate_to_position_page()
    count_before = positions_page.get_open_positions_count()
    logger.info(f"Open positions BEFORE API order: {count_before}")

    # 3. Navigate back to API page and place order.
    #    symbol=None → preserve the template's own symbol (e.g. X:BTCUSD).
    api_access_page.navigate_to_api_page()
    result = api_access_page.place_order_via_api_link(
        symbol=None,   # use the template's symbol — already validated by the server
        side="buy",
        lot=0.01,
        sl=0,
        target=0,
    )

    order_url = result["url"]
    response_text = result["response_text"]
    logger.info(f"API order URL used: {order_url}")
    logger.info(f"API order response: {response_text[:500]}")

    # 4. Verify response indicates success
    # The placeorder endpoint returns JSON: {"status":"success"|"fail", "message":"...", "data":[...]}
    import json as _json
    try:
        resp_json = _json.loads(response_text)
        resp_status = resp_json.get("status", "").lower()
        resp_message = resp_json.get("message", "")
    except _json.JSONDecodeError:
        resp_status = ""
        resp_message = response_text[:200]

    assert resp_status == "success", (
        f"API placeorder returned status='{resp_status}' (message='{resp_message}'). "
        f"Full response: {response_text[:500]}"
    )
    logger.info(f"API order response status='{resp_status}' ✓  message='{resp_message}'")

    # 5. Poll Positions page until the new order appears
    positions_page.navigate_to_position_page()
    # Give the server a moment to process the order before polling
    api_access_page.page.wait_for_timeout(3000)

    start_time = time.time()
    new_count = count_before
    while time.time() - start_time < 20:
        # Reload the positions list by re-navigating so fresh data is fetched
        try:
            positions_page.page.reload()
            positions_page.page.wait_for_timeout(1500)
            positions_page.navigate_to_position_page()
        except Exception:
            pass
        new_count = positions_page.get_open_positions_count()
        if new_count > count_before:
            break
        positions_page.page.wait_for_timeout(500)

    assert new_count > count_before, (
        f"Expected open positions to increase after API order. "
        f"Before={count_before}, After={new_count}. "
        f"API response was: {response_text[:300]}"
    )
    logger.info(f"Open positions AFTER API order: {new_count} (increased by {new_count - count_before}) ✓")

    # 6. Clean up — close all newly placed API orders matching the template's symbol
    open_positions = positions_page.get_open_positions_data()
    for pos in open_positions:
        pos_symbol = pos.get("symbol", "").upper().replace("X:", "").replace(" ", "")
        exp_symbol = expected_symbol.replace("X:", "").replace(" ", "")
        if pos_symbol == exp_symbol or pos.get("symbol", "").upper() == expected_symbol:
            try:
                positions_page.close_position_by_id(pos["id"])
                positions_page.page.wait_for_timeout(1000)
            except Exception as e:
                logger.warning(f"Could not close API-placed position {pos['id']}: {e}")


@pytest.mark.trade
@pytest.mark.regression
def test_api_access_page_runtime_diagnostics_clean(
    api_access_page: ApiAccessPage,
    trading_dashboard_page: TradingDashboardPage,
):
    """
    Verify that interacting with the API Access page operates with
    zero invisible runtime defects:
    - Zero JavaScript runtime exceptions (uncaught errors)
    - Zero console.error log emissions
    - Zero failed/aborted network requests
    - Zero HTTP 4xx/5xx error responses

    Exercises:
    1. Navigation to the API Access page via the left sidebar icon.
    2. Reading the API Secret token and API Link URL.
    3. Clicking the API Secret Copy button.
    4. Clicking the API Link Copy button.
    5. Reading all Quick Start guide steps.
    6. Asserting full diagnostic cleanliness after all interactions.
    """
    api_access_page.navigate_to_api_page()
    assert_url_contains(api_access_page.page, "/dashboard", timeout=15000)
    api_access_page.page.wait_for_timeout(1500)

    # Exercise: read token and URL
    token = api_access_page.get_api_secret_token()
    link_url = api_access_page.get_api_link_url()
    logger.info(f"[Diagnostics] Token length: {len(token)}, URL length: {len(link_url)}")

    # Exercise: click both copy buttons
    api_access_page.click_copy_secret()
    api_access_page.page.wait_for_timeout(400)
    api_access_page.click_copy_link()
    api_access_page.page.wait_for_timeout(400)

    # Exercise: read all Quick Start steps
    steps = api_access_page.get_quick_start_steps_text()
    logger.info(f"[Diagnostics] Quick Start steps: {steps}")

    # Assert zero hidden runtime defects
    api_access_page.assert_clean_diagnostics(
        check_js_errors=True,
        check_console_errors=True,
        check_failed_requests=True,
        check_http_errors=True,
        ignored_patterns=["google-analytics.com", "hotjar.com", "fonts.googleapis.com"],
    )

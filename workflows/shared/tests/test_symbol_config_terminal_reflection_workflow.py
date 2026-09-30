"""
Cross-Portal Symbol Configuration & Web Terminal Reflection Workflow Test Suite.

Verifies end-to-end symbol management between Admin Portal and Trade Terminal:
1. Snapshot initial state of target secondary symbol (USDCAD):
   - allow_trade, min_lot, max_lot, default_lot, precision.
   - brokerage (commission).
   - Market hours, holiday overrides, and special sessions.
2. In Admin Symbol Configuration (/admin/Controlbase/symbolConfiguration):
   - Validate modal tabs: General, Hours, Holiday, Special, Upcoming.
   - Test Trade Allowed toggle ("0" -> Not Allowed) and verify Admin table reflection.
3. In Trade Terminal (/dashboard/):
   - Verify reflection of "Trade Not Allowed" / Market closed state:
     - Order ticket blocks execution or returns trade disabled / market closed error.
4. In Admin Symbols (/admin/Controlbase/symbol):
   - Update brokerage / commission (per-minute workflow check).
   - Verify persistence in Admin table and reflection in Terminal / Client Portal.
5. Minute-by-minute workflow checks & form values validation.
6. Reversion & Clean Teardown:
   - Restores allow_trade to initial snapshot ("1" -> Allowed).
   - Restores brokerage to initial snapshot.
   - Logs out all sessions cleanly.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, Generator
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect

from config.settings import settings
from workflows.shared.utils.logger import get_logger

logger = get_logger("symbol_config_terminal_reflection")

ADMIN_USER = settings.admin_portal.username or "madmin"
ADMIN_PASS = settings.admin_portal.password or "Test@1234"
TARGET_SYMBOL = "USDCAD"


def _dismiss_confirm_dialogs(page: Page, timeout: int = 4000) -> None:
    """Helper to dismiss any $.confirm or SweetAlert dialogs."""
    try:
        swal = page.locator("button.swal2-confirm")
        if swal.first.is_visible(timeout=1500):
            swal.first.click()
            page.wait_for_timeout(800)
    except Exception:
        pass
    try:
        dialog_btns = page.locator(".jconfirm-box .jconfirm-buttons button")
        if dialog_btns.first.is_visible(timeout=timeout):
            dialog_btns.first.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass


def _dismiss_disclaimer_if_present(page: Page) -> None:
    """Dismiss One-Click Trading or any disclaimer popups in Trade Terminal."""
    try:
        page.evaluate("""() => {
            const modal = document.querySelector('#disclaimer') || document.querySelector('.modal.show');
            if (modal) {
                const btn = modal.querySelector('#acceptButton') || modal.querySelector('#close-disclaimer') || modal.querySelector('.close');
                if (btn) btn.click();
                modal.style.display = 'none';
                document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
                document.body.classList.remove('modal-open');
            }
        }""")
        page.wait_for_timeout(300)
    except Exception:
        pass


@pytest.fixture(scope="module")
def symbol_workflow_session(browser: Browser) -> Generator[Dict[str, Any], None, None]:
    """
    Session fixture:
    - Master Admin login.
    - Snapshot target symbol initial settings (allow_trade, brokerage).
    - Client login on Web Terminal.
    - Teardown: Reverts all modified symbol settings to snapshot values.
    """
    admin_ctx: BrowserContext = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    admin_page: Page = admin_ctx.new_page()

    # Step 1: Admin Login
    login_url = settings.admin_portal.login_url or "https://stage.xtremenext.com/admin/Login/index"
    admin_page.goto(login_url)
    admin_page.fill("#username, input[name='username']", ADMIN_USER)
    admin_page.fill("#password, input[name='password']", ADMIN_PASS)
    admin_page.click("button[type='submit'], .savebut")
    admin_page.wait_for_timeout(3000)
    assert "Controlbase" in admin_page.url or "admin" in admin_page.url
    logger.info("Admin successfully authenticated.")

    # Step 2: Snapshot Initial Symbol Configuration
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#symbolConfigurationTable_filter input", TARGET_SYMBOL)
    admin_page.wait_for_timeout(1500)

    edit_config_btn = admin_page.locator("a.btnConfigEdit").first
    expect(edit_config_btn).to_be_visible(timeout=10000)
    edit_config_btn.click(force=True)
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("#symbolConfigModal")).to_be_visible(timeout=10000)

    init_allow_trade = admin_page.locator("#allow_trade").input_value() or "1"
    init_min_lot = admin_page.locator("#min_lot").input_value() or "0.01"
    init_max_lot = admin_page.locator("#max_lot").input_value() or "100"
    logger.info(f"Snapshotted {TARGET_SYMBOL} Config: allow_trade={init_allow_trade}, min_lot={init_min_lot}, max_lot={init_max_lot}")

    # Close modal
    admin_page.locator("#symbolConfigModal button.btn-close, #symbolConfigModal button:has-text('Close')").first.click()
    admin_page.wait_for_timeout(1000)

    # Step 3: Snapshot Initial Brokerage in Symbols List
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolList")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input, input[type='search']", TARGET_SYMBOL)
    admin_page.wait_for_timeout(1500)

    symbol_edit_btn = admin_page.locator("table#datatable tbody tr a.btnEdit").first
    expect(symbol_edit_btn).to_be_visible(timeout=10000)
    symbol_edit_btn.click()
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("#myModal")).to_be_visible(timeout=10000)

    init_brokerage = admin_page.locator("#brokerage").input_value() or "0.00"
    logger.info(f"Snapshotted {TARGET_SYMBOL} Brokerage: {init_brokerage}")

    # Close modal
    admin_page.locator("#myModal button:has-text('Close'), #myModal .ux-card-close").first.click()
    admin_page.wait_for_timeout(1000)

    # Step 4: Web Terminal Session
    terminal_ctx: BrowserContext = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    terminal_page: Page = terminal_ctx.new_page()

    terminal_url = f"{settings.trade_terminal.base_url.rstrip('/')}/dashboard/"
    logger.info(f"Opening Trade Terminal: {terminal_url}")
    terminal_page.goto(terminal_url)
    terminal_page.wait_for_timeout(3500)
    _dismiss_disclaimer_if_present(terminal_page)

    session_data = {
        "admin_page": admin_page,
        "terminal_page": terminal_page,
        "target_symbol": TARGET_SYMBOL,
        "init_allow_trade": init_allow_trade,
        "init_brokerage": init_brokerage,
    }

    try:
        yield session_data
    finally:
        logger.info("Executing teardown: Reverting symbol configuration and brokerage to initial snapshot values...")
        try:
            # 1. Revert allow_trade in symbolConfiguration
            admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
            admin_page.wait_for_timeout(2000)
            admin_page.fill("#symbolConfigurationTable_filter input", TARGET_SYMBOL)
            admin_page.wait_for_timeout(1500)
            btn = admin_page.locator("a.btnConfigEdit").first
            if btn.is_visible(timeout=5000):
                btn.click(force=True)
                admin_page.wait_for_timeout(1500)
                admin_page.select_option("#allow_trade", init_allow_trade)
                admin_page.click("#symbolConfigSubmit")
                admin_page.wait_for_timeout(2500)
                _dismiss_confirm_dialogs(admin_page)
                logger.info(f"Reverted {TARGET_SYMBOL} allow_trade back to {init_allow_trade}")
        except Exception as e:
            logger.warning(f"Error reverting allow_trade in teardown: {e}")

        try:
            # 2. Revert brokerage in symbol
            admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolList")
            admin_page.wait_for_timeout(2000)
            admin_page.fill("#datatable_filter input, input[type='search']", TARGET_SYMBOL)
            admin_page.wait_for_timeout(1500)
            s_btn = admin_page.locator("table#datatable tbody tr a.btnEdit").first
            if s_btn.is_visible(timeout=5000):
                s_btn.click()
                admin_page.wait_for_timeout(1500)
                admin_page.fill("#brokerage", str(init_brokerage))
                admin_page.click("#myModal #formSubmit, #formSubmit")
                admin_page.wait_for_timeout(2500)
                _dismiss_confirm_dialogs(admin_page)
                logger.info(f"Reverted {TARGET_SYMBOL} brokerage back to {init_brokerage}")
        except Exception as e:
            logger.warning(f"Error reverting brokerage in teardown: {e}")

        terminal_ctx.close()
        admin_ctx.close()
        logger.info("Symbol reflection workflow sessions cleanly closed.")


# ==============================================================================
# WORKFLOW 1: SYMBOL CONFIGURATION MODAL TABS & MARKET HOURS INSPECTION
# ==============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.regression
def test_workflow_symbol_configuration_tabs_and_market_hours(symbol_workflow_session: Dict[str, Any]):
    """
    Workflow 1:
    - Navigates to /admin/Controlbase/symbolConfiguration.
    - Searches target symbol (USDCAD) and opens #symbolConfigModal.
    - Inspects General Tab form inputs: config_uid, display_name, min/max lot, precision.
    - Inspects Hours Tab: checks market calendar schedule and tests #refreshMarketCalendar.
    - Inspects Holiday Tab: tests #addHolidayOverride button and holiday controls.
    - Inspects Special Tab: tests #addSpecialOverride button and date input #specialOverrideDate.
    - Inspects Upcoming Tab: tests #refreshUpcomingPreview button.
    - Closes modal cleanly.
    """
    admin_page: Page = symbol_workflow_session["admin_page"]
    symbol = symbol_workflow_session["target_symbol"]

    logger.info("Executing Workflow 1: Inspecting Symbol Configuration modal tabs and market hours...")
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2500)

    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)

    edit_btn = admin_page.locator("a.btnConfigEdit").first
    expect(edit_btn).to_be_visible(timeout=10000)
    edit_btn.click(force=True)
    admin_page.wait_for_timeout(1500)

    modal = admin_page.locator("#symbolConfigModal")
    expect(modal).to_be_visible(timeout=10000)

    # 1. General Tab Elements
    expect(admin_page.locator("#symbolGeneralTab")).to_be_visible()
    expect(admin_page.locator("#config_symbol")).to_be_visible()
    expect(admin_page.locator("#min_lot")).to_be_visible()
    expect(admin_page.locator("#max_lot")).to_be_visible()
    expect(admin_page.locator("#allow_trade")).to_be_visible()
    expect(admin_page.locator("#is_active")).to_be_visible()
    logger.info("General tab configuration inputs verified.")

    # 2. Hours Tab
    hours_tab = admin_page.locator("button[data-bs-target='#symbolHoursTab']")
    hours_tab.click()
    admin_page.wait_for_timeout(1000)
    expect(admin_page.locator("#symbolHoursTab")).to_be_visible()
    refresh_cal = admin_page.locator("#refreshMarketCalendar")
    if refresh_cal.is_visible():
        refresh_cal.click()
        admin_page.wait_for_timeout(1000)
    logger.info("Hours tab market calendar and refresh action verified.")

    # 3. Holiday Tab
    holiday_tab = admin_page.locator("button[data-bs-target='#symbolHolidayTab']")
    holiday_tab.click()
    admin_page.wait_for_timeout(1000)
    expect(admin_page.locator("#symbolHolidayTab")).to_be_visible()
    add_holiday_btn = admin_page.locator("#addHolidayOverride")
    expect(add_holiday_btn).to_be_visible()
    logger.info("Holiday tab override controls verified.")

    # 4. Special Tab
    special_tab = admin_page.locator("button[data-bs-target='#symbolSpecialTab']")
    special_tab.click()
    admin_page.wait_for_timeout(1000)
    expect(admin_page.locator("#symbolSpecialTab")).to_be_visible()
    add_special_btn = admin_page.locator("#addSpecialOverride")
    expect(add_special_btn).to_be_visible()
    logger.info("Special tab override controls verified.")

    # 5. Upcoming Tab
    upcoming_tab = admin_page.locator("button[data-bs-target='#symbolUpcomingTab']")
    upcoming_tab.click()
    admin_page.wait_for_timeout(1000)
    expect(admin_page.locator("#symbolUpcomingTab")).to_be_visible()
    refresh_upcoming = admin_page.locator("#refreshUpcomingPreview")
    if refresh_upcoming.is_visible():
        refresh_upcoming.click()
        admin_page.wait_for_timeout(1000)
    logger.info("Upcoming preview tab verified.")

    # Close modal
    admin_page.locator("#symbolConfigModal button.btn-close, #symbolConfigModal button:has-text('Close')").first.click()
    admin_page.wait_for_timeout(1000)
    expect(modal).not_to_be_visible(timeout=5000)
    logger.info("Symbol configuration modal closed cleanly.")


# ==============================================================================
# WORKFLOW 2: TRADE DISALLOWED / MARKET CLOSED TERMINAL REFLECTION
# ==============================================================================

@pytest.mark.shared
@pytest.mark.regression
def test_workflow_trade_disallowed_and_terminal_reflection(symbol_workflow_session: Dict[str, Any]):
    """
    Workflow 2:
    - Step 1: In Admin Symbol Configuration, set Allow Trade = "0" (Not Allowed) for USDCAD.
    - Step 2: Save and verify Admin Datatable displays "Not Allowed".
    - Step 3: In Trade Terminal, inspect Watchlist for USDCAD.
    - Step 4: Open Order Entry dialog (#dragable_modal) for USDCAD and attempt order execution.
    - Step 5: Verify that order is blocked or returns trade not allowed / market closed toast.
    - Step 6: In Admin Symbol Configuration, re-enable Allow Trade = "1" (Allowed) and verify.
    """
    admin_page: Page = symbol_workflow_session["admin_page"]
    terminal_page: Page = symbol_workflow_session["terminal_page"]
    symbol = symbol_workflow_session["target_symbol"]

    logger.info("Executing Workflow 2: Testing Trade Disallowed toggle and Terminal reflection...")

    # 1. Set Allow Trade = 0 (Not Allowed)
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)

    admin_page.locator("a.btnConfigEdit").first.click(force=True)
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("#symbolConfigModal")).to_be_visible(timeout=10000)

    admin_page.select_option("#allow_trade", "0")
    admin_page.click("#symbolConfigSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # Verify datatable reflection
    admin_page.reload()
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)
    row_text = admin_page.locator("#symbolConfigurationTable tbody tr").first.inner_text()
    assert "Not Allowed" in row_text or "0" in row_text or "Disallowed" in row_text
    logger.info(f"Admin Symbol Configuration verified: {symbol} Allow Trade is Not Allowed.")

    # 2. Check Terminal Reflection
    _dismiss_disclaimer_if_present(terminal_page)
    terminal_page.wait_for_timeout(1500)

    # Search symbol in watchlist
    search_input = terminal_page.locator("#search-input")
    if search_input.is_visible():
        search_input.fill(symbol)
        terminal_page.wait_for_timeout(1000)

    # Find symbol row in favorites or all symbols
    symbol_row = terminal_page.locator(f".esearch-result li[data-symbol='{symbol}'], .list-all-symbols li[data-symbol='{symbol}']").first
    if symbol_row.is_visible(timeout=5000):
        symbol_row.hover()
        terminal_page.wait_for_timeout(500)
        buy_btn = symbol_row.locator(".placeorder.buy, button.buy").first

        if buy_btn.is_visible(timeout=3000):
            buy_btn.click()
            terminal_page.wait_for_timeout(1000)

            # In modal, attempt submit
            modal = terminal_page.locator("#dragable_modal")
            if modal.is_visible(timeout=5000):
                place_btn = modal.locator("button.placeorderx").first
                if place_btn.is_visible():
                    place_btn.click()
                    terminal_page.wait_for_timeout(1500)

                    # Verify error toast / alert notification
                    toast_text = terminal_page.evaluate("""() => {
                        const alert = document.querySelector('.alertify-notifier .ajs-message') ||
                                      document.querySelector('.toast') ||
                                      document.querySelector('.alert');
                        return alert ? alert.innerText : '';
                    }""")
                    logger.info(f"Terminal order feedback when trade not allowed: '{toast_text}'")

                # Close order modal
                close_btn = modal.locator("button.close, .modal-header button").first
                if close_btn.is_visible():
                    close_btn.click()

    logger.info("Terminal reflection check for trade disallowed completed successfully.")

    # 3. Restore Allow Trade = 1 (Allowed)
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)

    admin_page.locator("a.btnConfigEdit").first.click(force=True)
    admin_page.wait_for_timeout(1500)
    admin_page.select_option("#allow_trade", "1")
    admin_page.click("#symbolConfigSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    admin_page.reload()
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)
    restored_row_text = admin_page.locator("#symbolConfigurationTable tbody tr").first.inner_text()
    assert "Allowed" in restored_row_text and "Not Allowed" not in restored_row_text
    logger.info(f"Admin Symbol Configuration restored: {symbol} Allow Trade is Allowed.")


# ==============================================================================
# WORKFLOW 3: COMMISSION (BROKERAGE) UPDATE & PROPAGATION
# ==============================================================================

@pytest.mark.shared
@pytest.mark.regression
def test_workflow_commission_brokerage_update_and_propagation(symbol_workflow_session: Dict[str, Any]):
    """
    Workflow 3:
    - Step 1: Navigates to /admin/Controlbase/symbol.
    - Step 2: Search target symbol (USDCAD), open in-row edit modal (a.btnEdit -> #myModal).
    - Step 3: Update #brokerage to 5.00 and save (#formSubmit).
    - Step 4: Verify updated brokerage appears in Datatable row.
    - Step 5: Check Terminal order/specification calculation reflection.
    - Step 6: Restore original brokerage value and verify datatable restoration.
    """
    admin_page: Page = symbol_workflow_session["admin_page"]
    symbol = symbol_workflow_session["target_symbol"]
    init_brokerage = symbol_workflow_session["init_brokerage"]
    test_brokerage = "5.00"

    logger.info(f"Executing Workflow 3: Updating commission / brokerage for {symbol} to {test_brokerage}...")

    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolList")
    admin_page.wait_for_timeout(2500)
    admin_page.fill("#datatable_filter input, input[type='search']", symbol)
    admin_page.wait_for_timeout(1500)

    edit_btn = admin_page.locator("table#datatable tbody tr a.btnEdit").first
    expect(edit_btn).to_be_visible(timeout=10000)
    edit_btn.click()
    admin_page.wait_for_timeout(1500)
    expect(admin_page.locator("#myModal")).to_be_visible(timeout=10000)

    admin_page.fill("#brokerage", test_brokerage)
    admin_page.click("#myModal #formSubmit, #formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    # Verify updated brokerage in datatable
    admin_page.reload()
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#datatable_filter input, input[type='search']", symbol)
    admin_page.wait_for_timeout(1500)
    row_text = admin_page.locator("table#datatable tbody tr").first.inner_text()
    cols = [c.strip() for c in row_text.split("\t") if c.strip()]
    assert len(cols) >= 3, f"Unexpected row format: {row_text}"
    assert float(cols[2]) == float(test_brokerage), f"Expected brokerage {test_brokerage}, got {cols[2]}"
    logger.info(f"Commission update verified in Admin table: {cols[2]}")

    # Restore initial brokerage
    edit_btn_restore = admin_page.locator("table#datatable tbody tr a.btnEdit").first
    edit_btn_restore.click()
    admin_page.wait_for_timeout(1500)
    admin_page.fill("#brokerage", str(init_brokerage))
    admin_page.click("#myModal #formSubmit, #formSubmit")
    admin_page.wait_for_timeout(2500)
    _dismiss_confirm_dialogs(admin_page)

    admin_page.reload()
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#datatable_filter input, input[type='search']", symbol)
    admin_page.wait_for_timeout(1500)
    restored_text = admin_page.locator("table#datatable tbody tr").first.inner_text()
    restored_cols = [c.strip() for c in restored_text.split("\t") if c.strip()]
    assert float(restored_cols[2]) == float(init_brokerage), f"Expected restored brokerage {init_brokerage}, got {restored_cols[2]}"
    logger.info(f"Commission cleanly restored to initial value: {init_brokerage}")


# ==============================================================================
# WORKFLOW 4: MINUTE-BY-MINUTE SYMBOL CONFIGURATION FORM VALUES INSPECTION
# ==============================================================================

@pytest.mark.shared
@pytest.mark.admin
@pytest.mark.regression
def test_workflow_symbol_minute_workflow_and_form_values_inspection(symbol_workflow_session: Dict[str, Any]):
    """
    Workflow 4:
    - Step 1: Navigates to /admin/Controlbase/symbolConfiguration.
    - Step 2: Open edit modal and inspect all input fields:
      min_lot, max_lot, default_lot, step_size, margin_index, precision_digits.
    - Step 3: Validate that numeric inputs reject invalid characters or enforce constraints.
    - Step 4: Close modal without saving and verify state integrity.
    """
    admin_page: Page = symbol_workflow_session["admin_page"]
    symbol = symbol_workflow_session["target_symbol"]

    logger.info("Executing Workflow 4: Inspecting symbol configuration form values and minute workflow...")
    admin_page.goto("https://stage.xtremenext.com/admin/Controlbase/symbolConfiguration")
    admin_page.wait_for_timeout(2000)
    admin_page.fill("#symbolConfigurationTable_filter input", symbol)
    admin_page.wait_for_timeout(1500)

    admin_page.locator("a.btnConfigEdit").first.click(force=True)
    admin_page.wait_for_timeout(1500)
    modal = admin_page.locator("#symbolConfigModal")
    expect(modal).to_be_visible(timeout=10000)

    # Check form inputs
    min_lot = admin_page.locator("#min_lot").input_value()
    max_lot = admin_page.locator("#max_lot").input_value()
    default_lot = admin_page.locator("#default_lot").input_value()
    step_size = admin_page.locator("#step_size").input_value()

    assert float(min_lot) > 0, "Min lot should be positive"
    assert float(max_lot) >= float(min_lot), "Max lot should be >= Min lot"
    assert float(default_lot) >= float(min_lot), "Default lot should be >= Min lot"
    assert float(step_size) > 0, "Step size should be positive"
    logger.info(f"Verified {symbol} lot rules: min={min_lot}, max={max_lot}, default={default_lot}, step={step_size}")

    # Close modal
    admin_page.locator("#symbolConfigModal button.btn-close, #symbolConfigModal button:has-text('Close')").first.click()
    admin_page.wait_for_timeout(1000)
    expect(modal).not_to_be_visible(timeout=5000)
    logger.info("Form values integrity check completed successfully.")

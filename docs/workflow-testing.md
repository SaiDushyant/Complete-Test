# Behavioral Workflow Testing Guide

This guide details best practices for authoring, structuring, and debugging functional and end-to-end workflow tests in `workflows/`.

---

## 1. Page Object Model (POM) Design

Every page or major component in the application must be encapsulated by a Page Object inheriting from `workflows.shared.pages.base_page.BasePage`.

### Rules for Page Objects
1. **Encapsulate Selectors**: Never put raw CSS or XPath selectors directly in test functions. Store them as instance attributes (`self.locator_name`) inside the Page Object.
2. **Action-Oriented Methods**: Methods should represent user actions (`login()`, `submit_order()`, `filter_users()`) or queries (`is_displayed()`, `get_error_message()`).
3. **Return Next Page or Self**: Methods that navigate or transition pages can return the new Page Object instance for clean method chaining.

```python
# workflows/trade_terminal/pages/positions_page.py
from __future__ import annotations
from playwright.sync_api import Page, Locator
from workflows.shared.pages.base_page import BasePage

class PositionsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.positions_table = page.locator("table.positions-table")
        self.close_position_btn = page.locator("button.btn-close-position")
        self.pnl_summary = page.locator(".pnl-summary-value")

    def close_first_open_position(self) -> None:
        self.close_position_btn.first.click()

    def get_open_position_count(self) -> int:
        return self.page.locator("tr.position-row").count()
```

---

## 2. Fixture Strategy & Hierarchy

The workflow framework employs a tiered fixture model to maximize test speed and guarantee state isolation:

```text
               workflow_browser (session-scoped)
                           │
                           ▼
          workflow_context / authenticated_context (function-scoped)
                           │
                           ▼
             workflow_page / authenticated_page (function-scoped)
                           │
                           ▼
             Page Object Fixtures (trade_login_page, etc.)
```

### Portal-Specific Fixture Scopes
- `workflow_browser`: Shared Chromium browser instance launched once per test session.
- `authenticated_<portal>_context`: Browser context initialized with the portal's storage state (`auth/auth_state_<portal>.json`). Reused across tests to avoid repeated logins.
- `authenticated_<portal>_page`: Isolated page per test function, guaranteeing no cookie, tab, or DOM bleed between test cases.

---

## 3. Test Naming & Organization

- **File Naming**: Name test files `test_<feature_or_workflow>.py` (e.g., `test_order_placement.py`, `test_kyc_verification.py`).
- **Function Naming**: Use descriptive behavioral names: `test_<user_role>_<can/cannot>_<action>_<expected_outcome>()`:
  - `test_trader_can_place_limit_buy_order()`
  - `test_unauthenticated_user_is_redirected_to_login()`
  - `test_admin_cannot_delete_superuser_account()`
- **Organization**: Place tests strictly within your portal's `tests/` directory:
  - Trade Terminal: `workflows/trade_terminal/tests/`
  - Admin Portal: `workflows/admin_portal/tests/`
  - Client Portal: `workflows/client_portal/tests/`

---

## 4. Assertions & Assertion Helpers

Prefer readable, domain-specific assertions over bare Python asserts:

```python
from workflows.shared.assertions.assert_helpers import (
    assert_element_is_visible,
    assert_element_has_text,
    assert_url_contains,
)

def test_login_successful(client_dashboard_page):
    client_dashboard_page.navigate()
    assert_url_contains(client_dashboard_page.page, "/dashboard")
    assert_element_is_visible(client_dashboard_page.welcome_banner)
```

Playwright's web-first assertions (`expect(locator).to_be_visible()`) are automatically retried until the configured timeout expires.

---

## 5. Test Data Management

Do NOT hardcode dynamic or environment-specific test values inside test functions:
- Store static constants (e.g., standard symbols, currencies) in `workflows/<portal>/test_data/`.
- Use `workflows/shared/test_data/common_data.py` to generate unique random emails, order comments, or user names to prevent collision during concurrent test runs.

```python
from workflows.shared.test_data.common_data import random_email, random_string

def test_registration_with_unique_email(registration_page):
    email = random_email(prefix="test_client")
    registration_page.register(email=email, password="SafePassword123!")
```

---

## 6. Authentication Architecture

Authentication is decoupled and reused across tests:
1. `workflows/shared/fixtures/auth_fixtures.py` checks if `auth/auth_state_<portal>.json` exists and is non-empty.
2. If valid, the cached session cookies and local storage tokens are loaded into a new browser context in milliseconds.
3. If missing or expired, the portal's `_perform_login` helper is executed once, and the resulting state is saved to `auth/auth_state_<portal>.json`.
4. Authentication states are gitignored (`auth/*.json`) to avoid committing session tokens.

---

## 7. Wait Strategies (Avoiding Flakiness)

**Never use `time.sleep()`**. Hardcoded sleeps slow down suites and cause unpredictable failures across different hardware and CI environments.

Use Playwright auto-waiting or the helper functions in `workflows/shared/utils/waits.py`:
- `wait_for_network_idle(page)`
- `wait_for_selector(page, selector, state="visible")`
- `wait_for_condition(condition_fn)`

```python
from workflows.shared.utils.waits import wait_for_network_idle

def test_trade_chart_loads(trading_page):
    trading_page.select_symbol("BTCUSD")
    wait_for_network_idle(trading_page.page)
```

---

## 8. Failure Diagnostics: Screenshots & Traces

The framework automatically hooks into Pytest test execution via `pytest_runtest_makereport` in `conftest.py`:
- **Screenshots**: When a test fails, a full-page screenshot is automatically captured and saved to:
  `reports/workflows/screenshots/<test_name>_<timestamp>.png`
- **Traces**: Playwright trace zip files (recording DOM snapshots, console logs, network requests, and action timelines) are saved to:
  `reports/workflows/traces/<test_name>_<timestamp>.zip`

To view a trace zip file:
```bash
playwright show-trace reports/workflows/traces/<trace_filename>.zip
```

---

## 9. Debugging Tests

### Headed Mode
Run tests with a visible browser window:
```bash
pytest workflows/trade_terminal/tests --headed
```

### Slow Motion
Slow down execution by specified milliseconds to watch interactions live:
```bash
BROWSER_SLOW_MO=500 pytest workflows/trade_terminal/tests --headed
```

### Playwright Inspector (Step-Through Debugging)
Run with `PWDEBUG=1` to launch the Playwright interactive debugger:
```bash
PWDEBUG=1 pytest workflows/trade_terminal/tests/test_trade_example.py
```

### Pytest Specific Flags
- `-k <pattern>`: Run only tests matching a name pattern.
- `-s`: Show stdout prints and logs in the console.
- `--tb=short`: Short tracebacks for cleaner output.

# Domain Ownership & Boundary Matrix

To allow three developers to work concurrently in GitHub without stepping on each other's work or causing Git merge conflicts, this repository enforces strict directory-based domain ownership.

---

## 1. Domain Ownership Breakdown

```text
┌─────────────────────────┬───────────────────────────────────┬───────────────┬─────────────┐
│ Domain                  │ Primary Directory                 │ Primary Owner │ Total Tests │
├─────────────────────────┼───────────────────────────────────┼───────────────┼─────────────┤
│ Trade Terminal          │ workflows/trade_terminal/         │ Developer 1   │ 491 tests   │
│ Admin Portal            │ workflows/admin_portal/           │ Developer 2   │ 653 tests   │
│ Client Portal           │ workflows/client_portal/          │ Developer 3   │ 338 tests   │
│ Shared Infrastructure   │ workflows/shared/                 │ All Devs      │ 176 tests   │
│ Configuration           │ config/                           │ All Devs      │ N/A         │
│ UI Regression Engine    │ ui_regression/                    │ Automation TL │ 29 tests    │
│ Total Platform Coverage │ Whole Repository                  │ Core Team     │ 1,687 tests │
└─────────────────────────┴───────────────────────────────────┴───────────────┴─────────────┘
```

---

## 2. Developer 1 — Trade Terminal Domain

- **Primary Directory**: `workflows/trade_terminal/`
- **Total Tests**: **491 tests** (175 Workflow + 220 Validation + 96 Mock tests)
- **Subdirectories**:
  - `pages/`: Trade Terminal Page Objects (`login_page.py`, `trading_dashboard_page.py`, `order_entry_page.py`, `positions_page.py`, `watchlist_page.py`)
  - `tests/`:
    - Workflow Suites: `test_trade_*.py` (market orders, limit orders, chart interactions, watchlist selection, position lifecycle)
    - Validation Suites: `test_val_trade_*.py` (13 suites: order entry boundaries, account calculations, SQLi/XSS fuzzing, network resilience, password reset)
    - Mock Suites (`tests/mock/`): 96 tests across 13 suites (auth/session, order execution, account metrics, quotes/watchlist, positions, account switcher, navigation, chart, history, dashboard, profile, API keys, server errors)
  - `fixtures/`: `trade_fixtures.py` (authenticated trade contexts, trading pages)
  - `utils/`: Trade calculations, tick rounding, and order validation helpers
- **Execution Commands**:
  ```bash
  # Run all Trade Terminal tests
  pytest workflows/trade_terminal/ -v

  # Run Trade Terminal mock tests (96 tests in ~4s)
  python scripts/run_mock_tests.py --portal trade

  # Run Trade Terminal validation tests (220 tests)
  pytest workflows/trade_terminal/tests/test_val_trade_*.py -v
  ```
- **Markers**: `@pytest.mark.trade`, `@pytest.mark.validation`, `@pytest.mark.mock`

---

## 3. Developer 2 — Admin Portal Domain

- **Primary Directory**: `workflows/admin_portal/`
- **Total Tests**: **653 tests** (443 Workflow + 129 Validation + 81 Mock tests)
- **Subdirectories**:
  - `pages/`: Admin Management Page Objects (`admin_login_page.py`, `admin_dashboard_page.py`, `user_management_page.py`, `deposit_withdraw_page.py`)
  - `tests/`:
    - Workflow Suites: `test_admin_*.py` (administrator authentication, role permissions, user search, deposit approvals, account settings, plus `test_admin_shared_components.py` with 35 parameterized tests for tables, pagination, search, and export controls)
    - Validation Suites: `test_val_admin_*.py` (9 suites: orders calculation, input boundaries, user management, KYC document status, leads import, date filters)
    - Mock Suites (`tests/mock/`): 81 tests across 22 suites (auth, user CRUD, deposits, withdrawals, KYC review, LP bridge, orders, risk books, cron jobs, PAMM/MAM, roles, settings, symbols, bonus, leads, audit, server errors)
  - `fixtures/`: `admin_fixtures.py` (authenticated admin contexts, admin pages)
  - `utils/`: Admin navigation helpers, table row extractors, query utilities
- **Execution Commands**:
  ```bash
  # Run all Admin Portal tests
  pytest workflows/admin_portal/ -v

  # Run Admin Portal mock tests (81 tests in ~4s)
  python scripts/run_mock_tests.py --portal admin

  # Run Admin Portal validation tests (129 tests)
  pytest workflows/admin_portal/tests/test_val_admin_*.py -v
  ```
- **Markers**: `@pytest.mark.admin`, `@pytest.mark.validation`, `@pytest.mark.mock`

---

## 4. Developer 3 — Client Portal Domain

- **Primary Directory**: `workflows/client_portal/`
- **Total Tests**: **338 tests** (161 Workflow + 85 Validation + 92 Mock tests)
- **Subdirectories**:
  - `pages/`: Client Portal Page Objects (`client_login_page.py`, `client_dashboard_page.py`, `client_deposit_page.py`, `client_withdraw_page.py`, `client_settings_page.py`)
  - `tests/`:
    - Workflow Suites: `test_client_*.py` (client registration, login, profile updates, KYC document uploads, deposit/withdrawal requests, wallet transfers)
    - Validation Suites: `test_val_client_*.py` (13 suites: exhaustive labels/dropdowns, auth inputs, deposits, withdrawals, internal transfers, MAM/PAMM, security edge cases)
    - Mock Suites (`tests/mock/`): 92 tests across 7 suites (auth & security, dashboard & cashflow, deposits/gateways, withdrawals & payouts, internal transfers, KYC & wallets, PAMM/MAM, settings & IB referral, network resilience)
  - `fixtures/`: `client_fixtures.py` (authenticated client contexts, client pages)
  - `utils/`: Client validation utilities, session recovery helpers
- **Execution Commands**:
  ```bash
  # Run all Client Portal tests
  pytest workflows/client_portal/ -v

  # Run Client Portal mock tests (92 tests in ~4s)
  python scripts/run_mock_tests.py --portal client

  # Run Client Portal validation tests (85 tests)
  pytest workflows/client_portal/tests/test_val_client_*.py -v
  ```
- **Markers**: `@pytest.mark.client`, `@pytest.mark.validation`, `@pytest.mark.mock`

---

## 5. Shared Infrastructure (`workflows/shared/`)

The shared directory contains framework-level primitives reused across all three portals:

- `workflows/shared/pages/base_page.py`: Universal base class with high-level Playwright wrappers.
- `workflows/shared/helpers/`: Shared attack vectors (`validation_payloads.py`) and financial math formulas (`math_assertions.py`).
- `workflows/shared/fixtures/`: Global browser lifecycle management (`browser_fixtures.py`) and auth caching (`auth_fixtures.py`).
- `workflows/shared/utils/`: Multi-suite test logger (`test_logger.py`), runtime diagnostics telemetry (`diagnostics.py`), error monitor (`error_monitor.py`), and safe waits (`waits.py`).
- `workflows/shared/constants/`: Standard timeouts (`timeouts.py`), viewports (`viewports.py`), canonical routes (`routes.py`).
- `workflows/shared/assertions/`: Domain-agnostic assertion wrappers (`assert_helpers.py`).

### Rules for Contributing to `shared/`
1. **Never Put Portal-Specific Code in Shared**: If a method, locator, or test datum is only used by one portal, it belongs in that portal's directory.
2. **Team Communication**: Before modifying existing classes or signatures in `workflows/shared/`, notify the team to prevent breaking other developers' active branches.
3. **Isolate Shared Changes**: When possible, submit shared framework additions as independent, focused Pull Requests before depending on them in portal feature branches.

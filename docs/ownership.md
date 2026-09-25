# Domain Ownership & Boundary Matrix

To allow three developers to work concurrently in GitHub without stepping on each other's work or causing Git merge conflicts, this repository enforces strict directory-based domain ownership.

---

## 1. Domain Ownership Breakdown

```text
┌─────────────────────────┬───────────────────────────────────┬───────────────┐
│ Domain                  │ Primary Directory                 │ Primary Owner │
├─────────────────────────┼───────────────────────────────────┼───────────────┤
│ Trade Terminal          │ workflows/trade_terminal/         │ Developer 1   │
│ Admin Portal            │ workflows/admin_portal/           │ Developer 2   │
│ Client Portal           │ workflows/client_portal/          │ Developer 3   │
│ Shared Infrastructure   │ workflows/shared/                 │ All Devs      │
│ Configuration           │ config/                           │ All Devs      │
│ UI Regression Engine    │ ui_regression/                    │ Automation TL │
└─────────────────────────┴───────────────────────────────────┴───────────────┘
```

---

## 2. Developer 1 — Trade Terminal Domain

- **Primary Directory**: `workflows/trade_terminal/`
- **Subdirectories**:
  - `pages/`: Trade Terminal Page Objects (`login_page.py`, `trading_dashboard_page.py`, `order_entry_page.py`, `positions_page.py`)
  - `tests/`: Behavioral test suites for market orders, limit orders, chart interactions, watchlist selection, position lifecycle
  - `fixtures/`: `trade_fixtures.py` (authenticated trade contexts, trading pages)
  - `test_data/`: Instrument configurations, lot sizing fixtures, order parameters
  - `utils/`: Trade calculations, tick rounding, and order validation helpers
- **Execution Command**:
  ```bash
  pytest workflows/trade_terminal/
  # or: ./scripts/run_trade_tests.sh
  ```
- **Marker**: `@pytest.mark.trade`

---

## 3. Developer 2 — Admin Portal Domain

- **Primary Directory**: `workflows/admin_portal/`
- **Subdirectories**:
  - `pages/`: Admin Management Page Objects (`admin_login_page.py`, `admin_dashboard_page.py`, `user_management_page.py`)
  - `tests/`: Behavioral test suites for administrator authentication, role permissions, user search, deposit approvals, account settings
  - `fixtures/`: `admin_fixtures.py` (authenticated admin contexts, admin pages)
  - `test_data/`: Role matrices, mock administrative records, permission schemas
  - `utils/`: Admin navigation helpers, table row extractors, query utilities
- **Execution Command**:
  ```bash
  pytest workflows/admin_portal/
  # or: ./scripts/run_admin_tests.sh
  ```
- **Marker**: `@pytest.mark.admin`

---

## 4. Developer 3 — Client Portal Domain

- **Primary Directory**: `workflows/client_portal/`
- **Subdirectories**:
  - `pages/`: Client Portal Page Objects (`client_login_page.py`, `client_dashboard_page.py`, `client_watchlist_page.py`, `profile_page.py`)
  - `tests/`: Behavioral test suites for client registration, login, profile updates, KYC document uploads, deposit/withdrawal requests, symbol watchlists
  - `fixtures/`: `client_fixtures.py` (authenticated client contexts, client pages)
  - `test_data/`: Client profile fixtures, KYC test documents, deposit amounts
  - `utils/`: Client validation utilities, session recovery helpers
- **Execution Command**:
  ```bash
  pytest workflows/client_portal/
  # or: ./scripts/run_client_tests.sh
  ```
- **Marker**: `@pytest.mark.client`

---

## 5. Shared Infrastructure (`workflows/shared/`)

The shared directory contains framework-level primitives reused across all three portals:

- `workflows/shared/pages/base_page.py`: Universal base class with high-level Playwright wrappers.
- `workflows/shared/fixtures/`: Global browser lifecycle management (`browser_fixtures.py`) and auth caching (`auth_fixtures.py`).
- `workflows/shared/utils/`: Safe waiting logic (`waits.py`), failure screenshot capture (`screenshot.py`), logger (`logger.py`), and browser configuration (`browser.py`).
- `workflows/shared/constants/`: Standard timeouts (`timeouts.py`), viewports (`viewports.py`), canonical routes (`routes.py`).
- `workflows/shared/assertions/`: Domain-agnostic assertion wrappers (`assert_helpers.py`).
- `workflows/shared/test_data/`: Generic test data utilities like random email and string generators (`common_data.py`).

### Rules for Contributing to `shared/`
1. **Never Put Portal-Specific Code in Shared**: If a method, locator, or test datum is only used by one portal, it belongs in that portal's directory.
2. **Team Communication**: Before modifying existing classes or signatures in `workflows/shared/`, notify the team to prevent breaking other developers' active branches.
3. **Isolate Shared Changes**: When possible, submit shared framework additions as independent, focused Pull Requests before depending on them in portal feature branches.

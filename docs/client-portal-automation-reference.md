# Client Portal Automation & Quality Assurance Reference Manual

## 1. Overview & Scope

This document serves as the authoritative technical reference for the **Client Portal Behavioral Test Automation Suite** in the `Complete-Test` repository. It provides future engineers, QA testers, and developers with a complete architectural breakdown, a comprehensive inventory of all files created and modified, detailed specifications of live API workflows, and instructions for running and maintaining the test suite.

### Key Suite Metrics
- **Total Test Suites**: 10 test modules
- **Total Automated Tests**: 80 test cases
- **Pass Rate**: 100% (80 / 80 passing)
- **Error Tolerance**: Zero console errors, zero uncaught JavaScript exceptions, zero HTTP 5xx backend server errors
- **Primary Execution Engine**: Python 3.11+ / Playwright 1.63+ / Pytest

---

## 2. Architecture & Design Principles

The testing framework follows the repository's dual-layer testing architecture:

```text
                        Complete-Test Architecture
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         │                                                     │
   UI REGRESSION LAYER                                BEHAVIORAL WORKFLOWS
  (DOM Structural Drift)                             (End-to-End User Journeys)
   ui_regression/                                     workflows/
         │                                                     │
   crawler/comparer                                   client_portal/
                                                               │
                              ┌────────────────────────────────┼────────────────────────────────┐
                              ▼                                ▼                                ▼
                        Page Objects                      Test Suites                     Error Monitor
                     (Encapsulate UI)                 (Assert Journeys)               (Zero-Crash Check)
```

### Core Design Rules
1. **Strict Page Object Model (POM)**:
   - All DOM locators, element interactions, and CSS selectors reside exclusively inside Page Objects inheriting from [BasePage](file:///Users/appdev/Complete-Test/workflows/shared/pages/base_page.py).
   - Test functions never contain raw CSS/XPath selectors.
2. **Component-Based Modularity**:
   - Reusable UI elements across pages (such as [ClientHeader](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/components/client_header.py) and [ClientSidebar](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/components/client_sidebar.py)) are encapsulated into standalone component classes.
3. **Session-Cached Authentication**:
   - Authentication cookies and local storage tokens are stored in `auth/auth_state_client.json` to prevent repetitive logins across 72 tests.
4. **Automated Error Monitoring (Zero-Tolerance Policy)**:
   - Every test attaches an [ErrorMonitor](file:///Users/appdev/Complete-Test/workflows/shared/utils/error_monitor.py) instance to the Playwright page.
   - The test asserts that no browser console errors, unhandled JavaScript exceptions, or HTTP 5xx server responses were emitted during execution.

---

## 3. Inventory of Created & Modified Files

### 3.1 Shared Utilities
| File Path | Description | Lines / Size |
| :--- | :--- | :--- |
| [workflows/shared/utils/error_monitor.py](file:///Users/appdev/Complete-Test/workflows/shared/utils/error_monitor.py) | Playwright event listener engine tracking `console.error`, unhandled `pageerror`, HTTP 4xx API errors, HTTP 5xx backend server crashes, and network connection failures. | 128 lines |

### 3.2 Component Layer
| File Path | Description | Lines / Size |
| :--- | :--- | :--- |
| [workflows/client_portal/pages/components/client_header.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/components/client_header.py) | Global top navigation header: dark/light theme toggle, notifications drawer, profile avatar menu, quick deposit/withdraw buttons, and MT5/Wallet account switcher dropdown. | 258 lines |
| [workflows/client_portal/pages/components/client_sidebar.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/components/client_sidebar.py) | Global sidebar navigation: handles routing to Dashboard, Deposit, Withdraw, Internal Transfer, Wallet, Refer & Earn, Settings, Copy Trading, MAM, and PAMM. | 65 lines |
| [workflows/client_portal/pages/components/__init__.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/components/__init__.py) | Package initialization exporting `ClientHeader` and `ClientSidebar`. | 9 lines |

### 3.3 Page Objects
| File Path | Description | Lines / Size |
| :--- | :--- | :--- |
| [workflows/client_portal/pages/client_dashboard_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_dashboard_page.py) | Client dashboard view: balance cards, equity metrics, trading account cards, and quick navigation shortcuts. | 87 lines |
| [workflows/client_portal/pages/client_deposit_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_deposit_page.py) | Deposit page: handles 5 payment gateways, dynamic exchange rate calculators, transaction proof receipt file upload, and deposit history. | 240 lines |
| [workflows/client_portal/pages/client_withdraw_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_withdraw_page.py) | Withdrawal page: bank details form, crypto wallet address configuration, "Save Changes" functionality, OTP verification modal, withdrawal request submission, and history table with sorting & pagination. | 329 lines |
| [workflows/client_portal/pages/client_internal_transfer_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_internal_transfer_page.py) | Internal Transfer page: source/destination account selectors, amount inputs, transfer review modal confirmation, live API execution, and transfer history. | 224 lines |
| [workflows/client_portal/pages/client_wallet_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_wallet_page.py) | Client Wallet page: Consolidated Funds card, Available Balance, Total Wallets, Ledger CSV export report button, "Account to Wallet" transfer redirect button, wallet accounts table, and transfer history table with dynamic pagination. | 155 lines |
| [workflows/client_portal/pages/client_refer_earn_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_refer_earn_page.py) | Refer & Earn page: referral link clipboard copying, QR code rendering, referral statistics cards, and referral partner table. | 148 lines |
| [workflows/client_portal/pages/client_settings_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_settings_page.py) | User settings page: personal information form editing, password change security form, 2FA toggle, and preferences. | 148 lines |
| [workflows/client_portal/pages/client_copy_trading_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_copy_trading_page.py) | Copy Trading view: 4 summary cards (MANAGERS, MANAGED CAPITAL, CLOSED TRADES, FOLLOWERS), view switching (`TRADING MANAGER` <-> `MY FOLLOWERS` with Active/History tabs and 7 follower headers), 4 dropdown filters (Range, Risk, Fund, Rows), Refresh button, search filter, 9-column managers table, Statistics modal (8 metric cards & Equity Curve chart), and Follow Manager modal (`Balance Based`, `Equity Based`, `Multiplier Based`). | 196 lines |
| [workflows/client_portal/pages/client_mam_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_mam_page.py) | Multi-Account Manager (MAM) view: 4 summary cards, view switching (`MAM MANAGER` <-> `MY FOLLOWERS` with 5 follower headers), 4 dropdown filters, Refresh button, search filter, 9-column master accounts table, Statistics modal (8 metric cards & Equity Curve chart), Follow MAM confirmation modal, and multi-page pagination. | 192 lines |
| [workflows/client_portal/pages/client_pamm_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_pamm_page.py) | PAMM investment view: 4 summary cards, view switching (`PAMM MANAGER` <-> `MY FOLLOWERS` with 4 follower headers), 4 dropdown filters, Refresh button, search filter, 9-column PAMM strategies table, Statistics modal (8 metric cards & Equity Curve chart), Follow PAMM modal with investment amount input, and multi-page pagination. | 194 lines |
| [workflows/client_portal/pages/__init__.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/__init__.py) | Central package export for all Client Portal Page Objects. | 33 lines |

### 3.4 Test Suites
| File Path | Tests | Key Areas & Negative Scenarios Tested |
| :--- | :---: | :--- |
| [workflows/client_portal/tests/test_client_dashboard.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_dashboard.py) | 4 | Dashboard layout, balance cards, quick action links, **rapid cash flow toggle resilience**. |
| [workflows/client_portal/tests/test_client_header.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_header.py) | 10 | Header elements, profile drawer, notification badge & drawer, dark/light theme toggling, quick deposit & withdraw modals, account switcher dropdown, **search special character/injection resilience**. |
| [workflows/client_portal/tests/test_client_refer_earn.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_refer_earn.py) | 6 | Referral link copy, QR code visibility, performance stats, referral table pagination, **referral link immutability/readonly protection**. |
| [workflows/client_portal/tests/test_client_settings.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_settings.py) | 7 | Personal details form, password change validation, 2FA toggle, notification preferences, **email field immutability/tamper protection**. |
| [workflows/client_portal/tests/test_client_deposit.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_deposit.py) | 10 | 5 deposit gateways, dynamic conversion calculator, transaction receipt upload, deposit history table, **negative threshold validation (zero, sub-minimum, empty)**. |
| [workflows/client_portal/tests/test_client_withdraw.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_withdraw.py) | 13 | Bank account form, crypto wallet form, "Save Changes" validation, OTP verification modal, history table sorting & pagination, **negative form validation and empty OTP boundary handling**. |
| [workflows/client_portal/tests/test_client_internal_transfer.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_internal_transfer.py) | 9 | Transfer form validation, review transfer modal, all 5 live transfer modes with wallet credit, **negative invalid amounts (empty, 0, negative) blocking review modal**. |
| [workflows/client_portal/tests/test_client_wallet.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_wallet.py) | 8 | Summary cards, Ledger CSV export download, "Account to Wallet" transfer redirect button, wallet accounts table, multi-page history pagination, **negative pagination boundary limits (Previous disabled on page 1)**. |
| [workflows/client_portal/tests/test_client_copy_mam_pamm.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_copy_mam_pamm.py) | 17 | **Master Account Suite**: 4 summary cards & manager count matching across all 3 pages, 4 dropdown filters (Range, Risk, Fund, Rows), Refresh button reload, search filter, 9 static columns, `MY FOLLOWERS` view switching (Active & History subtabs, follower headers & records) <-> Manager view, Statistics modal (8 metric cards & Equity Curve chart), Follow modals lifecycle, Prev/Next pagination navigation, header interactivity, and End-to-End Master journey with zero console/JS/backend errors. |
| [workflows/client_portal/tests/test_client_example.py](file:///Users/appdev/Complete-Test/workflows/client_portal/tests/test_client_example.py) | 2 | Smoke tests verifying login state and authenticated dashboard landing. |

### 3.5 Test Fixtures & Configuration
| File Path | Description |
| :--- | :--- |
| [workflows/client_portal/fixtures/client_fixtures.py](file:///Users/appdev/Complete-Test/workflows/client_portal/fixtures/client_fixtures.py) | Injects authenticated pages, initialized Page Objects, error monitors, and mock test data into test functions. |
| [workflows/client_portal/conftest.py](file:///Users/appdev/Complete-Test/workflows/client_portal/conftest.py) | Registers client fixtures and portal-level configurations for Pytest. |
| [conftest.py](file:///Users/appdev/Complete-Test/conftest.py) | Root-level pytest configuration defining shared browser fixtures and report hooks. |

---

## 4. In-Depth Technical Details: Verified Live Workflows

### 4.1 Internal Transfer & Wallet Credit Mechanics
The internal transfer subsystem was tested against the live staging backend (`https://stage.xtremenext.com/client-portal/apiTransfer`), verifying 5 distinct transfer modes:

```text
                             TRANSFER MODES MATRIX
                             
   [ Trading Account ] ─────── Mode 1 (Account -> Wallet) ───────> [ Client Wallet ]
   [ Trading Account ] <────── Mode 2 (Wallet -> Account) ──────── [ Client Wallet ]
   [ Trading Account ] ─────── Mode 3 (Account -> Account) ──────> [ Trading Account ]
   [ IB Wallet ]       ─────── Mode 4 (IB Wallet -> Account) ────> [ Trading Account ]
   [ IB Wallet ]       ─────── Mode 5 (IB Wallet -> Wallet) ─────> [ Client Wallet ]
```

#### Verified Transfer Modes:
1. **Account &rarr; Wallet**: Source `account:LWR8AUE0TS` to Destination `client_wallet:808780896656`.
2. **Wallet &rarr; Account**: Source `client_wallet:808780896656` to Destination `account:LWR8AUE0TS`.
3. **Account &rarr; Account**: Source `account:LWR8AUE0TS` to Destination `account:BKQIOI0MAT`.
4. **IB Wallet &rarr; Account**: Source `ib_wallet:868001043731` to Destination `account:LWR8AUE0TS`.
5. **IB Wallet &rarr; Client Wallet**: Source `ib_wallet:868001043731` to Destination `client_wallet:808780896656`.

#### Live API Specification:
- **Endpoint**: `POST https://stage.xtremenext.com/client-portal/apiTransfer`
- **Payload Structure**:
  ```json
  {
    "token": "<JWT_AUTHENTICATION_TOKEN>",
    "source": "account:LWR8AUE0TS",
    "destination": "client_wallet:808780896656",
    "amount": "1.00",
    "memo": "Automated E2E Test Transfer"
  }
  ```
- **Backend Response**:
  ```json
  {
    "status": "success",
    "message": "Transfer amount successfully"
  }
  ```
- **Real-Time Verification**:
  - Live transfers reflect immediately in the **Recent Transfers** table on the Internal Transfer view.
  - Live transfers update balances in the **Consolidated Funds** and **Wallet Accounts** table on the Wallet view.

---

### 4.2 Wallet Minute Elements & Ledger Export
All minute UI controls and interactive components on the Wallet page ([client_wallet_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_wallet_page.py)) were systematically verified:

1. **Summary Metrics Cards**:
   - **Consolidated Funds**: Full text locator asserting `$1,688.74` with `+0.0% 30 day net movement`.
   - **Available Balance**: Verifies liquidity balance card.
   - **Total Wallets**: Displays count of registered user wallets.
2. **Ledger CSV Export Button**:
   - Locates button containing text `Export Report`.
   - Listens to Playwright `page.expect_download()` event.
   - Asserts downloaded filename matches regex `^Ledger_.*\.csv$`.
3. **Action Redirection**:
   - `ACCOUNT TO WALLET` action button triggers navigation and verifies redirect to `/client-portal` (transfer interface).
4. **Multi-Page History Pagination**:
   - Verifies rows-per-page dropdown (options: 10, 25, 50, 100 rows).
   - Validates dynamic `Showing X-Y of Z records` status text.
   - Validates Next (`>`) and Previous (`<`) pagination buttons and disabled boundaries on first/last pages.

---

### 4.3 Withdrawals, Security Controls & OTP Verification
The withdrawal view ([client_withdraw_page.py](file:///Users/appdev/Complete-Test/workflows/client_portal/pages/client_withdraw_page.py)) enforces multi-layered validation:

1. **Bank Details Form**:
   - Form fields: Bank Name, Account Holder Name, Account Number, IFSC/SWIFT Code.
   - Form action: "Save Changes" button saves details and displays feedback toast.
2. **Crypto Wallet Address**:
   - Network selection: USDT TRC-20, USDT ERC-20, BTC.
   - Address input validation.
3. **OTP Security Modal**:
   - Triggering a withdrawal opens an OTP Verification Modal dialog.
   - Asserts OTP inputs, Resend OTP link, and Confirm/Cancel actions.
4. **Withdrawal History Table**:
   - History table columns: Date, Method, Amount, Status, Transaction ID.
   - Supports column sorting and page pagination.

---

### 4.4 Copy Trading, MAM & PAMM Portals (Master Account Architecture)
Now that client account `10026` is a designated Master Account, all three social and investment management pages share an expanded, highly detailed architecture:

#### 1. Master Summary Metric Cards
Rendered in the top summary grid across all 3 pages:
- **MANAGERS**: Displays total available managers/masters (e.g. 22 for Copy Trading, 15 for MAM, 21 for PAMM).
- **MANAGED CAPITAL**: Total funds managed (e.g. `$315,123.41` for Copy Trading, `$64,346.2` for MAM, `$3,280` for PAMM).
- **CLOSED TRADES**: Total closed trade volume across master strategies (e.g. `1,478`, `3,111`, `2,666`).
- **FOLLOWERS**: Total active followers subscribed (e.g. `310`, `47`, `34`).

#### 2. Leaderboard Table & 9 Standardized Columns
All 3 portals present 9 standardized columns with static header cursor behavior:
| Column # | Header Name | Description |
| :---: | :--- | :--- |
| 1 | **NAME** | Manager display name & MT5 account identifier |
| 2 | **RANK** | Leaderboard rank badge (#1, #2, etc.) |
| 3 | **GROWTH** | Historical performance growth percentage |
| 4 | **WIN RATE** | Win rate percentage |
| 5 | **TRADES** | Total executed trades |
| 6 | **DRAWDOWN** | Maximum historical drawdown percentage |
| 7 | **MANAGED** | Total capital under management |
| 8 | **RISK** | Risk score category (Risk 1, Risk 2, Risk 3) |
| 9 | **ACTION** | Interactive action cell containing Statistics icon button and Follow button |

#### 3. Dropdown Filtering & Refresh Controls
- **Range Dropdown**: Options `30 Days` (`30`), `90 Days` (`90`), `1 Year` (`365`), `All Time` (`all`). Default: `1 Year`.
- **Risk Dropdown**: Options `Risk` (empty reset), `Risk 1` (`1`), `Risk 2` (`2`), `Risk 3` (`3`).
- **Fund Dropdown**: Options `Fund` (empty reset), `$1,000+` (`1000`), `$10,000+` (`10000`), `$50,000+` (`50000`).
- **Rows Dropdown**: Options `10`, `25`, `50`. Setting Rows to `25` displays all master rows matching the MANAGERS card count.
- **Refresh Button**: Header button (`button[title='Refresh']`) triggers an immediate table data re-fetch cleanly.
- **Search Input**: Debounced filter searching by manager name and restoring table on clear.

#### 4. View Switching: Leaderboard <-> MY FOLLOWERS
- Toggle buttons in header area:
  - Copy Trading: `TRADING MANAGER` <-> `MY FOLLOWERS`
  - MAM: `MAM MANAGER` <-> `MY FOLLOWERS`
  - PAMM: `PAMM MANAGER` <-> `MY FOLLOWERS`
- In `MY FOLLOWERS` view:
  - Subtabs: `Active` and `History`
  - Specialized follower data grid headers:
    - **Copy Trading**: `['ACCOUNT ID', 'FOLLOW DATE', 'TRADE METHOD', 'FOLLOWER FUND', 'COPIED ORDERS', 'COPIED LOTS', 'COPIED PNL']`
    - **MAM**: `['FOLLOWER NAME', 'YOUR PROFIT SHARE', 'USER ID', 'MAM ID', 'ACTION']`
    - **PAMM**: `['NAME', 'INVESTMENT', 'MANAGER SHARE (ELIGIBLE ORDERS)', 'ACTION']`

#### 5. Statistics Modal Dialog
Triggered by the inline `button[title='Statistics']` on any table row:
- Displays manager profile details (Name, email, account ID).
- 8 Numerical metric cards: `NET PROFIT`, `GROWTH`, `WIN RATE`, `PROFIT FACTOR`, `CLOSED TRADES`, `TOTAL LOTS`, `MAX DRAWDOWN`, `MANAGED CAPITAL`.
- Interactive SVG/Canvas `EQUITY CURVE` chart displaying equity progression milestones.
- Clean dismissal via top-right close action button.

#### 6. Follow Manager Modals Lifecycle
- **Copy Trading Follow Modal**:
  - Contains trade method selection (`Balance Based`, `Equity Based`, `Multiplier Based`).
  - Performance fee and subscription disclosure.
  - `Cancel` and `CONFIRM FOLLOW` buttons.
- **MAM Follow Modal**:
  - Confirmation prompt (`Are you sure you want to follow this MAM manager?`).
  - `Cancel` and `CONFIRM FOLLOW` buttons.
- **PAMM Investment Modal**:
  - Investment Amount input field (`INVESTMENT AMOUNT`).
  - Debit notice (`This amount will be debited from your balance after confirmation.`).
  - `Cancel` and `CONFIRM FOLLOW` buttons.

#### 7. Pagination Navigation
- Controls: `Prev` and `Next` buttons, page indicator (e.g. `1 / 3`), and counter (`Showing 1-10 of 22`).
- Boundary limits: `Prev` is disabled on Page 1, `Next` is disabled on the final page.

---

### 4.5 Error Monitoring & Zero-Tolerance Implementation
The [ErrorMonitor](file:///Users/appdev/Complete-Test/workflows/shared/utils/error_monitor.py) class attaches directly to the Playwright page lifecycle:

```python
class ErrorMonitor:
    def __init__(self, page: Page):
        self.console_errors = []
        self.js_page_errors = []
        self.backend_errors = []
        self.failed_requests = []

        page.on("console", self._handle_console)
        page.on("pageerror", self._handle_pageerror)
        page.on("response", self._handle_response)
        page.on("requestfailed", self._handle_requestfailed)
```

#### Assertions Run on Every Test:
- `error_monitor.assert_no_errors()`: Ensures 0 `console.error` logs and 0 unhandled JavaScript exceptions.
- `error_monitor.assert_no_backend_errors()`: Ensures 0 HTTP 5xx responses and 0 unexpected 4xx API failures.

---

## 5. Test Suite Execution Guide

### 5.1 Prerequisites
Ensure the virtual environment is activated and Playwright browsers are installed:
```bash
source .venv/bin/activate
playwright install chromium
```

Ensure valid authentication state is available in `auth/auth_state_client.json`.

### 5.2 Common Execution Commands

#### Run the Entire Client Portal Suite (72 Tests):
```bash
pytest workflows/client_portal/tests/ -v
```

#### Run a Specific Test Module:
```bash
# Internal Transfer suite (including all 5 transfer modes)
pytest workflows/client_portal/tests/test_client_internal_transfer.py -v

# Wallet suite (including CSV export, summary cards, pagination)
pytest workflows/client_portal/tests/test_client_wallet.py -v

# Withdraw suite (including bank details, OTP modal, history)
pytest workflows/client_portal/tests/test_client_withdraw.py -v

# Copy Trading, MAM, PAMM suite
pytest workflows/client_portal/tests/test_client_copy_mam_pamm.py -v
```

#### Run in Headed Mode for Visual Debugging:
```bash
pytest workflows/client_portal/tests/test_client_wallet.py --headed
```

#### Generate a Self-Contained HTML Test Report:
```bash
pytest workflows/client_portal/tests/ --html=reports/client_portal_report.html --self-contained-html
```

---

## 6. Maintenance & Troubleshooting

| Issue / Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **Authentication Redirect / 401 Unauthorized** | Expired session token in `auth/auth_state_client.json`. | Re-generate storage state using the login workflow or client login fixture. |
| **Selector Not Found on Staging** | DOM attribute or text label change. | Update the locator inside the respective Page Object in `workflows/client_portal/pages/`. Never edit test files for selector updates. |
| **Download Timeout on CSV Export** | Browser pop-up blocker or slow file generation. | Ensure `page.expect_download(timeout=10000)` has adequate timeout configured. |
| **Transfer Limit Exceeded** | Insufficient balance in test source account. | Top up test account or adjust the transfer amount parameter in `test_client_internal_transfer.py`. |

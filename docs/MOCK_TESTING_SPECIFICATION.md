# Mock Testing Specification & Team Implementation Guide

This document is the **definitive implementation guide and technical specification** for authoring and running **Mock Tests** across all three portals (**Trade Terminal**, **Admin Portal**, and **Client Portal**). Any developer on the team can pick up mock testing tasks for any domain using this common reference.

---

## 📑 Table of Contents
1. [Overview & Philosophy](#1-overview--philosophy)
2. [Mock Testing vs Live Workflow Testing](#2-mock-testing-vs-live-workflow-testing)
3. [Architecture & How Network Interception Works](#3-architecture--how-network-interception-works)
4. [Shared Mocking Infrastructure](#4-shared-mocking-infrastructure)
   - [MockRouter API](#mockrouter-api)
   - [Centralized Mock Datasets (`mock_data`)](#centralized-mock-datasets-mock_data)
   - [Pre-configured Scenarios (`MockScenarios`)](#pre-configured-scenarios-mockscenarios)
5. [Directory Layout & File Structure](#5-directory-layout--file-structure)
6. [How to Author a Mock Test (Step-by-Step)](#6-how-to-author-a-mock-test-step-by-step)
7. [Portal-by-Portal Mock Test Catalog](#7-portal-by-portal-mock-test-catalog)
   - [Trade Terminal Mock Suites](#trade-terminal-mock-suites)
   - [Admin Portal Mock Suites](#admin-portal-mock-suites)
   - [Client Portal Mock Suites](#client-portal-mock-suites)
8. [CLI Execution & Debugging](#8-cli-execution--debugging)
9. [Best Practices & Troubleshooting](#9-best-practices--troubleshooting)

---

## 1. Overview & Philosophy

In standard end-to-end (E2E) testing, tests communicate directly with live staging backend servers and databases. While essential for overall platform integration, live tests have inherent limitations:
- **Flakiness from Backend/Network**: Staging servers might reboot, rate-limit, or drop connections.
- **Database Mutation Constraints**: Cannot easily test deleting super-admins or wiping trading accounts without corrupting shared test environments.
- **Edge-Case Difficulty**: Simulating HTTP `500 Internal Server Error`, `504 Gateway Timeout`, or `429 Rate Limiting` against live servers requires intrusive fault injection.

**Mock Testing** solves this by intercepting browser HTTP/XHR/Fetch requests at the Playwright network layer. The browser interacts with a **deterministic mock layer** instead of live servers, enabling:
- **100% Offline & Isolated Execution**: Runs anywhere in sub-second speeds with zero database dependency.
- **Extreme Fault Injection**: Instantly test server crashes, maintenance modes, and malformed responses.
- **Zero Live DB Mutations**: Safe to test aggressive deletion, account termination, and high-volume operations.

---

## 2. Mock Testing vs Live Workflow Testing

| Dimension | Mock Tests (`@pytest.mark.mock`) | Live Workflow Tests (`@pytest.mark.workflow`) |
| :--- | :--- | :--- |
| **Network Destination** | Intercepted in-memory by Playwright (`page.route()`) | Sent over network to staging/live servers |
| **Backend State Required** | None (100% offline & self-contained) | Live backend, active DB, seeded accounts |
| **Execution Speed** | Sub-second per scenario (< 100ms) | 2–10 seconds per user journey |
| **Failure Scope** | Frontend UI handling, state transitions, rendering logic | Full stack (UI + API + DB + Third-party gateways) |
| **Primary Use Cases** | Error banners, boundary rendering, 4xx/5xx handling, empty states, offline UI | Real-money lifecycle, multi-system synchronization |

---

## 3. Architecture & How Network Interception Works

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MOCK TESTING EXECUTION                          │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                   Playwright Browser Context / Page
                                   │
                   [Network Request: GET/POST/PUT/DELETE]
                                   │
                                   ▼
             ┌───────────────────────────────────────────┐
             │    Playwright Route Interceptor Layer     │
             │   (page.route() / context.route())        │
             └───────────────────────────────────────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  ▼                                 ▼
       [Matched Mock Pattern]             [Unmatched / Static Asset]
                  │                                 │
                  ▼                                 ▼
      ┌───────────────────────┐            ┌─────────────────┐
      │ Mock Registry & Data  │            │ Pass Through or │
      │ Fixtures (JSON / DTO) │            │ Cache (CSS/JS)  │
      └───────────────────────┘            └─────────────────┘
                  │
                  ▼
     route.fulfill(
         status=200/400/500,
         content_type="application/json",
         json=mock_response,
     )
                  │
                  ▼
      Browser UI renders mocked state without ever reaching real backend!
```

---

## 4. Shared Mocking Infrastructure

All core mocking utilities are located under `workflows/shared/mocks/`.

### MockRouter API
The `MockRouter` class (`workflows/shared/mocks/mock_router.py`) provides high-level routing methods:

```python
from workflows.shared.mocks.mock_router import MockRouter

# 1. Mock JSON Success or Payload
mock_router.mock_json("**/api/v1/orders**", {"order_id": 12345, "status": "FILLED"}, status=200)

# 2. Mock Standard Server Errors (500, 502, 504, 403, etc.)
mock_router.mock_error("**/api/v1/orders**", status=500, error_message="Order Matching Engine Offline")

# 3. Simulate Network Dropout / Offline State
mock_router.mock_abort("**/api/**", error_code="internetdisconnected")

# 4. Simulate Network Latency (Slow 3G / Spinner UI validation)
mock_router.mock_json("**/api/v1/reports**", {"data": []}, delay_ms=2000)

# 5. Capture Request Headers and Payloads for Assertions
mock_router.capture_requests("**/api/v1/transfer**", mock_response_data={"success": True})
# After clicking UI:
requests = mock_router.captured_requests
assert requests[0]["post_data"]["amount"] == 500
```

### Centralized Mock Datasets (`mock_data`)
Pre-built, typed datasets are available under `workflows/shared/mocks/mock_data/`:
- **`auth_mocks.py`**: `MOCK_LOGIN_SUCCESS`, `MOCK_ADMIN_LOGIN_SUCCESS`, `MOCK_LOGIN_INVALID_CREDENTIALS`, `MOCK_LOGIN_ACCOUNT_LOCKED`, `MOCK_2FA_REQUIRED`.
- **`trade_mocks.py`**: `MOCK_WATCHLIST_SYMBOLS`, `MOCK_ACCOUNT_METRICS`, `MOCK_ZERO_BALANCE_METRICS`, `MOCK_OPEN_POSITIONS`, `MOCK_ORDER_SUCCESS_RESPONSE`, `MOCK_ORDER_REJECTED_MARGIN`, `MOCK_MARKET_CLOSED_RESPONSE`.
- **`admin_mocks.py`**: `MOCK_ADMIN_USER_LIST`, `MOCK_KYC_DOCUMENTS_QUEUE`, `MOCK_PENDING_DEPOSITS`, `MOCK_ACTION_SUCCESS`, `MOCK_ACTION_PERMISSION_DENIED`.
- **`client_mocks.py`**: `MOCK_CLIENT_WALLET_SUMMARY`, `MOCK_PAYMENT_GATEWAYS`, `MOCK_WITHDRAWAL_SUBMIT_SUCCESS`, `MOCK_INTERNAL_TRANSFER_SUCCESS`, `MOCK_LEADERBOARD_MANAGERS`.
- **`error_mocks.py`**: `HTTP_400_BAD_REQUEST`, `HTTP_401_UNAUTHORIZED`, `HTTP_403_FORBIDDEN`, `HTTP_404_NOT_FOUND`, `HTTP_422_UNPROCESSABLE_ENTITY`, `HTTP_429_TOO_MANY_REQUESTS`, `HTTP_500_INTERNAL_SERVER_ERROR`, `HTTP_502_BAD_GATEWAY`, `HTTP_503_SERVICE_UNAVAILABLE`, `HTTP_504_GATEWAY_TIMEOUT`.

### Pre-configured Scenarios (`MockScenarios`)
Located in `workflows/shared/mocks/mock_scenarios.py`:
- `MockScenarios.apply_offline_mode(mock_router)`
- `MockScenarios.apply_maintenance_mode(mock_router)`
- `MockScenarios.apply_zero_balance_state(mock_router)`
- `MockScenarios.apply_vip_trader_state(mock_router)`

---

## 5. Directory Layout & File Structure

```text
workflows/
├── shared/
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── mock_router.py              # Core route interception helper
│   │   ├── mock_scenarios.py           # Reusable scenario presets
│   │   └── mock_data/                  # Standard mock JSON/Python dict payloads
│   │       ├── __init__.py
│   │       ├── auth_mocks.py
│   │       ├── trade_mocks.py
│   │       ├── admin_mocks.py
│   │       ├── client_mocks.py
│   │       └── error_mocks.py
│   └── fixtures/
│       └── mock_fixtures.py            # mock_router, mock_context, mock_page
│
├── trade_terminal/
│   └── tests/
│       └── mock/                       # Trade Terminal Mock Suites
│           ├── test_mock_trade_order_execution.py
│           ├── test_mock_trade_server_errors.py
│           └── ...
│
├── admin_portal/
│   └── tests/
│       └── mock/                       # Admin Portal Mock Suites
│           ├── test_mock_admin_user_crud.py
│           ├── test_mock_admin_server_failures.py
│           └── ...
│
└── client_portal/
    └── tests/
        └── mock/                       # Client Portal Mock Suites
            ├── test_mock_client_deposit_withdraw.py
            ├── test_mock_client_network_failures.py
            └── ...
```

---

## 6. How to Author a Mock Test (Step-by-Step)

### Step 1: Import Fixtures and Data
```python
import pytest
from playwright.sync_api import Page, expect
from workflows.shared.mocks.mock_router import MockRouter
from workflows.shared.mocks.mock_data import client_mocks, error_mocks
from workflows.client_portal.pages.client_deposit_page import ClientDepositPage
```

### Step 2: Decorate with Markers
Always tag mock tests with `@pytest.mark.mock` and the portal marker (`@pytest.mark.client`, `@pytest.mark.admin`, or `@pytest.mark.trade`):
```python
@pytest.mark.mock
@pytest.mark.client
def test_mock_deposit_gateway_500_error(mock_router: MockRouter, workflow_page: Page):
    """Verify that when deposit gateway crashes with 500, UI renders an error banner."""
```

### Step 3: Register Mock Routes BEFORE Triggering UI Actions
```python
    # Intercept payment gateway submission
    mock_router.mock_error(
        "**/api/deposit/process**",
        status=500,
        error_message="Payment Gateway Temporary Unavailable",
    )
```

### Step 4: Interact with Page Object and Assert
```python
    deposit_page = ClientDepositPage(workflow_page)
    deposit_page.goto_deposit()
    deposit_page.submit_deposit(amount=250, gateway="USDT")
    
    # Assert UI handled error gracefully
    expect(deposit_page.error_banner).to_be_visible()
    expect(deposit_page.error_banner).to_contain_text("Payment Gateway Temporary Unavailable")
```

---

## 7. Portal-by-Portal Mock Test Catalog

Here is the implementation roadmap of mock tests across all three portals. Any team member can implement any of these test cases:

### Trade Terminal Mock Suites (`workflows/trade_terminal/tests/mock/`)
- [ ] **Order Execution**:
  - `test_mock_market_buy_success`: Successful buy fill with custom ticket ID.
  - `test_mock_market_sell_success`: Successful sell fill with custom execution price.
  - `test_mock_insufficient_margin_error`: HTTP 400 Insufficient margin toast.
  - `test_mock_market_halted_warning`: HTTP 400 Market closed alert.
  - `test_mock_order_rate_limit_429`: HTTP 429 Rapid order placement warning.
- [ ] **Account Metrics & PnL**:
  - `test_mock_account_balance_zero`: Zero balance rendering, disables Trade button.
  - `test_mock_high_floating_pnl_equity`: Live equity calculation with floating profit.
  - `test_mock_margin_call_warning_level`: Margin level < 100% warning banner.
- [ ] **Watchlist & Quotes**:
  - `test_mock_watchlist_empty_state`: Empty watchlist search message.
  - `test_mock_watchlist_spread_formatting`: Spread and tick rendering accuracy.
- [ ] **Server Resilience**:
  - `test_mock_trade_server_500_banner`: Server 500 crash notification.
  - `test_mock_trade_server_503_maintenance`: Scheduled maintenance overlay.
  - `test_mock_trade_gateway_timeout_504`: Upstream liquidity timeout warning.
  - `test_mock_trade_network_offline`: Browser offline banner.

### Admin Portal Mock Suites (`workflows/admin_portal/tests/mock/`)
- [ ] **User Management**:
  - `test_mock_admin_user_table_pagination`: 100+ mocked user records traversal.
  - `test_mock_admin_user_filter_by_group`: Filtering VIP vs Standard accounts.
  - `test_mock_admin_create_user_success`: Form submit 200 and table refresh.
  - `test_mock_admin_create_user_duplicate_email`: 422 Duplicate email validation error.
- [ ] **KYC & Document Verification**:
  - `test_mock_admin_kyc_queue_empty`: "No pending KYC documents" placeholder.
  - `test_mock_admin_kyc_approve_success`: Immediate status update to VERIFIED.
  - `test_mock_admin_kyc_reject_with_remarks`: Status update to REJECTED with note.
- [ ] **Deposits & Withdrawals Queue**:
  - `test_mock_admin_approve_deposit_instant_sync`: Approval updates balance.
  - `test_mock_admin_reject_withdrawal_refund`: Rejection returns funds to wallet.
- [ ] **Security & Role Permissions**:
  - `test_mock_admin_read_only_manager_action_denied`: 403 Forbidden alert.
  - `test_mock_admin_audit_log_capture`: Verify user ID and timestamp captured.

### Client Portal Mock Suites (`workflows/client_portal/tests/mock/`)
- [x] **Authentication & Security** (`test_mock_client_auth_security.py`):
  - `test_mock_client_login_success`: Mock JWT session injection and profile retrieval.
  - `test_mock_client_login_invalid_password`: HTTP 401 Invalid credentials banner.
  - `test_mock_client_login_account_suspended`: HTTP 403 Account locked alert.
  - `test_mock_client_2fa_otp_screen`: 2FA prompt navigation and verification challenge.
  - `test_mock_client_session_expiration_401`: Auto-redirect to login on expired token.
  - `test_mock_client_user_signup_success`: User registration submit 200 OK.
  - `test_mock_client_user_signup_duplicate_email`: HTTP 409 duplicate email conflict error.
  - `test_mock_client_password_reset_dispatch`: Password reset email trigger 200 OK.
  - `test_mock_client_password_reset_user_not_found`: HTTP 404 unrecognized user email.
- [x] **Dashboard Workspace & Metrics** (`test_mock_client_dashboard.py`):
  - `test_mock_client_dashboard_metrics_render`: 4 primary summary metric cards (Total Funds, Balance, Buffer, Referrals).
  - `test_mock_client_dashboard_zero_metrics`: $0.00 zero-balance state for brand-new users.
  - `test_mock_client_dashboard_high_net_worth_formatting`: High Net Worth figure formatting ($15,000,000.00+).
  - `test_mock_client_dashboard_cash_flow_period_filter`: Account Cash Flow period filtering (Day, Week, Month).
  - `test_mock_client_dashboard_loading_delay_skeleton`: Skeleton loader resilience with 500ms network latency.
  - `test_mock_client_dashboard_cashflow_500_resilience`: Cash flow 500 failure resilience without crashing dashboard cards.
- [x] **Deposits, Gateways & Funding Boundaries** (`test_mock_client_deposit_withdraw.py`):
  - `test_mock_client_dynamic_gateways_render`: Dynamic payment method cards rendering.
  - `test_mock_client_deposit_minimum_boundary`: HTTP 422 minimum threshold error (< $10).
  - `test_mock_client_deposit_maximum_boundary_error`: HTTP 422 upper threshold limit (> $100,000).
  - `test_mock_client_deposit_crypto_address_generation`: Dynamic TRC20/BEP20 crypto address & QR generator.
  - `test_mock_client_deposit_proof_upload_failure`: HTTP 500 payment proof upload error.
  - `test_mock_client_deposit_gateway_500`: Payment provider offline notification.
  - `test_mock_client_deposit_history_populated_ledger`: Populated deposit transaction history ledger & badges.
  - `test_mock_client_deposit_history_empty_state`: Empty state placeholder when user has 0 deposit records.
  - `test_mock_client_deposit_history_pagination`: 50+ records pagination traversal and rows per page filter.
  - `test_mock_client_deposit_proof_invalid_file_format`: HTTP 415 unsupported file format validation.
  - `test_mock_client_deposit_proof_file_too_large`: HTTP 413 file size limit (>5MB) exceeded.
  - `test_mock_client_deposit_bank_wire_instructions`: Dynamic bank wire IBAN, SWIFT & reference notes.
  - `test_mock_client_deposit_gateway_maintenance_mode`: Single gateway HTTP 503 maintenance mode handling.
- [x] **Withdrawals & Payout Processing** (`test_mock_client_deposit_withdraw.py`):
  - `test_mock_client_withdraw_insufficient_funds`: HTTP 400 Insufficient balance alert.
  - `test_mock_client_withdraw_invalid_otp`: HTTP 400 Incorrect or expired OTP passcode.
  - `test_mock_client_withdraw_kyc_unverified_block`: HTTP 403 Unverified KYC restriction.
  - `test_mock_client_withdraw_daily_limit_exceeded`: HTTP 422 Daily payout limit reached ($50,000).
  - `test_mock_client_withdrawal_submission`: HTTP 200 OK withdrawal request submitted.
  - `test_mock_client_withdraw_fee_calculation`: Dynamic withdrawal fee percentage & net payout calculation.
  - `test_mock_client_withdraw_history_empty_state`: Empty state placeholder for withdrawal history.
  - `test_mock_client_withdraw_history_pagination`: 50+ withdrawal records pagination traversal.
  - `test_mock_client_withdraw_save_details_invalid_iban_swift`: HTTP 422 invalid SWIFT/IFSC format validation.
- [x] **Internal Wallet & Account Transfers** (`test_mock_client_deposit_withdraw.py`):
  - `test_mock_client_internal_transfer_success`: HTTP 200 OK immediate balance deduction.
  - `test_mock_client_transfer_same_account_error`: HTTP 422 Identical source and destination account validation.
  - `test_mock_client_transfer_zero_amount`: HTTP 422 $0.00 transfer rejection.
  - `test_mock_client_transfer_concurrency_lock`: HTTP 409 Concurrent transfer protection.
  - `test_mock_client_transfer_history_empty_state`: Empty recent transfers ledger.
  - `test_mock_client_transfer_history_pagination`: 50+ internal transfer records pagination.
  - `test_mock_client_transfer_insufficient_source_balance`: HTTP 400 Insufficient source account balance.
- [x] **KYC & Multi-Account Wallet Management** (`test_mock_client_kyc_wallet.py`):
  - `test_mock_client_kyc_pending_banner`: KYC in review compliance banner.
  - `test_mock_client_kyc_rejected_alert`: KYC rejection with reviewer reason & resubmit action.
  - `test_mock_client_kyc_upload_file_size_exceeded`: HTTP 413 File size limit (>10MB) exceeded.
  - `test_mock_client_wallet_zero_balance`: $0.00 zero balance rendering.
  - `test_mock_client_wallet_multi_currency`: USD, EUR, and USDT multi-currency ledger.
  - `test_mock_client_wallet_consolidated_funds_breakdown`: Consolidated funds summary (Client Wallet + IB Wallet + Trading Accounts).
  - `test_mock_client_wallet_transfer_history_populated`: Populated wallet transfer history with movement directions.
  - `test_mock_client_wallet_transfer_history_empty`: Empty wallet transfer history ledger.
  - `test_mock_client_wallet_export_report_csv`: CSV statement export trigger.
  - `test_mock_client_create_trading_account_success`: Multi-account creation 200 OK.
  - `test_mock_client_create_trading_account_limit_reached`: HTTP 403 quota exceeded error.
- [x] **Copy Trading, PAMM & MAM** (`test_mock_client_copy_pamm_mam.py`):
  - `test_mock_client_copy_leaderboard_render`: Leaderboard table sorting by ROI.
  - `test_mock_client_copy_leaderboard_empty_state`: Empty state when no managers match search.
  - `test_mock_client_subscribe_strategy_success`: Subscription active badge and strategy follow.
  - `test_mock_client_unfollow_manager_success`: Unfollow confirmation and state reset.
  - `test_mock_client_copy_insufficient_investment_margin`: Minimum equity requirement rejection.
  - `test_mock_client_copy_my_subscriptions_populated`: Active subscriptions tab with allocated capital and follow date.
  - `test_mock_client_copy_statistics_modal_metrics`: Strategy statistics modal (Net profit, win rate, closed trades, drawdown).
  - `test_mock_client_copy_filter_by_range_and_risk`: Dropdown filters by time range and risk level.
  - `test_mock_client_mam_strategy_allocation`: MAM multiplier allocation configuration.
  - `test_mock_client_mam_followers_table_render`: MAM My Followers table with Follower Name, Profit Share %, and User ID.
  - `test_mock_client_mam_statistics_modal_render`: MAM statistics modal with net profit and managed capital.
  - `test_mock_client_mam_unfollow_confirmation`: Unfollow MAM manager workflow.
  - `test_mock_client_mam_empty_followers_state`: Empty state when MAM manager has 0 followers.
  - `test_mock_client_pamm_pool_investment`: PAMM pool allocation and equity share calculation.
  - `test_mock_client_pamm_investors_table_render`: PAMM pool investors list with equity shares.
  - `test_mock_client_pamm_statistics_modal_render`: PAMM pool statistics modal.
  - `test_mock_client_pamm_uninvest_withdrawal`: Uninvest capital from PAMM pool back into wallet.
  - `test_mock_client_pamm_empty_investors_state`: Empty state when PAMM pool has 0 investors.
- [x] **Settings, Security & Refer & Earn** (`test_mock_client_settings_referral.py`):
  - `test_mock_client_referral_stats_render`: IB partner referral count, commissions & affiliate link.
  - `test_mock_client_referral_history_empty_state`: Empty commission payouts ledger.
  - `test_mock_client_password_change_mismatch`: HTTP 400 Incorrect current password alert.
  - `test_mock_client_2fa_toggle_enable_qr`: 2FA TOTP QR code generator.
  - `test_mock_client_bank_details_update_success`: Bank payout instructions save confirmation.
  - `test_mock_client_referral_tree_hierarchy_render`: Multi-tier referral tree hierarchy with direct vs sub-affiliates.
  - `test_mock_client_referred_clients_table_populated`: Referred clients table with accounts, balance, and IB earned.
  - `test_mock_client_referred_clients_table_pagination`: 50+ referred clients pagination traversal.
  - `test_mock_client_personal_info_update_success`: Personal contact and address details update.
  - `test_mock_client_personal_info_invalid_phone_email`: HTTP 422 malformed phone/email validation.
  - `test_mock_client_trading_settings_update`: Trading account leverage and type settings.
  - `test_mock_client_security_password_update_success`: Password change with OTP verification.
- [x] **Network Resilience & Latency Simulation** (`test_mock_client_network_failures.py`):
  - `test_mock_client_deposit_500_server_error`: Payment provider 500 error interception.
  - `test_mock_client_session_expired_401`: HTTP 401 session expiration handling.
  - `test_mock_client_gateway_timeout_504`: Upstream liquidity timeout warning.
  - `test_mock_client_rate_limit_429_toast`: HTTP 429 rate limit with Retry-After header.
  - `test_mock_client_slow_network_latency_spinner`: Simulated 500ms network delay with spinner rendering.
  - `test_mock_client_corrupted_json_payload`: Malformed / 502 Bad Gateway HTML resilience.
  - `test_mock_client_network_offline_abort`: Playwright offline network disconnect simulation (`internetdisconnected`).

---

## 8. CLI Execution & Debugging

```bash
# 1. Run all mock tests across all portals
pytest -m mock -v

# 2. Run mock tests using dedicated master runner
python scripts/run_mock_tests.py

# 3. Run mock tests for a specific portal
python scripts/run_mock_tests.py --portal trade
python scripts/run_mock_tests.py --portal admin
python scripts/run_mock_tests.py --portal client

# 4. Run mock tests in headed mode for visual observation
python scripts/run_mock_tests.py --portal client --headed --slowmo 200

# 5. Parallel execution across 4 CPU workers
python scripts/run_mock_tests.py -n 4
```

---

## 9. Best Practices & Troubleshooting

1. **Always Register Mocks Before Actions**: `mock_router.mock_json()` must be called before the user action that triggers the network call (e.g. before clicking *Submit* or loading the page).
2. **Use Broad Wildcard Patterns**: Endpoints may have variable base URLs or query strings. Prefer `**/api/deposit/**` or `**/Controlbase/userList**` over strict full URLs.
3. **Keep Payloads Isolated**: Use `workflows/shared/mocks/mock_data/` for reusable standard schemas, or define test-specific dictionary payloads inline when testing specific edge cases.
4. **Clean Teardown**: `mock_router` fixture automatically cleans up and unroutes all endpoints after each test, preventing cross-test pollution.

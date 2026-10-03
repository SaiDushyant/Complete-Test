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

### Trade Terminal Mock Suites (`workflows/trade_terminal/tests/mock/` - 96 Tests)
- [x] **Authentication & Session Management** (`test_mock_trade_auth_session.py` - 9 tests):
  - `test_mock_trade_login_success`: Valid login with token injection.
  - `test_mock_trade_login_invalid_credentials`: HTTP 401 invalid credentials alert.
  - `test_mock_trade_session_expiration_401`: Dynamic session expiration and login redirect.
  - `test_mock_trade_account_suspended_403`: HTTP 403 account suspension notice.
  - `test_mock_trade_2fa_otp_challenge`: 2FA prompt rendering.
  - `test_mock_trade_concurrent_session_kickout`: HTTP 409 multi-login kickout.
  - `test_mock_trade_logout_clears_session`: Clean session tear-down.
  - `test_mock_trade_password_reset_request`: Password reset link dispatch.
  - `test_mock_trade_auth_service_500_resilience`: Auth service downtime handling.
- [x] **Order Execution & Ticket Validation** (`test_mock_trade_order_execution.py` - 10 tests):
  - `test_mock_market_buy_success`: Successful buy fill with custom ticket ID.
  - `test_mock_market_sell_success`: Successful sell fill with custom execution price.
  - `test_mock_limit_buy_order_placement`: Pending limit buy order placed.
  - `test_mock_stop_loss_take_profit_submission`: SL/TP parameters submitted and acknowledged.
  - `test_mock_insufficient_margin_error`: HTTP 400 Insufficient margin toast.
  - `test_mock_market_halted_warning`: HTTP 400 Market closed alert.
  - `test_mock_order_rate_limit_429`: HTTP 429 Rapid order placement warning.
  - `test_mock_order_lot_size_invalid`: Min/Max lot size boundaries rejection.
  - `test_mock_order_execution_500_error`: Matching engine 500 error toast.
  - `test_mock_order_delayed_fill_spinner`: Delayed order fill with progress indicator.
- [x] **Account Metrics & Financial Balance** (`test_mock_trade_account_metrics.py` - 5 tests):
  - `test_mock_account_balance_zero`: Zero balance rendering, disables Trade button.
  - `test_mock_high_floating_pnl_equity`: Live equity calculation with floating profit.
  - `test_mock_margin_call_warning_level`: Margin level < 100% warning banner.
  - `test_mock_margin_stop_out_notification`: Margin level < 50% stop-out alert.
  - `test_mock_metrics_endpoint_500_resilience`: Fallback to cached metrics on server error.
- [x] **Watchlist & Live Quotes** (`test_mock_trade_watchlist_quotes.py` - 9 tests):
  - `test_mock_watchlist_symbols_render`: Watchlist symbols, bid/ask quotes rendering.
  - `test_mock_watchlist_empty_state`: Empty watchlist search message.
  - `test_mock_watchlist_search_filter`: Symbol search filtering.
  - `test_mock_watchlist_add_custom_symbol`: Custom symbol addition.
  - `test_mock_watchlist_remove_symbol`: Symbol removal from watchlist.
  - `test_mock_watchlist_spread_formatting`: Spread and tick rendering accuracy.
  - `test_mock_watchlist_live_tick_color_flash`: Green/Red price tick flashing.
  - `test_mock_watchlist_quotes_timeout_indicator`: Disconnected quote feed indicator.
  - `test_mock_watchlist_corrupted_symbol_data`: Graceful recovery from malformed quote JSON.
- [x] **Open & Closed Positions Management** (`test_mock_trade_positions.py` - 10 tests):
  - `test_mock_open_positions_table_render`: Position rows with symbol, volume, PnL, open price.
  - `test_mock_close_single_position_success`: Immediate position closure and row removal.
  - `test_mock_close_all_positions_success`: Bulk close-all action.
  - `test_mock_partial_position_close`: Partial volume close.
  - `test_mock_modify_position_sltp`: Modify SL/TP on active position.
  - `test_mock_positions_empty_state`: "No open positions" banner.
  - `test_mock_close_position_rejected_500`: Position close failure toast.
  - `test_mock_position_auto_liquidated_badge`: Liquidation badge on forced close.
  - `test_mock_positions_sorting_by_pnl`: Sorting table by floating PnL.
  - `test_mock_positions_filter_by_symbol`: Filter positions by asset symbol.
- [x] **Account Switcher & Multi-Account** (`test_mock_trade_account_switcher.py` - 6 tests):
  - `test_mock_account_switcher_dropdown_render`: Live accounts list.
  - `test_mock_switch_account_success`: Switch active account and refresh balance.
  - `test_mock_demo_vs_live_account_badge`: Demo vs Live account badges.
  - `test_mock_account_switcher_single_account`: Single account state.
  - `test_mock_switch_account_network_failure`: Switch account network failure resilience.
  - `test_mock_archived_account_grayed_out`: Inactive/archived account state.
- [x] **Navigation & Layout Structure** (`test_mock_trade_navigation.py` - 5 tests):
  - `test_mock_navigation_tabs_switching`: Seamless switching between Trade, Positions, History, Chart.
  - `test_mock_responsive_layout_mobile_toggle`: Mobile navigation hamburger menu.
  - `test_mock_dark_light_theme_toggle`: UI theme switching.
  - `test_mock_fullscreen_chart_mode`: Chart expansion toggle.
  - `test_mock_keyboard_shortcuts_modal`: Hotkeys cheatsheet modal.
- [x] **Interactive Charting** (`test_mock_trade_chart.py` - 7 tests):
  - `test_mock_chart_candlestick_data_load`: Historical candlestick bar rendering.
  - `test_mock_chart_timeframe_switch_1m_1h_1d`: Dynamic timeframe interval changes.
  - `test_mock_chart_empty_history_placeholder`: "No chart data available" placeholder.
  - `test_mock_chart_data_stream_500_resilience`: Chart feed error recovery.
  - `test_mock_chart_indicator_overlay_rsi_macd`: Technical indicator overlays.
  - `test_mock_chart_drawing_tools_activation`: Trendline drawing tool activation.
  - `test_mock_chart_zoom_pan_interaction`: Zoom in/out viewport interaction.
- [x] **Trading History & Statement Export** (`test_mock_trade_history.py` - 7 tests):
  - `test_mock_history_closed_trades_render`: Closed trades table.
  - `test_mock_history_date_range_filter`: Date filtering (Today, Last 7 Days, Custom).
  - `test_mock_history_empty_state`: Empty history ledger.
  - `test_mock_history_pagination_50_plus`: Traversal of 50+ closed orders.
  - `test_mock_history_export_csv`: CSV transaction report download.
  - `test_mock_history_summary_aggregates`: Realized profit, commission, and swap totals.
  - `test_mock_history_500_error_retry`: History fetch retry on error.
- [x] **Terminal Dashboard & Workspace** (`test_mock_trade_dashboard.py` - 7 tests):
  - `test_mock_dashboard_full_workspace_render`: Multi-pane workspace initialization.
  - `test_mock_dashboard_quick_trade_widget`: One-click quick trade buttons.
  - `test_mock_dashboard_market_sentiment_gauge`: Buy/Sell ratio bar.
  - `test_mock_dashboard_economic_calendar_events`: Calendar high-impact news items.
  - `test_mock_dashboard_widget_minimize_maximize`: Workspace panel resizing.
  - `test_mock_dashboard_latency_meter`: Connection latency / ping meter.
  - `test_mock_dashboard_skeleton_loader`: Initial skeleton loader during delayed API response.
- [x] **Profile & Terminal Settings** (`test_mock_trade_profile_settings.py` - 7 tests):
  - `test_mock_profile_details_render`: Account ID, email, leverage, group display.
  - `test_mock_change_trading_password_success`: Password change with OTP.
  - `test_mock_change_password_mismatch_error`: Password mismatch validation.
  - `test_mock_default_lot_size_setting_save`: Preferred default lot size persistence.
  - `test_mock_one_click_trading_toggle`: One-click trading disclaimer modal & toggle.
  - `test_mock_sound_notifications_toggle`: Sound alert toggle.
  - `test_mock_profile_save_500_error`: Profile update server error notification.
- [x] **API Key & Webhook Access** (`test_mock_trade_api_access.py` - 6 tests):
  - `test_mock_api_keys_list_render`: Active API keys and permission scopes.
  - `test_mock_generate_new_api_key_modal`: New API key generation & secret display.
  - `test_mock_revoke_api_key_success`: Key revocation confirmation.
  - `test_mock_api_key_limit_reached`: Maximum API keys quota exceeded.
  - `test_mock_ip_whitelist_update`: IP whitelist save confirmation.
  - `test_mock_api_secret_copy_clipboard`: Secret copy-to-clipboard action.
- [x] **Server Errors & Network Resilience** (`test_mock_trade_server_errors.py` - 8 tests):
  - `test_mock_trade_server_500_banner`: Server 500 crash notification.
  - `test_mock_trade_server_502_bad_gateway`: 502 Bad Gateway fallback.
  - `test_mock_trade_server_503_maintenance`: Scheduled maintenance overlay.
  - `test_mock_trade_gateway_timeout_504`: Upstream liquidity timeout warning.
  - `test_mock_trade_rate_limit_429`: HTTP 429 rate limit with Retry-After header.
  - `test_mock_trade_network_offline_abort`: Playwright offline network disconnect simulation.
  - `test_mock_trade_corrupted_response_payload`: HTML error response in JSON endpoint resilience.
  - `test_mock_trade_slow_network_reconnect_prompt`: Reconnection prompt under severe latency.

### Admin Portal Mock Suites (`workflows/admin_portal/tests/mock/` - 81 Tests)
- [x] **Authentication & Role Authorization** (`test_mock_admin_auth.py`): SuperAdmin / Manager logins, 2FA, session expiry.
- [x] **User Management & Accounts** (`test_mock_admin_users.py`): User list, pagination, balance adjustment, group modification.
- [x] **Deposits & Fund Approvals** (`test_mock_admin_deposits.py`): Deposit approval, rejection, audit log verification.
- [x] **Withdrawal Queue & Processing** (`test_mock_admin_withdrawals.py`): Payout approval, fee deduction, reversal.
- [x] **KYC & Document Verification** (`test_mock_admin_kyc.py`): ID document review, approval, rejection with notes.
- [x] **LP & Liquidity Providers** (`test_mock_admin_lp.py`): LP bridge health, feed status, symbol routing.
- [x] **Orders & Trade Management** (`test_mock_admin_orders.py`): Order book audit, Category A/B/C inspection, force close.
- [x] **Risk Management & A/B Books** (`test_mock_admin_risk_books.py`): Book allocation, toxic flow rules, exposure limits.
- [x] **Automated Cron Jobs** (`test_mock_admin_cron_jobs.py`): Daily rollover, interest accrual, statement generation triggers.
- [x] **PAMM / MAM Administration** (`test_mock_admin_pamm_mam.py`): Manager approval, investor detachment, fee settlement.
- [x] **Admin Roles & Permissions** (`test_mock_admin_roles.py`): Granular permission matrix, read-only restriction enforcement.
- [x] **System Settings & Maintenance** (`test_mock_admin_settings.py`): Global platform flags, maintenance mode switch.
- [x] **Symbol & Spread Configuration** (`test_mock_admin_symbols.py`): Spread markups, swap rates, trading hours.
- [x] **Bonus & Promotions** (`test_mock_admin_bonus.py`): Deposit bonus allocation, wagering requirements.
- [x] **Leads & CRM Management** (`test_mock_admin_leads.py`): Lead assignment, sales stage updates.
- [x] **Audit Logs & Security** (`test_mock_admin_audit.py`): Immutable audit trail, IP tracking.
- [x] **Server Resilience & Fault Injection** (`test_mock_admin_server_errors.py`): HTTP 500/502/503/504 fault injection.

### Client Portal Mock Suites (`workflows/client_portal/tests/mock/` - 92 Tests)
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

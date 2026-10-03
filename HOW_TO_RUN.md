# How to Run the Complete Test Framework: CLI & Execution Guide

This comprehensive guide details how to configure, execute, and inspect all test suites in the **Complete Test Framework** across **Element-Level Validation Testing** (434 tests), **Behavioral Workflow Testing** (920 tests), and **UI DOM Structural Regression Testing** (29 tests) — totaling **1,383 test cases**.

---

## 📑 Table of Contents

1. [Quick Start & Overview](#1-quick-start--overview)
2. [Environment Setup & Configuration (`.env`)](#2-environment-setup--configuration-env)
3. [Validation Test Suites (434 Tests)](#3-validation-test-suites-434-tests)
   - [3.1 Full Platform Validation Suite](#31-full-platform-validation-suite)
   - [3.2 Portal-Specific Validation Suites](#32-portal-specific-validation-suites)
   - [3.3 Running Specific Validation Modules & Individual Tests](#33-running-specific-validation-modules--individual-tests)
4. [Master & Specialized Workflow Test Runners (`scripts/`)](#4-master--specialized-workflow-test-runners-scripts)
   - [4.1 Master Runner (`run_all_workflows.py`)](#41-master-runner-run_all_workflowspy)
   - [4.2 Smoke Test Runner (`run_smoke_tests.py`)](#42-smoke-test-runner-run_smoke_testspy)
   - [4.3 Regression Test Runner (`run_regression_tests.py`)](#43-regression-test-runner-run_regression_testspy)
   - [4.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)](#44-shared--cross-portal-runner-run_shared_testspy)
5. [UI DOM Regression & Drift Detection Runners](#5-ui-dom-regression--drift-detection-runners)
6. [High-Performance Parallel Execution (`pytest-xdist`)](#6-high-performance-parallel-execution-pytest-xdist)
7. [Headed vs Headless Visual Debugging](#7-headed-vs-headless-visual-debugging)
8. [Reporting & Suite-Level History Management](#8-reporting--suite-level-history-management)

---

## 1. Quick Start & Overview

The framework unifies all test suites into clean, non-conflicting domains:

```text
                            COMPLETE-TEST FRAMEWORK
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │                                           │
                 ▼                                           ▼
      workflows/ (1,354 tests)                     ui_regression/ (29 tests)
  Behavioral & Validation Testing                 DOM Drift & Structural Accuracy
                 │                                           │
   ┌─────────────┼─────────────┐                ┌────────────┴────────────┐
   │             │             │                │                         │
 Admin        Client         Trade          Crawler                   Comparer
Portal        Portal       Terminal        (Baselines)             (Drift Diffing)
(554 tests)  (246 tests)  (395 tests)
```

### Quick Commands Cheat Sheet

```bash
# Activate Conda environment
conda activate playwright-env

# 1. Run All Platform Validation Tests (434 Tests)
pytest -m validation -v

# 2. Run Trade Terminal Validation Tests (220 Tests)
pytest workflows/trade_terminal/tests/test_val_trade_*.py -v

# 3. Run Admin Portal Validation Tests (129 Tests)
pytest workflows/admin_portal/tests/test_val_admin_*.py -v

# 4. Run Client Portal Validation Tests (85 Tests)
pytest workflows/client_portal/tests/test_val_client_*.py -v

# 5. Run all behavioral workflow tests headless
python scripts/run_all_workflows.py

# 6. Run critical smoke tests (< 2 mins)
python scripts/run_smoke_tests.py

# 7. Run full UI DOM regression pipeline
python scripts/run_ui_full_pipeline.py
```

---

## 2. Environment Setup & Configuration (`.env`)

Before running tests, ensure your `.env` file is present in the repository root (copied from `.env.example`).

```env
# Client Portal
BASELINE_URL=https://stage.xtremenext.com/
BASELINE_TEST_USER_EMAIL=10009
BASELINE_TEST_USER_PASSWORD=Temp@123
CLIENT_USERNAME=10009
CLIENT_PASSWORD=Temp@123

# Trade Terminal
TRADE_TERMINAL_URL=https://stage.xtremenext.com/
TRADE_LOGIN_URL=https://stage.xtremenext.com/login/
TRADE_USERNAME=10009
TRADE_PASSWORD=Temp@123

# Admin Portal
BASELINE_ADMIN_BASE_URL=https://stage.xtremenext.com/admin/Controlbase/Dashboard
BASELINE_ADMIN_LOGIN_URL=https://stage.xtremenext.com/admin/Login/index
ADMIN_USERNAME=madmin
ADMIN_PASSWORD=Test@1234
```

---

## 3. Validation Test Suites (434 Tests)

Validation tests verify boundary values, SQL injection, XSS attacks, financial calculations, form submission guards, and UI controls across all portals.

### 3.1 Full Platform Validation Suite
Executes all 434 validation tests across Admin, Client, and Trade Terminal:
```bash
pytest -m validation -v
```

### 3.2 Portal-Specific Validation Suites
```bash
# Trade Terminal Validation Suite (220 tests)
pytest workflows/trade_terminal/tests/test_val_trade_*.py -v

# Admin Portal Validation Suite (129 tests)
pytest workflows/admin_portal/tests/test_val_admin_*.py -v

# Client Portal Validation Suite (85 tests)
pytest workflows/client_portal/tests/test_val_client_*.py -v
```

### 3.3 Running Specific Validation Modules & Individual Tests

#### Run a Single Test Module:
```bash
# Trade Order Entry & Ticket boundary tests
pytest workflows/trade_terminal/tests/test_val_trade_order_entry.py -v

# Client Deposit form validation tests
pytest workflows/client_portal/tests/test_val_client_deposit.py -v

# Admin User Management validation tests
pytest workflows/admin_portal/tests/test_val_admin_user_management.py -v
```

#### Run an Individual Test Case / Function:
```bash
# Specific test function inside a class
pytest workflows/trade_terminal/tests/test_val_trade_login.py::TestValTradeLogin::test_val_login_empty_form_submission_blocked -v

# Specific standalone test function
pytest workflows/client_portal/tests/test_val_client_deposit.py::test_val_deposit_submit_disabled_when_empty -v
```

#### Run by Keyword Search (`-k`):
```bash
# Run any test matching "deposit"
pytest -k "deposit" -v

# Run any test matching "xss"
pytest -k "xss" -v
```

---

## 4. Master & Specialized Workflow Test Runners (`scripts/`)

### 4.1 Master Runner (`run_all_workflows.py`)
Executes all behavioral workflow tests:
```bash
python scripts/run_all_workflows.py
```

### 4.2 Smoke Test Runner (`run_smoke_tests.py`)
Runs critical smoke paths for fast feedback:
```bash
python scripts/run_smoke_tests.py
```

### 4.3 Regression Test Runner (`run_regression_tests.py`)
Runs full behavioral regression suites:
```bash
python scripts/run_regression_tests.py
```

### 4.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)
Runs multi-account, MAM/PAMM replication, and cross-portal synchronization workflows:
```bash
python scripts/run_shared_tests.py
```

---

## 5. UI DOM Regression & Drift Detection Runners

- **Compare Live against Baseline**:
  ```bash
  python scripts/run_ui_compare.py
  ```
- **Re-Crawl and Update Baselines**:
  ```bash
  python scripts/run_ui_crawl.py
  ```
- **Full Pipeline (Crawl + Compare + Report)**:
  ```bash
  python scripts/run_ui_full_pipeline.py
  ```

---

## 6. High-Performance Parallel Execution (`pytest-xdist`)

Run tests concurrently across multiple CPU workers:
```bash
# Run validation tests in parallel with 4 workers
pytest -m validation -n 4 -v

# Run workflow tests with loadfile work distribution
pytest workflows/ -n 4 --dist loadfile -v
```

---

## 7. Headed vs Headless Visual Debugging

- **Headed Browser Mode**:
  ```bash
  pytest workflows/client_portal/tests/test_val_client_deposit.py -v --headed
  ```
- **Slow Motion Delay** (e.g. 300ms pause between actions):
  ```bash
  pytest workflows/trade_terminal/tests/test_val_trade_order_entry.py -v --headed --slowmo 300
  ```
- **Live Output Print (`-s`)**:
  ```bash
  pytest workflows/admin_portal/tests/test_val_admin_user_management.py -v -s
  ```

---

## 8. Reporting & Suite-Level History Management

Reports are automatically partitioned into segregated suite folders under `reports/`:

```text
reports/
├── validations/                      # Active validation suite outputs
│   ├── logs/                         # global_test_summary.txt, global_test_results.json
│   ├── diagnostics/                  # Detailed telemetry JSONs (console errors, HTTP 4xx/5xx)
│   ├── screenshots/                  # Failure PNG screenshots
│   ├── traces/                       # Playwright timeline traces (.zip)
│   └── history/                      # Timestamped prior run archives
│       └── <RunType> - DD-MM-YYYY_HH-MM-SS/
│           ├── logs/
│           ├── diagnostics/
│           ├── screenshots/
│           └── traces/
│
├── workflows/                        # Behavioral workflow suite outputs
│   ├── logs/
│   ├── screenshots/
│   ├── traces/
│   └── history/
│
└── ui_regression/                    # Visual DOM regression comparison reports
    └── history/
```

- **Active Summary**: [`reports/validations/logs/global_test_summary.txt`](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/reports/validations/logs/global_test_summary.txt)
- **JSON Telemetry Report**: [`reports/validations/logs/global_test_results.json`](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/reports/validations/logs/global_test_results.json)
- **Automatic History Archiving**: On every new session start, previous logs, screenshots, diagnostics, and traces are cleanly archived into `history/`, ensuring active test directories remain clean.

# How to Run the Complete Test Framework: CLI & Execution Guide

This comprehensive guide details how to configure, execute, and inspect all test suites in the **Complete Test Framework** across **Element-Level Validation Testing** (434 tests), **Behavioral Workflow Testing** (955 tests), **Network Mock Testing** (269 tests), and **UI DOM Structural Regression Testing** (29 tests) — totaling **1,687 test cases**.

---

## 📑 Table of Contents

1. [Quick Start & Overview](#1-quick-start--overview)
2. [Environment Setup & Configuration (`.env`)](#2-environment-setup--configuration-env)
3. [Mock Testing Suites (269 Tests)](#3-mock-testing-suites-269-tests)
   - [3.1 Full Platform Mock Suite](#31-full-platform-mock-suite)
   - [3.2 Portal-Specific Mock Suites](#32-portal-specific-mock-suites)
   - [3.3 Parallel Mock Execution & Fault Injection](#33-parallel-mock-execution--fault-injection)
4. [Validation Test Suites (434 Tests)](#4-validation-test-suites-434-tests)
   - [4.1 Full Platform Validation Suite](#41-full-platform-validation-suite)
   - [4.2 Portal-Specific Validation Suites](#42-portal-specific-validation-suites)
   - [4.3 Running Specific Validation Modules & Individual Tests](#43-running-specific-validation-modules--individual-tests)
5. [Master & Specialized Workflow Test Runners (`scripts/`)](#5-master--specialized-workflow-test-runners-scripts)
   - [5.1 Master Runner (`run_all_workflows.py`)](#51-master-runner-run_all_workflowspy)
   - [5.2 Smoke Test Runner (`run_smoke_tests.py`)](#52-smoke-test-runner-run_smoke_testspy)
   - [5.3 Regression Test Runner (`run_regression_tests.py`)](#53-regression-test-runner-run_regression_testspy)
   - [5.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)](#54-shared--cross-portal-runner-run_shared_testspy)
6. [UI DOM Regression & Drift Detection Runners](#6-ui-dom-regression--drift-detection-runners)
7. [High-Performance Parallel Execution (`pytest-xdist`)](#7-high-performance-parallel-execution-pytest-xdist)
8. [Headed vs Headless Visual Debugging](#8-headed-vs-headless-visual-debugging)
9. [Reporting & Suite-Level History Management](#9-reporting--suite-level-history-management)

---

## 1. Quick Start & Overview

The framework unifies all test suites into clean, non-conflicting domains:

```text
                            COMPLETE-TEST FRAMEWORK
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │                     │                     │
                 ▼                     ▼                     ▼
      workflows/ (1,389 tests)   mock/ (269 tests)    ui_regression/ (29 tests)
  Behavioral & Validation Testing Network Mocking      DOM Drift & Structural
                 │                     │                     │
   ┌─────────────┼─────────────┐   ┌───┼───┐          ┌──────┴──────┐
   │             │             │   │   │   │          │             │
 Admin        Client         Trade Adm Cli Tra     Crawler       Comparer
```

### Quick Commands Cheat Sheet

```bash
# Activate Conda environment
conda activate playwright-env

# 1. Run All Mock Tests across all portals (269 Tests in ~16s)
python scripts/run_mock_tests.py --portal all

# 2. Run Portal-Specific Mock Tests
python scripts/run_mock_tests.py --portal trade
python scripts/run_mock_tests.py --portal admin
python scripts/run_mock_tests.py --portal client

# 3. Run All Platform Validation Tests (434 Tests)
pytest -m validation -v

# 4. Run Trade Terminal Validation Tests (220 Tests)
pytest workflows/trade_terminal/tests/test_val_trade_*.py -v

# 5. Run Admin Portal Validation Tests (129 Tests)
pytest workflows/admin_portal/tests/test_val_admin_*.py -v

# 6. Run Client Portal Validation Tests (85 Tests)
pytest workflows/client_portal/tests/test_val_client_*.py -v

# 7. Run all behavioral workflow tests headless
python scripts/run_all_workflows.py

# 8. Run critical smoke tests (< 2 mins)
python scripts/run_smoke_tests.py

# 9. Run full UI DOM regression pipeline
python scripts/run_ui_full_pipeline.py
```

---

## 2. Environment Setup & Configuration (`.env`)

Before running tests, ensure your `.env` file is present in the repository root (copied from `.env.example`).

```env
# Client Portal
BASELINE_URL=https://stage.xtremenext.com/
BASELINE_TEST_USER_EMAIL=your_test_user
BASELINE_TEST_USER_PASSWORD=your_password
CLIENT_USERNAME=your_client_username
CLIENT_PASSWORD=your_password

# Trade Terminal
TRADE_TERMINAL_URL=https://stage.xtremenext.com/
TRADE_LOGIN_URL=https://stage.xtremenext.com/login/
TRADE_USERNAME=your_trade_username
TRADE_PASSWORD=your_password

# Admin Portal
BASELINE_ADMIN_BASE_URL=https://stage.xtremenext.com/admin/Controlbase/Dashboard
BASELINE_ADMIN_LOGIN_URL=https://stage.xtremenext.com/admin/Login/index
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_password
```

---

## 3. Mock Testing Suites (269 Tests)

Mock testing uses Playwright route interception (`MockRouter`) to test frontend UI states, error handling, rate limiting, and zero-balance configurations 100% offline with zero database mutation.

### 3.1 Full Platform Mock Suite
Executes all 269 mock tests across Trade Terminal, Admin Portal, and Client Portal in ~16 seconds:
```bash
python scripts/run_mock_tests.py --portal all
```

### 3.2 Portal-Specific Mock Suites
```bash
# Trade Terminal Mock Suite (96 tests across 13 suites)
python scripts/run_mock_tests.py --portal trade

# Admin Portal Mock Suite (81 tests across 22 suites)
python scripts/run_mock_tests.py --portal admin

# Client Portal Mock Suite (92 tests across 7 suites)
python scripts/run_mock_tests.py --portal client
```

### 3.3 Parallel Mock Execution & Fault Injection
```bash
# Run mock tests in parallel across 4 CPU workers
python scripts/run_mock_tests.py -n 4

# Run with visible browser and slowmo delay for visual demonstration
python scripts/run_mock_tests.py --portal trade --headed --slowmo 200

# Filter mock tests by keyword or scenario
python scripts/run_mock_tests.py -k "server_errors or rate_limit"
```

---

## 4. Validation Test Suites (434 Tests)

Validation tests verify boundary values, SQL injection, XSS attacks, financial calculations, form submission guards, and UI controls across all portals.

### 4.1 Full Platform Validation Suite
Executes all 434 validation tests across Admin, Client, and Trade Terminal:
```bash
pytest -m validation -v
```

### 4.2 Portal-Specific Validation Suites
```bash
# Trade Terminal Validation Suite (220 tests)
pytest workflows/trade_terminal/tests/test_val_trade_*.py -v

# Admin Portal Validation Suite (129 tests)
pytest workflows/admin_portal/tests/test_val_admin_*.py -v

# Client Portal Validation Suite (85 tests)
pytest workflows/client_portal/tests/test_val_client_*.py -v
```

### 4.3 Running Specific Validation Modules & Individual Tests

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

## 5. Master & Specialized Workflow Test Runners (`scripts/`)

### 5.1 Master Runner (`run_all_workflows.py`)
Executes all behavioral workflow tests:
```bash
python scripts/run_all_workflows.py
```

### 5.2 Smoke Test Runner (`run_smoke_tests.py`)
Runs critical smoke paths for fast feedback:
```bash
python scripts/run_smoke_tests.py
```

### 5.3 Regression Test Runner (`run_regression_tests.py`)
Runs full behavioral regression suites:
```bash
python scripts/run_regression_tests.py
```

### 5.4 Shared & Cross-Portal Runner (`run_shared_tests.py`)
Runs multi-account, MAM/PAMM replication, and cross-portal synchronization workflows:
```bash
python scripts/run_shared_tests.py
```

---

## 6. UI DOM Regression & Drift Detection Runners

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

## 7. High-Performance Parallel Execution (`pytest-xdist`)

Run tests concurrently across multiple CPU workers:
```bash
# Run mock tests in parallel with 4 workers
python scripts/run_mock_tests.py -n 4

# Run validation tests in parallel with 4 workers
pytest -m validation -n 4 -v

# Run workflow tests with loadfile work distribution
pytest workflows/ -n 4 --dist loadfile -v
```

---

## 8. Headed vs Headless Visual Debugging

- **Headed Browser Mode**:
  ```bash
  python scripts/run_mock_tests.py --portal trade --headed --slowmo 200
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

## 9. Reporting & Suite-Level History Management

Reports are automatically partitioned into segregated suite folders under `reports/`:

```text
reports/
├── mock/                             # Mock testing outputs
│   ├── logs/                         # global_test_summary.txt, global_test_results.json
│   ├── history/                      # Timestamped prior mock run archives
│   └── individual/                   # Individual test txt/json logs
│
├── validations/                      # Active validation suite outputs
│   ├── logs/                         # global_test_summary.txt, global_test_results.json
│   ├── diagnostics/                  # Detailed telemetry JSONs (console errors, HTTP 4xx/5xx)
│   ├── screenshots/                  # Failure PNG screenshots
│   ├── traces/                       # Playwright timeline traces (.zip)
│   └── history/                      # Timestamped prior run archives
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

- **Mock Tests Summary**: [`reports/mock/logs/global_test_summary.txt`](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/reports/mock/logs/global_test_summary.txt)
- **Validation Summary**: [`reports/validations/logs/global_test_summary.txt`](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/reports/validations/logs/global_test_summary.txt)
- **JSON Telemetry Report**: [`reports/mock/logs/global_test_results.json`](file:///Users/xtremenext_viji/Code/Playwrite/Complete-Test/reports/mock/logs/global_test_results.json)
- **Automatic History Archiving**: On every new session start, previous logs, screenshots, diagnostics, and traces are cleanly archived into `history/`, ensuring active test directories remain clean.


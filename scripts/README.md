# Automated Test Execution Scripts & Suite Guide

This directory contains executable test runners and CLI automation scripts for both **Behavioral Workflow Testing** and **UI DOM Regression Testing**.

All scripts execute in **Headless mode by default** to maximize performance and compatibility with headless CI/CD environments. To launch a visible browser window for interactive debugging or visual monitoring, pass the `--headed` flag to any script.

---

## 📑 Table of Contents
1. [Quick Reference Matrix](#quick-reference-matrix)
2. [Workflow Test Runners](#workflow-test-runners)
   - [1. Master Workflow Runner (`run_all_workflows.py`)](#1-master-workflow-runner-run_all_workflowspy)
   - [2. Smoke Test Runner (`run_smoke_tests.py`)](#2-smoke-test-runner-run_smoke_testspy)
   - [3. Regression Test Runner (`run_regression_tests.py`)](#3-regression-test-runner-run_regression_testspy)
   - [4. Shared & Cross-Portal Runner (`run_shared_tests.py`)](#4-shared--cross-portal-runner-run_shared_testspy)
   - [5. Admin Portal Runner (`run_admin_tests.py`)](#5-admin-portal-runner-run_admin_testspy)
   - [6. Client Portal Runner (`run_client_tests.py`)](#6-client-portal-runner-run_client_testspy)
   - [7. Trade Terminal Runner (`run_trade_tests.py`)](#7-trade-terminal-runner-run_trade_testspy)
   - [8. Mock Testing Runner (`run_mock_tests.py`)](#8-mock-testing-runner-run_mock_testspy--run_mock_testssh)
3. [UI DOM Regression & Drift Scripts](#ui-dom-regression--drift-scripts)
   - [9. UI Drift Comparison (`run_ui_compare.py`)](#9-ui-drift-comparison-run_ui_comparepy)
   - [10. Baseline Re-Crawl Generator (`run_ui_crawl.py`)](#10-baseline-re-crawl-generator-run_ui_crawlpy)
   - [11. Full UI Regression Pipeline (`run_ui_full_pipeline.py`)](#11-full-ui-regression-pipeline-run_ui_full_pipelinepy)
   - [12. UI Regression Assertions (`run_ui_tests.py`)](#12-ui-regression-assertions-run_ui_testspy)
   - [13. Status Inspector (`status.py`)](#13-status-inspector-statuspy)
4. [Universal CLI Flags & Options](#universal-cli-flags--options)
5. [Reporting & Test Output Formats (JSON + TXT)](#reporting--test-output-formats-json--txt)

---

## 📊 Quick Reference Matrix

| Script | Level / Category | What It Does | When to Use | Default Mode |
| :--- | :--- | :--- | :--- | :--- |
| `run_all_workflows.py` | **Master Suite** | Executes all behavioral workflows across all portals. | Pre-release sign-off, full nightly builds, end-to-end audit. | Headless (`--headed` available) |
| `run_smoke_tests.py` | **Smoke Level** | Executes critical user journeys (`-m smoke`). | Post-deployment sanity check, fast PR validation (< 2 mins). | Headless (`--headed` available) |
| `run_regression_tests.py` | **Regression Level** | Executes full functional regression workflows across portals. | Sprint regression verification, pre-merge gate. | Headless (`--headed` available) |
| `run_shared_tests.py` | **Cross-Portal** | Runs multi-portal integration, user discovery, and auth negative tests. | Testing cross-system interactions & permission synchronization. | Headless (`--headed` available) |
| `run_admin_tests.py` | **Portal-Specific** | Runs Admin Portal workflows (Managers, Orders A/B/C, Margins, Roles). | Developing or validating Admin management functionality. | Headless (`--headed` available) |
| `run_client_tests.py` | **Portal-Specific** | Runs Client Portal workflows (Dashboard, Accounts, Uploads, Deposits). | Validating client user journeys and account requests. | Headless (`--headed` available) |
| `run_trade_tests.py` | **Portal-Specific** | Runs Web Trading Terminal workflows (Orders, Watchlist, MAM/PAMM). | Validating trading operations, order execution, and replication. | Headless (`--headed` available) |
| `run_mock_tests.py` | **Mock Testing** | Runs mock server and network interception tests across all portals. | Offline testing, fault injection (500/504), rate limit, 0-balance states. | Headless (`--headed` available) |
| `run_ui_compare.py` | **UI Drift (Level 1)** | Compares live DOM against baseline snapshots without recrawling. | Rapidly check if recent frontend UI code drifted from baseline. | Headless (`--headed` available) |
| `run_ui_crawl.py` | **UI Baseline (Level 2)** | Re-crawls live application to extract and update baseline JSONs. | After intentional frontend releases or new page additions. | Headless (`--headed` available) |
| `run_ui_full_pipeline.py`| **UI E2E (Level 3)** | Multi-phase: Recrawls, compares DOM, logs errors, and prints status. | Comprehensive UI health audit & drift verification. | Headless (`--headed` available) |
| `run_ui_tests.py` | **UI Assertions (Level 4)** | Runs Pytest assertions verifying element structures and zero errors. | Automated CI assertion test for DOM integrity. | Headless (`--headed` available) |
| `status.py` | **Diagnostics** | Formats comparison reports, prints element drift and runtime errors. | Inspecting JS exceptions, network failures, and drift reasons. | CLI Inspector |

---

## 🏃 Workflow Test Runners

### 1. Master Workflow Runner (`run_all_workflows.py`)
- **Purpose**: Master orchestrator for running the entire end-to-end behavioral test suite.
- **Why Use It**: Provides a single unified command that tests all portals, collects comprehensive metrics across all modules, and flushes consolidated master TXT and JSON reports.
- **Usage**:
  ```bash
  # Run all workflows headless (default)
  python scripts/run_all_workflows.py

  # Run all workflows in a visible browser with 200ms delay between actions
  python scripts/run_all_workflows.py --headed --slowmo 200

  # Run only Admin portal workflows
  python scripts/run_all_workflows.py --portal admin

  # Run only MAM / PAMM workflows
  python scripts/run_all_workflows.py -m "mam or pamm"

  # Parallel execution across 4 CPU workers
  python scripts/run_all_workflows.py -n 4
  ```

---

### 2. Smoke Test Runner (`run_smoke_tests.py`)
- **Purpose**: Executes high-priority critical user journeys tagged with the `@pytest.mark.smoke` marker.
- **Why Use It**: Delivers fast, immediate feedback on core system health (login, dashboard rendering, basic balance check) within 1-2 minutes.
- **Usage**:
  ```bash
  # Headless smoke execution
  python scripts/run_smoke_tests.py

  # Headed smoke execution
  python scripts/run_smoke_tests.py --headed

  # Filter smoke tests for specific portal
  python scripts/run_smoke_tests.py -k "admin"
  ```

---

### 3. Regression Test Runner (`run_regression_tests.py`)
- **Purpose**: Runs the full functional and behavioral regression suite across all portals.
- **Why Use It**: Guarantees that changes in one module do not break existing functionality in order processing, margin validation, user permissions, or copy trading.
- **Usage**:
  ```bash
  python scripts/run_regression_tests.py
  python scripts/run_regression_tests.py --headed
  python scripts/run_regression_tests.py -k "order_lifecycle"
  ```

---

### 4. Shared & Cross-Portal Runner (`run_shared_tests.py`)
- **Purpose**: Executes integration tests in `workflows/shared/tests/` including Admin User Discovery, Manage User matrix, Multi-Portal Data Reflection, Negative Authentication, **Manager Hierarchy Data Isolation**, **A Book / B Book Order Lifecycle**, and **Financial Metric Calculation Verification**.
- **Why Use It**: Verifies data synchronization and state consistency across Admin, Client, and Trade portals simultaneously.
- **Usage**:
  ```bash
  python scripts/run_shared_tests.py
  python scripts/run_shared_tests.py --headed
  python scripts/run_shared_tests.py -k "test_manage_user"
  ```

---

### 5. Admin Portal Runner (`run_admin_tests.py`)
- **Purpose**: Executes all Admin Management Portal workflows (`workflows/admin_portal/tests/`).
- **Why Use It**: Tests Category A/B/C orders, Forced Liquidation, Manager Creation, Role Permissions, Symbol Reflection, and Book Reports.
- **Usage**:
  ```bash
  python scripts/run_admin_tests.py
  python scripts/run_admin_tests.py -m orders
  python scripts/run_admin_tests.py -m category_a
  python scripts/run_admin_tests.py --headed
  ```

---

### 6. Client Portal Runner (`run_client_tests.py`)
- **Purpose**: Executes all Client Portal workflows (`workflows/client_portal/tests/`).
- **Why Use It**: Tests Client Login, Dashboard metrics, Account Request submissions, Document KYC uploads, Deposits, and PAMM/MAM subscriptions.
- **Usage**:
  ```bash
  python scripts/run_client_tests.py
  python scripts/run_client_tests.py --headed
  ```

---

### 7. Trade Terminal Runner (`run_trade_tests.py`)
- **Purpose**: Executes Web Trading Terminal workflows (`workflows/trade_terminal/tests/`).
- **Why Use It**: Tests Market Watch, Order Ticket execution (Buy/Sell/Limit/Stop), Margin Level calculations, API token management, and Copy Trading Manager/Follower execution.
- **Usage**:
  ```bash
  python scripts/run_trade_tests.py
  python scripts/run_trade_tests.py -m mam
  python scripts/run_trade_tests.py --headed
  ```

---

### 8. Mock Testing Runner (`run_mock_tests.py` / `run_mock_tests.sh`)
- **Purpose**: Executes offline Mock Server & Network Interception Test Suites (269 tests across Trade Terminal, Admin Portal, and Client Portal).
- **Why Use It**: Fast, deterministic test execution with zero live database mutations. Injects HTTP 500/504 errors, 429 rate limiting, offline network drops, and extreme boundary states.
- **Usage**:
  ```bash
  # Run all mock tests across all portals
  python scripts/run_mock_tests.py
  ./scripts/run_mock_tests.sh

  # Filter mock tests by portal
  python scripts/run_mock_tests.py --portal trade
  python scripts/run_mock_tests.py --portal admin
  python scripts/run_mock_tests.py --portal client

  # Run mock tests with headed browser and slowmo
  python scripts/run_mock_tests.py --portal trade --headed --slowmo 200

  # Parallel execution with 4 workers
  python scripts/run_mock_tests.py -n 4
  ```

---

## 🎨 UI DOM Regression & Drift Scripts

### 8. UI Drift Comparison (`run_ui_compare.py`)
- **Level**: Level 1 (Comparison Only)
- **Purpose**: Compares live webpage DOMs against existing baseline JSON snapshots without overwriting baselines.
- **Why Use It**: Quickly identifies DOM modifications, missing selectors, added elements, or layout shifts without risking baseline corruption.
- **Usage**:
  ```bash
  # Compare both portals across all viewports
  python scripts/run_ui_compare.py

  # Compare only Admin portal in desktop viewport
  python scripts/run_ui_compare.py --portal admin --viewports desktop

  # Compare with visible browser
  python scripts/run_ui_compare.py --headed
  ```

---

### 9. Baseline Re-Crawl Generator (`run_ui_crawl.py`)
- **Purpose**: Crawls the live applications, extracts all DOM elements across desktop/mobile/tablet viewports, and creates/updates baseline snapshots in `ui_regression/element_output/` and `ui_regression/element_output_admin/`.
- **When to Use**: When a new UI feature has been officially deployed and you want to establish a new golden baseline for future regression tests.
- **Usage**:
  ```bash
  # Re-crawl all portals
  python scripts/run_ui_crawl.py

  # Re-crawl only Admin portal
  python scripts/run_ui_crawl.py --portal admin

  # Re-crawl with depth limit
  python scripts/run_ui_crawl.py --max-depth 5 --max-pages 50
  ```

---

### 10. Full UI Regression Pipeline (`run_ui_full_pipeline.py`)
- **Level**: Level 3 (Full End-to-End Pipeline)
- **Purpose**: Runs the complete automated UI regression workflow:
  1. Re-crawls baselines (optional via `--skip-crawl`).
  2. Compares live DOM with full telemetry & error capture.
  3. Displays detailed diagnostic status breakdowns.
- **Why Use It**: Comprehensive single-command audit for all UI structures and runtime errors.
- **Usage**:
  ```bash
  # Complete pipeline for all portals
  python scripts/run_ui_full_pipeline.py

  # Skip re-crawl and only run comparison + status inspector
  python scripts/run_ui_full_pipeline.py --skip-crawl

  # Run pipeline for Admin portal only
  python scripts/run_ui_full_pipeline.py --portal admin
  ```

---

### 11. UI Regression Assertions (`run_ui_tests.py`)
- **Purpose**: Executes the pytest test suite in `ui_regression/tests/` to perform programmatic assertions on baseline completeness and error logs.
- **Usage**:
  ```bash
  python scripts/run_ui_tests.py
  python scripts/run_ui_tests.py -k "test_baseline_completeness"
  ```

---

### 12. Status Inspector (`status.py`)
- **Purpose**: CLI inspector that parses comparison JSON reports (`comparison_report_admin.json`, `comparison_report.json`) and prints:
  - Page drift summary (MATCHED, MODIFIED, MISSING, ADDED).
  - Telemetry diagnostics (Console JS errors, uncaught exceptions, HTTP 4xx/5xx errors, failed requests).
  - Exact file references and URL line-items.
- **Usage**:
  ```bash
  python scripts/status.py
  python scripts/status.py reports/ui_regression/comparison_report_admin.json
  ```

---

## 🛠️ Universal CLI Flags & Options

| Flag | Script Types | Description | Example |
| :--- | :--- | :--- | :--- |
| `--headed` | All Scripts | Launches visible Chromium browser window instead of background headless mode. | `--headed` |
| `--slowmo <ms>` | Workflow Runners | Adds a delay in milliseconds between Playwright actions (ideal for visual inspection). | `--slowmo 300` |
| `--portal <name>` | Master & UI Runners | Selects target portal (`admin`, `client`, `trade`, `shared`, `both`, `all`). | `--portal admin` |
| `-m <marker>` | Workflow Runners | Pytest marker expression (`smoke`, `regression`, `orders`, `mam`, `pamm`, `critical`). | `-m "smoke or critical"` |
| `-k <expression>` | Workflow Runners | Pytest name filter substring. | `-k "test_deposit"` |
| `-v` / `-vv` | Workflow Runners | Pytest verbosity level. | `-vv` |
| `-n <workers>` | Workflow Runners | Parallel execution using pytest-xdist. | `-n 4` |
| `--dist <mode>` | Workflow Runners | Parallel distribution mode (`loadfile`, `load`, `loadgroup`). | `--dist loadfile` |
| `--viewports <names>`| UI Runners | Restricts UI crawl/comparison to specific viewports (`desktop`, `mobile`, `tablet`). | `--viewports desktop mobile` |
| `--skip-crawl` | Full UI Pipeline | Skips baseline extraction and immediately runs comparison. | `--skip-crawl` |
| `--max-pages <N>` | UI Crawler | Limits the maximum number of pages crawled per viewport. | `--max-pages 25` |
| `--max-depth <N>` | UI Crawler | Limits link traversal depth during crawling. | `--max-depth 3` |

---

## 📈 Reporting & Test Output Formats (JSON + TXT)

The test framework features dual-format reporting with intelligent session isolation:

### 1. Single Module Execution vs Full Test Suite
- **Single Module Run** (e.g. running `python scripts/run_admin_tests.py`):
  - Overwrites previous test run logs to keep the active report scoped strictly to the current module being tested.
  - Generates dedicated individual test logs for each test in `reports/workflows/logs/individual/admin_portal/<test_name>.txt`.
- **Full Test Suite Run** (e.g. running `python scripts/run_all_workflows.py`):
  - Aggregates results from **every module** across all three portals into a consolidated master report without omitting any test.

### 2. Available Report Artifacts

| Report Path | Format | Description |
| :--- | :--- | :--- |
| `reports/workflows/logs/global_test_summary.txt` | **TXT** | Human-readable summary of total runs, pass rate, and portal-by-portal breakdown for behavioral workflows. |
| `reports/workflows/logs/global_passed_tests.txt` | **TXT** | Detailed block log of all passed workflow tests with test ID, humanized meaning, and status. |
| `reports/workflows/logs/global_failed_tests.txt` | **TXT** | Detailed workflow failure logs with error reason, line numbers, and traceback. |
| `reports/workflows/logs/global_skipped_tests.txt` | **TXT** | Detailed log of skipped workflow tests and reasoning. |
| `reports/workflows/logs/global_test_results.json` | **JSON** | Full structured JSON dataset of all workflow test outcomes, durations, and metadata. |
| `reports/workflows/logs/summary_report.json` | **JSON** | Standard summary JSON with overall metrics and breakdown by portal. |
| `reports/validations/logs/global_test_summary.txt` | **TXT** | Human-readable summary for all 434 validation tests across Admin, Client, and Trade portals. |
| `reports/validations/logs/global_passed_tests.txt` | **TXT** | Detailed block log of all passed validation tests. |
| `reports/validations/logs/global_test_results.json` | **JSON** | Full structured JSON telemetry dataset for validation tests. |
| `reports/validations/history/<RunType> - <Date>_<Time>/` | **Archive** | Full archived session snapshot of logs, screenshots, traces, and diagnostics on each fresh session. |
| `reports/mock/logs/global_test_summary.txt` | **TXT** | Human-readable summary for all 269 mock tests across Trade Terminal, Admin, and Client portals. |
| `reports/mock/logs/global_passed_tests.txt` | **TXT** | Detailed block log of all passed mock tests with humanized meanings. |
| `reports/mock/logs/global_test_results.json` | **JSON** | Full structured JSON dataset of mock test outcomes, durations, and injected scenarios. |
| `reports/mock/history/<RunType> - <Date>_<Time>/` | **Archive** | Archived mock run session snapshots with logs, screenshots, and diagnostics. |
| `reports/workflows/logs/individual/<portal>/<test>.txt`| **TXT** | Isolated diagnostic log with captured stdout/stderr, timestamps, and stack traces. |
| `reports/ui_regression/comparison_report_admin.json` | **JSON** | Detailed DOM element drift and runtime telemetry error log for Admin Portal. |
| `reports/ui_regression/comparison_report.json` | **JSON** | Detailed DOM element drift and runtime telemetry error log for Client Portal. |

### 3. Example JSON Report Schema (`summary_report.json`)
```json
{
  "timestamp": "2026-10-01T12:00:00.000000",
  "summary": {
    "total_tests": 920,
    "passed": 912,
    "failed": 0,
    "skipped": 8,
    "pass_rate_percentage": 99.13,
    "total_duration_seconds": 184.32,
    "portal_breakdown": {
      "Admin Portal": {
        "total": 425,
        "passed": 425,
        "failed": 0,
        "skipped": 0,
        "duration_seconds": 82.10
      },
      "Client Portal": {
        "total": 161,
        "passed": 161,
        "failed": 0,
        "skipped": 0,
        "duration_seconds": 34.20
      },
      "Trade Terminal": {
        "total": 158,
        "passed": 150,
        "failed": 0,
        "skipped": 8,
        "duration_seconds": 38.50
      },
      "Shared & Integrations": {
        "total": 176,
        "passed": 176,
        "failed": 0,
        "skipped": 0,
        "duration_seconds": 29.52
      }
    }
  },
  "failed_tests": [],
  "skipped_tests": [...]
}
```

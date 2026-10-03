# Testing Framework Architecture

This document describes the high-level architecture of the test automation repository, detailing why the **UI Regression Layer** and the **Behavioral & Validation Workflow Layer** are structured, how boundaries are maintained, and how multi-developer collaboration is structured across portals.

---

## 1. Conceptual Model: Dual-Layer Testing

```text
                    TEST AUTOMATION
                          │
             ┌────────────┴────────────┐
             │                         │
       UI REGRESSION              WORKFLOWS
       DOM STRUCTURE             BEHAVIORAL & VALIDATION
             │                         │
       crawler/comparer          Trade / Admin / Client
             │                         │
   "Has the UI/DOM structure    "Can a user perform workflows
    changed from baseline?"      and are all inputs validated?"
```

### Why These Systems Are Logically Separated

| Dimension | `ui_regression/` (DOM Structural Regression) | `workflows/` (Behavioral & Validation Layer) |
| :--- | :--- | :--- |
| **Primary Question** | *"Did any element change, move, disappear, or introduce unexpected CSS/attribute drift?"* | *"Can an end user perform workflows and are all boundaries, calculations, and security payloads guarded?"* |
| **Execution Style** | Breadth-first crawl across canonical routes at 5 viewports (`sm`, `md`, `lg`, `xl`, `2xl`). | Linear, action-driven user journeys (click, fill, wait, assert) and boundary validation testing. |
| **Ground Truth** | Static, approved JSON element trees stored in `element_output/` and `element_output_admin/`. | Dynamic business expectations and security vectors (`validation_payloads.py`). |
| **Noise Filtering** | 6-tier matching engine normalizing timestamps, prices, ticket IDs, and loading skeletons. | Targeted Playwright locators asserting specific UI states or server responses. |
| **Failure Indication** | Visual, layout, or structural drift from release milestones. | Functional bug, broken calculation, or missing input validation. |
| **Speed & Cadence** | Deep audits run against staging/preprod or before major releases. | Fast smoke, regression, and validation suites (434 tests) run on feature PRs and CI. |

---

## 2. Target Directory Structure & Boundary Layout

```text
Complete-Test/
│
├── ui_regression/                    # DOM-level structural/UI regression testing (29 tests)
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   ├── comparer/                     # 6-tier matching engine & drift comparer
│   ├── element_output/               # Authoritative Client baseline DOM snapshots (sm-2xl)
│   ├── element_output_admin/         # Authoritative Admin baseline DOM snapshots (sm-2xl)
│   └── tests/                        # DOM regression unit & matching accuracy tests
│
├── workflows/                        # Behavioral & Validation Testing Layer (1,354 tests)
│   ├── conftest.py                   # Root workflow fixtures (browser lifecycle)
│   │
│   ├── trade_terminal/               # Developer 1 Domain: Trade Terminal (395 tests)
│   │   ├── conftest.py               # Trade fixtures loader
│   │   ├── pages/                    # Trade Page Objects (LoginPage, OrderEntryPage, WatchlistPage)
│   │   ├── tests/                    # Workflow (test_trade_*.py) & Validation (test_val_trade_*.py)
│   │   ├── fixtures/                 # Trade-specific session & page fixtures
│   │   └── utils/                    # Trade calculation & helper functions
│   │
│   ├── admin_portal/                 # Developer 2 Domain: Admin Portal (554 tests)
│   │   ├── conftest.py               # Admin fixtures loader
│   │   ├── pages/                    # Admin Page Objects (AdminLoginPage, UserManagementPage)
│   │   ├── tests/                    # Workflow (test_admin_*.py) & Validation (test_val_admin_*.py)
│   │   ├── fixtures/                 # Admin session & page fixtures
│   │   └── utils/                    # Admin navigation helpers, query utilities
│   │
│   ├── client_portal/                # Developer 3 Domain: Client Portal (246 tests)
│   │   ├── conftest.py               # Client fixtures loader
│   │   ├── pages/                    # Client Page Objects (ClientLoginPage, ClientDepositPage)
│   │   ├── tests/                    # Workflow (test_client_*.py) & Validation (test_val_client_*.py)
│   │   ├── fixtures/                 # Client session & page fixtures
│   │   └── utils/                    # Client validation utilities, session recovery
│   │
│   └── shared/                       # Reusable infrastructure & shared helpers
│       ├── pages/base_page.py        # Abstract BasePage with resilient Playwright helpers
│       ├── helpers/                  # validation_payloads.py, math_assertions.py
│       ├── fixtures/                 # browser_fixtures.py, auth_fixtures.py
│       ├── utils/                    # test_logger.py, diagnostics.py, error_monitor.py, waits.py
│       ├── constants/                # timeouts.py, viewports.py, routes.py
│       └── assertions/               # Domain-agnostic assertion wrappers
│
├── config/                           # Centralized configuration loaded from .env
│   └── settings.py
│
├── auth/                             # Cached storage state sessions (gitignored)
├── reports/                          # Segregated multi-suite reporting and history
│   ├── validations/                  # Active validation logs, screenshots, diagnostics, traces & history
│   ├── workflows/                    # Active workflow logs, screenshots, traces & history
│   └── ui_regression/                # DOM drift comparison reports & history
│
├── scripts/                          # Test runner CLI entrypoints
├── docs/                             # Engineering documentation & testing specifications
├── conftest.py                       # Root pytest conftest (telemetry hooks, session routing)
├── pytest.ini                        # Pytest discovery settings and markers
└── requirements.txt                  # Minimal Python dependencies
```

---

## 3. Dependency & Boundary Isolation Rules

To prevent coupling and merge conflicts between teammates, the following boundary rules are strictly enforced:

```text
┌────────────────────────────────────────────────────────┐
│                      workflows/                        │
│                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  │  trade_terminal/ │  │  admin_portal/   │  │  client_portal/  │
│  │   (Developer 1)  │  │   (Developer 2)  │  │   (Developer 3)  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
│           │                     │                     │
│           └──────────────┬──────┴─────────────────────┘
│                          ▼
│               ┌──────────────────────┐
│               │   workflows/shared/  │
│               └──────────────────────┘
└────────────────────────────────────────────────────────┘
                           │
                           ▼
               ┌──────────────────────┐
               │    config/settings   │
               └──────────────────────┘
```

1. **Portal Independence**: Code in `workflows/trade_terminal/` must **never** import from `workflows/admin_portal/` or `workflows/client_portal/`.
2. **Shared Infrastructure Gate**: Only genuinely reusable components (`BasePage`, `validation_payloads.py`, `math_assertions.py`, browser helpers, waits) belong in `workflows/shared/`.
3. **UI Regression Isolation**: `workflows/` does not import from `ui_regression/`, and `ui_regression/` does not import from `workflows/`.
4. **Configuration Unification**: Both systems read configuration from environment variables via `config/settings.py`, ensuring single-source-of-truth environment management.

---

## 4. Execution Flow Diagrams

### Validation & Workflow Execution Flow
```text
pytest -m validation -v
               │
               ▼
      [root conftest.py] ──> Initializes GlobalTestLogger targeting reports/validations/
               │
               ▼
 [portal/conftest.py] ──> Injects portal fixtures & authenticated context
               │
               ▼
   [Page Object Models] ──> Executes user actions, fills boundary payloads, checks math
               │
               ▼
[Telemetry & Reporting] ──> Captures console errors, failed requests, HTTP 4xx/5xx headers/payloads
               │
               ▼
 [Flushes Summary & JSON] ──> Finalizes reports/validations/logs/global_test_summary.txt
```

### DOM Regression Execution Flow
```text
python scripts/run_ui_compare.py
               │
               ▼
   [Load Baseline JSON] ──> Reads snapshots from ui_regression/element_output/
               │
               ▼
   [Live Crawl Engine]  ──> Launches Chromium, crawls canonical routes across 5 viewports
               │
               ▼
  [6-Tier Comparer Pass] ──> Matches elements via Unique ID, Semantic Attrs, Fallbacks
               │
               ▼
    [Noise Filtering]   ──> Normalizes dynamic timestamps, numbers, and chart noise
               │
               ▼
   [Report Generation]  ──> Saves structured comparison_report.json to reports/ui_regression/
```

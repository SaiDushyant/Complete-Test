# Testing Framework Architecture

This document describes the high-level architecture of the test automation repository, detailing why the **UI Regression Layer** and the **Behavioral Workflow Layer** are intentionally separated, how boundaries are maintained, and how multi-developer collaboration is structured across portals.

---

## 1. Conceptual Model: Dual-Layer Testing

```text
                    TEST AUTOMATION
                          │
             ┌────────────┴────────────┐
             │                         │
       UI REGRESSION              WORKFLOWS
       DOM STRUCTURE             APPLICATION BEHAVIOR
             │                         │
       crawler/comparer          Trade/Admin/Client
             │                         │
   "Has the UI/DOM structure    "Can a user successfully
    changed from baseline?"      perform workflows?"
```

### Why These Systems Are Intentionally Separated

| Dimension | `ui_regression/` (DOM Structural Regression) | `workflows/` (Behavioral / E2E Workflows) |
| :--- | :--- | :--- |
| **Primary Question** | *"Did any element change, move, disappear, or introduce unexpected CSS/attribute drift?"* | *"Can an end user log in, place an order, approve a user, or withdraw funds successfully?"* |
| **Execution Style** | Breadth-first crawl across canonical routes at 5 viewports (`sm`, `md`, `lg`, `xl`, `2xl`). | Linear, action-driven user journeys (click, fill, wait, assert). |
| **Ground Truth** | Static, approved JSON element trees stored in `element_output/` and `element_output_admin/`. | Dynamic business expectations (e.g. order filled, balance updated). |
| **Noise Filtering** | 6-tier matching engine normalizing timestamps, prices, ticket IDs, and loading skeletons. | Targeted Playwright locators asserting specific UI states or backend effects. |
| **Failure Indication** | Visual, layout, or structural drift from release milestones. | Functional bug, broken business logic, or server error. |
| **Speed & Cadence** | Deep audits run against staging/preprod or before major releases. | Fast smoke and regression suites run on feature PRs and CI. |

Combining these two concerns into a single test runner or mixing crawler code into workflow Page Objects creates fragile tests, tight coupling, and maintenance bottlenecks. Keeping them logically independent allows each system to specialize without interfering with the other.

---

## 2. Target Directory Structure & Boundary Layout

```text
Playwrite/new/
│
├── ui_regression/                    # DOM-level structural/UI regression testing
│   ├── crawler/                      # Multi-viewport crawler & element extractor
│   │   ├── crawler.py                # Asynchronous BFS crawler
│   │   ├── crawler_config.py         # Viewport breakpoints, timeouts, output paths
│   │   ├── element_extractor.py      # In-browser DOM element attribute extractor
│   │   ├── auth.py                   # Client portal authentication
│   │   ├── auth_admin.py             # Admin console authentication
│   │   ├── run_crawler.py            # Client portal crawler CLI entry point
│   │   └── run_crawler_admin.py      # Admin portal crawler CLI entry point
│   │
│   ├── comparer/                     # Multi-tier element matcher & drift detector
│   │   ├── comparer.py               # 6-tier matching algorithm & NoiseFilter
│   │   ├── comparer_config.py        # Baseline dirs, report output paths, viewports
│   │   ├── run_comparer.py           # Client live vs baseline comparison CLI
│   │   └── run_comparer_admin.py     # Admin live vs baseline comparison CLI
│   │
│   ├── element_output/               # Authoritative Client baseline DOM snapshots (sm-2xl)
│   ├── element_output_admin/         # Authoritative Admin baseline DOM snapshots (sm-2xl)
│   └── tests/                        # DOM regression unit & matching accuracy tests
│       ├── test_baseline_live_urls.py # Canonical routes & cross-environment matching
│       ├── test_comparer_accuracy.py  # Cascade prevention & noise filter unit tests
│       └── test_viewports.py          # 5-viewport definitions & segregation tests
│
├── workflows/                        # Behavioral / Functional / E2E testing layer
│   ├── conftest.py                   # Root workflow fixtures (browser lifecycle, failure hooks)
│   │
│   ├── trade_terminal/               # Developer 1 Domain: Trade Terminal
│   │   ├── conftest.py               # Trade fixtures loader
│   │   ├── pages/                    # Trade Terminal Page Objects (LoginPage, OrderEntryPage)
│   │   ├── tests/                    # Trade Terminal behavioral tests (test_trade_example.py)
│   │   ├── fixtures/                 # Trade-specific session & page fixtures
│   │   ├── test_data/                # Symbols, lot sizes, order payloads
│   │   └── utils/                    # Trade calculation & helper functions
│   │
│   ├── admin_portal/                 # Developer 2 Domain: Admin Portal
│   │   ├── conftest.py               # Admin fixtures loader
│   │   ├── pages/                    # Admin Console Page Objects (AdminLoginPage, AdminDashboardPage)
│   │   ├── tests/                    # Admin behavioral tests (test_admin_example.py)
│   │   ├── fixtures/                 # Admin session & page fixtures
│   │   ├── test_data/                # User roles, permission matrices, mock data
│   │   └── utils/                    # Admin-specific helper functions
│   │
│   ├── client_portal/                # Developer 3 Domain: Client Portal
│   │   ├── conftest.py               # Client fixtures loader
│   │   ├── pages/                    # Client Page Objects (ClientLoginPage, ClientWatchlistPage)
│   │   ├── tests/                    # Client behavioral tests (test_client_example.py, test_client_watchlist.py)
│   │   ├── fixtures/                 # Client session & page fixtures
│   │   ├── test_data/                # Deposit amounts, KYC documents, profile payloads
│   │   └── utils/                    # Client-specific helper functions
│   │
│   └── shared/                       # Reusable infrastructure (shared across portals)
│       ├── pages/base_page.py        # Abstract BasePage with resilient Playwright helpers
│       ├── fixtures/                 # browser_fixtures.py, auth_fixtures.py
│       ├── utils/                    # waits.py, logger.py, screenshot.py, browser.py
│       ├── constants/                # timeouts.py, viewports.py, routes.py
│       ├── assertions/assert_helpers.py # Domain-agnostic assertion wrappers
│       └── test_data/common_data.py  # Common random generators (emails, strings)
│
├── config/                           # Centralized configuration
│   ├── settings.py                   # Unified dataclass configuration loaded from .env
│   └── environments/                 # Environment profiles (staging.py, production.py, local.py)
│
├── auth/                             # Cached storage state sessions (gitignored)
├── reports/                          # Segregated report directories (gitignored)
│   ├── ui_regression/                # DOM drift comparison reports (JSON)
│   └── workflows/                    # Failure screenshots, Playwright traces
│
├── scripts/                          # Convenience execution scripts
├── docs/                             # Engineering documentation
├── .github/                          # PR templates and GitHub collaboration assets
├── .env.example                      # Environment variables template
├── .gitignore                        # Git exclusion rules
├── conftest.py                       # Root pytest conftest (session browser, failure hooks)
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
2. **Shared Infrastructure Gate**: Only genuinely reusable components (`BasePage`, browser helpers, waits, common assertions) belong in `workflows/shared/`.
3. **UI Regression Isolation**: `workflows/` does not import from `ui_regression/`, and `ui_regression/` does not import from `workflows/`.
4. **Configuration Unification**: Both systems read configuration from environment variables via `config/settings.py` or dedicated fallback config modules, ensuring single-source-of-truth environment management without competing config mechanisms.

---

## 4. Execution Flow Diagrams

### Behavioral Workflow Execution Flow
```text
pytest workflows/trade_terminal/tests
               │
               ▼
   [workflows/conftest.py] ──> Initializes workflow_browser fixture
               │
               ▼
[trade_terminal/conftest.py] ──> Injects trade_fixtures & authenticated context
               │
               ▼
     [TradeLoginPage / OrderEntryPage] ──> Executes user actions via BasePage
               │
               ▼
       [Pass / Fail] ──> On failure: automatic screenshot & trace saved to reports/workflows/
```

### DOM Regression Execution Flow
```text
python -m ui_regression.comparer.run_comparer
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

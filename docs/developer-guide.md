# Developer Onboarding & Quick-Start Guide

Welcome to the Automated UI Regression and Workflow Testing repository. This guide walks you through the complete 15-step procedure from cloning the repository to creating Page Objects, writing tests, and opening your first Pull Request.

---

## 15-Step Developer Onboarding Procedure

### Step 1: Clone Repository
Clone the repository using your team's Git URL:
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <repository-folder>
```

### Step 2: Create Virtual Environment
Create an isolated Python 3.12+ virtual environment:

**macOS / Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt (CMD)**:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
Install the project requirements into your active virtual environment:
```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers
Install the Chromium browser binary required by Playwright:
```bash
playwright install chromium
```

### Step 5: Create Local `.env` Configuration
Copy the template configuration file:
```bash
cp .env.example .env
```
Open `.env` in your editor and configure the endpoints and credentials for your assigned portal:
- **Developer 1 (Trade Terminal)**: Set `TRADE_USERNAME` and `TRADE_PASSWORD`
- **Developer 2 (Admin Portal)**: Set `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- **Developer 3 (Client Portal)**: Set `CLIENT_USERNAME` and `CLIENT_PASSWORD`

> ⚠️ **CRITICAL SECURITY NOTE**: Never commit `.env` to Git. The `.gitignore` file is pre-configured to exclude `.env` and `auth/*.json`.

### Step 6: Run a Smoke / Example Test
Verify your setup by running the fast smoke test suite or the DOM regression suite:
```bash
# Verify DOM regression test collection and execution
pytest ui_regression/tests/

# Verify workflow test collection
pytest workflows/ --collect-only
```

### Step 7: Understand Repository Structure
Review the dual-layer architecture:
- `ui_regression/`: DOM-level structural regression framework (crawler, comparer, baselines).
- `workflows/`: Behavioral E2E tests, Page Objects, fixtures, and test data.
- Read **[Architecture Overview](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/architecture.md)** and **[Ownership Matrix](file:///Users/xtremenext_viji/Code/Playwrite/new/docs/ownership.md)** to identify your primary working directory.

### Step 8: Create Feature Branch
Always create a feature branch off an up-to-date `main`:
```bash
git checkout main
git pull origin main
git checkout -b feature/<portal>-<short-description>
```
*Branch naming examples:*
- `feature/trade-order-placement`
- `feature/admin-user-verification`
- `feature/client-watchlist-toggle`

### Step 9: Add Page Object
Add your new Page Object inside your portal's `pages/` directory, subclassing `BasePage`:

```python
# File: workflows/trade_terminal/pages/order_entry_page.py
from __future__ import annotations
from playwright.sync_api import Page, expect
from workflows.shared.pages.base_page import BasePage

class OrderEntryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.symbol_input = page.locator("input#order-symbol")
        self.volume_input = page.locator("input#order-volume")
        self.buy_button = page.locator("button#order-buy-btn")
        self.success_toast = page.locator(".toast-success")

    def place_market_buy_order(self, symbol: str, volume: str) -> None:
        self.symbol_input.fill(symbol)
        self.volume_input.fill(volume)
        self.buy_button.click()

    def is_order_confirmed(self) -> bool:
        return self.success_toast.is_visible()
```

### Step 10: Add Workflow Test
Create your test inside your portal's `tests/` directory, using relevant fixtures and markers:

```python
# File: workflows/trade_terminal/tests/test_order_placement.py
import pytest
from workflows.trade_terminal.pages.order_entry_page import OrderEntryPage

@pytest.mark.trade
@pytest.mark.regression
def test_user_can_place_market_order(order_entry_page: OrderEntryPage):
    """Verify that an authenticated trader can place a market buy order."""
    order_entry_page.place_market_buy_order(symbol="EURUSD", volume="1.0")
    assert order_entry_page.is_order_confirmed(), (
        "Expected success notification after placing market order."
    )
```

### Step 11: Run Relevant Tests
Execute your portal's tests and ensure existing suites remain green:
```bash
# Run your portal's tests:
pytest workflows/trade_terminal/tests

# Run the DOM regression test suite:
pytest ui_regression/tests/
```

### Step 12: Review Changes
Check your working tree before staging:
```bash
git status
git diff
```
Ensure:
- No temporary files, debug prints, or scratch JSON files are present.
- No files in `.env` or `auth/` were modified or staged.
- Only files within your portal directory (or coordinated shared additions) were touched.

### Step 13: Commit
Stage only your specific files and write a semantic commit message:
```bash
git add workflows/trade_terminal/pages/order_entry_page.py
git add workflows/trade_terminal/tests/test_order_placement.py
git commit -m "feat(trade): add market order placement page and workflow test"
```

### Step 14: Push Feature Branch
Push your branch to GitHub and set upstream tracking:
```bash
git push -u origin feature/<portal>-<short-description>
```

### Step 15: Open Pull Request
1. Navigate to the repository on GitHub.
2. Click **Compare & pull request**.
3. Complete the standardized template from `.github/pull_request_template.md`:
   - Select your portal.
   - List tests added/changed.
   - Note local test commands executed and results.
   - Verify all pre-merge checklist items.
4. Request reviews from your teammates.

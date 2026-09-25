# Git & GitHub Team Collaboration Workflow

This document defines the team Git standards, branching strategy, daily development workflow, rebase routines, and merge conflict resolution procedures for all three developers working concurrently in this repository.

---

## 1. Branching Strategy

The repository follows a trunk-based feature-branch workflow centered on `main`:

```text
main (Protected — No direct commits)
 │
 ├── feature/trade-login-workflow       (Developer 1)
 ├── feature/trade-order-placement      (Developer 1)
 │
 ├── feature/admin-user-management      (Developer 2)
 ├── feature/admin-role-permissions     (Developer 2)
 │
 ├── feature/client-profile-update      (Developer 3)
 └── feature/client-watchlist-toggle    (Developer 3)
```

### Branch Naming Conventions
Always prefix your branch name with `feature/` followed by your portal identifier:
- `feature/trade-<feature-name>` (Developer 1)
- `feature/admin-<feature-name>` (Developer 2)
- `feature/client-<feature-name>` (Developer 3)
- `chore/shared-<feature-name>` (Shared framework updates)
- `fix/<portal>-<bug-description>` (Targeted bug fixes)

> ⛔ **STRICT RULE**: Never commit or push directly to `main`. All changes must arrive in `main` through reviewed Pull Requests.

---

## 2. First-Time Setup on a New Machine

### Step 1: Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <repository-folder>
```

### Step 2: Configure Git User Identity (If not set globally)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Create and Activate Virtual Environment

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

### Step 4: Install Dependencies & Browsers
```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 5: Configure Local Environment
```bash
cp .env.example .env
```
Fill in the credentials for your portal in `.env`.

> 🔒 **Security Notice**: Never commit `.env`. It is excluded by `.gitignore`.

---

## 3. Daily Workflow: Starting New Work

### Step 1: Sync Your Local `main`
Always pull the latest changes before branching:
```bash
git checkout main
git pull origin main
```

### Step 2: Create a Dedicated Feature Branch
```bash
git checkout -b feature/trade-order-placement
```

### Step 3: Make Changes Confined to Your Portal
Develop within your designated directory (`workflows/<portal>/`).

### Step 4: Verify Status and Diff
Before staging files, check what changed:
```bash
git status
git diff
```

### Step 5: Run Tests Locally
Run your portal tests and the DOM regression suite to ensure nothing is broken:
```bash
# Portal tests:
pytest workflows/trade_terminal/tests

# DOM regression suite:
pytest ui_regression/tests/
```

### Step 6: Stage and Commit
Stage only specific, relevant files:
```bash
git add workflows/trade_terminal/pages/order_entry_page.py
git add workflows/trade_terminal/tests/test_order_placement.py
git commit -m "feat(trade): add market order placement workflow test"
```

### Step 7: Push Feature Branch to GitHub
```bash
git push -u origin feature/trade-order-placement
```

---

## 4. Keeping Your Branch Updated from `main`

While you work, teammates may merge PRs into `main`. Keep your feature branch up to date using a safe Git rebase.

### Why Rebase?
Rebase replays your branch's commits on top of the latest `main`, producing a clean, linear project history without messy merge commits.

### Safe Rebase Procedure

#### 1. Check for Uncommitted Changes First
```bash
git status
```
If you have uncommitted changes, commit them or stash them safely:
```bash
git stash save "WIP: my in-progress work"
```

#### 2. Fetch Latest Upstream Commits
```bash
git fetch origin
```

#### 3. Rebase Your Branch onto `origin/main`
```bash
git rebase origin/main
```

#### 4. Restore Stashed Changes (if you stashed earlier)
```bash
git stash pop
```

#### Alternative: Standard Merge Approach
If you are uncomfortable with rebase, you can merge `main` into your feature branch:
```bash
git fetch origin
git merge origin/main
```
Both approaches are valid, but rebase is preferred for a cleaner Git history.

---

## 5. Resolving Merge Conflicts

### Why Conflicts Happen
A conflict occurs when two branches modify the exact same lines of the same file, and Git cannot automatically decide which version to keep. Because Developers 1, 2, and 3 work in separate portal directories, conflicts in portal code should be extremely rare. Conflicts typically only happen if two developers modify shared files (e.g., `workflows/shared/`, `conftest.py`, `pytest.ini`, or `requirements.txt`).

### Step-by-Step Conflict Resolution (During Rebase)

#### 1. Inspect Conflicted Files
Git will pause the rebase and notify you:
```bash
git status
```
Files with conflicts will be listed under `"Unmerged paths:"`.

#### 2. Open and Edit the Conflicted Files
Look for standard Git conflict markers:
```text
<<<<<<< HEAD (Current main version)
DEFAULT_TIMEOUT = 30000
=======
DEFAULT_TIMEOUT = 45000
>>>>>>> feature/trade-order-placement (Your commit)
```
Discuss with your teammate if needed, choose or combine the correct code, and delete the marker lines (`<<<<<<<`, `=======`, `>>>>>>>`).

#### 3. Test After Resolving
Ensure syntax is valid and tests pass:
```bash
pytest ui_regression/tests/
```

#### 4. Stage Resolved Files and Continue Rebase
```bash
git add <resolved-file-path>
git rebase --continue
```
Repeat until the rebase completes successfully.

#### 5. How to Abort Safely
If the rebase becomes confusing or you want to return to your exact starting state without losing any work:
```bash
git rebase --abort
```
This safely undoes the rebase operation completely.

---

## 6. Team Rules to Prevent Conflicts

1. **Strict Portal Separation**:
   - Developer 1 works in `workflows/trade_terminal/`
   - Developer 2 works in `workflows/admin_portal/`
   - Developer 3 works in `workflows/client_portal/`
2. **Coordinate Shared Changes**:
   - Before modifying files in `workflows/shared/`, `config/`, `pytest.ini`, `conftest.py`, or `requirements.txt`, notify teammates in team chat.
3. **Small, Focused Pull Requests**:
   - Do not bundle multi-week refactoring into a single giant PR. Submit focused PRs addressing one feature or fix at a time.
4. **Never Touch Another Developer's Portal Directory**:
   - If you need a helper from another portal, discuss promoting it to `workflows/shared/`.

---

## 7. Recommended GitHub Repository Settings

To safeguard `main` and ensure code quality, configure these settings in GitHub repository settings:

### Branch Protection Rules for `main`
1. Navigate to: **Settings** → **Branches** → **Add branch protection rule**
2. Branch name pattern: `main`
3. Enable:
   - **Require a pull request before merging**
   - **Require approvals** (minimum 1 approval from a teammate)
   - **Require status checks to pass before merging** (e.g. CI workflow running `pytest`)
   - **Require branches to be up to date before merging**
   - **Do not allow bypassing the above settings**
   - **Include administrators**

---

## 8. Continuous Integration (CI) Strategy

A future GitHub Actions workflow (`.github/workflows/ci.yml`) should be configured with two parallel jobs:

```text
               GitHub Actions CI Matrix
                          │
             ┌────────────┴────────────┐
             │                         │
      Job 1: DOM Regression      Job 2: Workflow Smoke Tests
             │                         │
     pytest ui_regression/       pytest -m smoke
```

- **Job 1** runs unit and accuracy tests for the DOM regression system without needing external network access or production secrets.
- **Job 2** runs workflow smoke tests using mock or test environments configured via GitHub repository secrets.

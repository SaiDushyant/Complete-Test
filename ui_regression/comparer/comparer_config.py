import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# UI regression directory and Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT_DIR.parent

# Baseline element directory
BASELINE_DIR = ROOT_DIR / "element_output"

# Admin baseline element directory
ADMIN_BASELINE_DIR = ROOT_DIR / "element_output_admin"

# Comparison report output path in reports/ui_regression directory
REPORTS_DIR = PROJECT_ROOT / "reports" / "ui_regression"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
COMPARISON_REPORT_FILE = REPORTS_DIR / "comparison_report.json"

# Admin comparison report output path in reports/ui_regression directory
ADMIN_COMPARISON_REPORT_FILE = REPORTS_DIR / "comparison_report_admin.json"

# Headless mode
HEADLESS = os.getenv("CRAWLER_HEADLESS", "true").lower() == "true"

# Centralized Viewport and URL Configuration
from crawler.crawler_config import (
    ADMIN_BASE_URL,
    ADMIN_LOGIN_URL,
    BASE_URL,
    BASELINE_ADMIN_AUTH_STATE,
    BASELINE_ADMIN_BASE_URL,
    BASELINE_ADMIN_LOGIN_URL,
    BASELINE_AUTH_STATE,
    BASELINE_URL,
    DEFAULT_VIEWPORT,
    DEFAULT_VIEWPORT_HEIGHT,
    DEFAULT_WORKERS,
    LIVE_ADMIN_AUTH_STATE,
    LIVE_ADMIN_BASE_URL,
    LIVE_ADMIN_LOGIN_URL,
    LIVE_AUTH_STATE,
    LIVE_URL,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    get_viewport_config,
    parse_viewports,
)


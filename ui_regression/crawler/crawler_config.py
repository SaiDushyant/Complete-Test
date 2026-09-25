import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Root directory of the UI regression module and Project root
ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT_DIR.parent

# Authentication state files directory in auth/
AUTH_DIR = PROJECT_ROOT / "auth"
AUTH_DIR.mkdir(parents=True, exist_ok=True)
AUTH_STATE = AUTH_DIR / "auth_state.json"

# Output directory for extracted page JSON files
OUTPUT_DIR = ROOT_DIR / "element_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Crawl report output path
REPORT_FILE = OUTPUT_DIR / "crawl_report.json"

# ============================================================
# CENTRALIZED VIEWPORT CONFIGURATION (5-VIEWPORT REGRESSION)
# ============================================================

DEFAULT_VIEWPORT_HEIGHT = int(os.getenv("CRAWLER_VIEWPORT_HEIGHT", "800"))

VIEWPORTS = {
    "sm": {"width": 640, "height": DEFAULT_VIEWPORT_HEIGHT},
    "md": {"width": 768, "height": DEFAULT_VIEWPORT_HEIGHT},
    "lg": {"width": 1024, "height": DEFAULT_VIEWPORT_HEIGHT},
    "xl": {"width": 1280, "height": DEFAULT_VIEWPORT_HEIGHT},
    "2xl": {"width": 1536, "height": DEFAULT_VIEWPORT_HEIGHT},
}

VIEWPORT_ORDER = ["sm", "md", "lg", "xl", "2xl"]
VIEWPORT_NAMES = list(VIEWPORTS.keys())
DEFAULT_VIEWPORT = "xl"


def get_viewport_config(name: str) -> dict:
    """Return viewport width and height dictionary for a given viewport name."""
    clean_name = (name or "").strip().lower()
    if clean_name in VIEWPORTS:
        return VIEWPORTS[clean_name]
    raise ValueError(f"Unknown viewport '{name}'. Valid viewports are: {VIEWPORT_NAMES}")


def parse_viewports(viewports_arg=None) -> list:
    """
    Parse a comma-separated string or list of viewport names into a validated list of viewports.
    Defaults to all 5 viewports if None or empty.
    """
    if not viewports_arg:
        return list(VIEWPORT_ORDER)

    if isinstance(viewports_arg, str):
        candidates = [v.strip().lower() for v in viewports_arg.split(",") if v.strip()]
    elif isinstance(viewports_arg, (list, tuple, set)):
        candidates = [str(v).strip().lower() for v in viewports_arg if str(v).strip()]
    else:
        return list(VIEWPORT_ORDER)

    validated = []
    for c in candidates:
        if c in VIEWPORTS and c not in validated:
            validated.append(c)
        elif c not in VIEWPORTS:
            raise ValueError(f"Invalid viewport '{c}'. Valid viewports are: {VIEWPORT_NAMES}")

    return validated or list(VIEWPORT_ORDER)


# ============================================================
# TARGET APPLICATION URLS (BASELINE VS LIVE)
# ============================================================

# Baseline Client Portal URL (used to crawl baseline snapshots)
BASELINE_URL = os.getenv("BASELINE_URL") or os.getenv("BASE_URL")
if not BASELINE_URL:
    raise RuntimeError("BASELINE_URL (or legacy BASE_URL) is missing from .env")

# Live Client Portal URL (used for live comparison; defaults to BASELINE_URL)
LIVE_URL = os.getenv("LIVE_URL") or BASELINE_URL

# Legacy compatibility alias
BASE_URL = BASELINE_URL

# Domains
BASELINE_DOMAIN = urlparse(BASELINE_URL).netloc
LIVE_DOMAIN = urlparse(LIVE_URL).netloc
BASE_DOMAIN = BASELINE_DOMAIN

# ============================================================
# ADMIN PANEL SETTINGS (BASELINE VS LIVE)
# ============================================================

BASELINE_ADMIN_BASE_URL = (
    os.getenv("BASELINE_ADMIN_BASE_URL")
    or os.getenv("BASELINE_ADMIN_URL")
    or os.getenv("ADMIN_BASELINE_BASE_URL")
    or os.getenv("ADMIN_BASELINE_URL")
    or os.getenv("ADMIN_BASE_URL")
    or "https://stage.xtremenext.com/admin/Controlbase/Dashboard"
)
LIVE_ADMIN_BASE_URL = (
    os.getenv("LIVE_ADMIN_BASE_URL")
    or os.getenv("LIVE_ADMIN_URL")
    or os.getenv("ADMIN_LIVE_BASE_URL")
    or os.getenv("ADMIN_LIVE_URL")
    or BASELINE_ADMIN_BASE_URL
)

# Admin legacy aliases
ADMIN_BASE_URL = BASELINE_ADMIN_BASE_URL
ADMIN_BASELINE_URL = BASELINE_ADMIN_BASE_URL
ADMIN_LIVE_URL = LIVE_ADMIN_BASE_URL

BASELINE_ADMIN_LOGIN_URL = (
    os.getenv("BASELINE_ADMIN_LOGIN_URL")
    or os.getenv("ADMIN_BASELINE_LOGIN_URL")
    or os.getenv("ADMIN_LOGIN_URL")
    or "https://stage.xtremenext.com/admin/Login/index"
)
LIVE_ADMIN_LOGIN_URL = (
    os.getenv("LIVE_ADMIN_LOGIN_URL")
    or os.getenv("ADMIN_LIVE_LOGIN_URL")
    or BASELINE_ADMIN_LOGIN_URL
)
ADMIN_LOGIN_URL = BASELINE_ADMIN_LOGIN_URL

BASELINE_ADMIN_DOMAIN = urlparse(BASELINE_ADMIN_BASE_URL).netloc
LIVE_ADMIN_DOMAIN = urlparse(LIVE_ADMIN_BASE_URL).netloc

# Allowed domains list
_allowed_env = os.getenv("CRAWLER_ALLOWED_DOMAINS", "")
ALLOWED_DOMAINS = []
if _allowed_env.strip():
    ALLOWED_DOMAINS.extend([d.strip() for d in _allowed_env.split(",") if d.strip()])
for d in (BASELINE_DOMAIN, LIVE_DOMAIN, BASELINE_ADMIN_DOMAIN, LIVE_ADMIN_DOMAIN):
    if d and d not in ALLOWED_DOMAINS:
        ALLOWED_DOMAINS.append(d)

# Credentials and Login Verification (Client Portal)
BASELINE_TEST_USER_EMAIL = os.getenv("BASELINE_TEST_USER_EMAIL") or os.getenv("TEST_USER_EMAIL", "")
LIVE_TEST_USER_EMAIL = os.getenv("LIVE_TEST_USER_EMAIL") or BASELINE_TEST_USER_EMAIL
TEST_USER_EMAIL = BASELINE_TEST_USER_EMAIL

BASELINE_TEST_USER_PASSWORD = os.getenv("BASELINE_TEST_USER_PASSWORD") or os.getenv("TEST_USER_PASSWORD", "")
LIVE_TEST_USER_PASSWORD = os.getenv("LIVE_TEST_USER_PASSWORD") or BASELINE_TEST_USER_PASSWORD
TEST_USER_PASSWORD = BASELINE_TEST_USER_PASSWORD

BASELINE_POST_LOGIN_URL_PATTERN = os.getenv("BASELINE_POST_LOGIN_URL_PATTERN") or os.getenv("POST_LOGIN_URL_PATTERN", "")
LIVE_POST_LOGIN_URL_PATTERN = os.getenv("LIVE_POST_LOGIN_URL_PATTERN") or BASELINE_POST_LOGIN_URL_PATTERN
POST_LOGIN_URL_PATTERN = BASELINE_POST_LOGIN_URL_PATTERN

POST_LOGIN_SELECTOR = os.getenv("POST_LOGIN_SELECTOR", "")

# Credentials and Login Verification (Admin Console)
BASELINE_ADMIN_USER_USERNAME = (
    os.getenv("BASELINE_ADMIN_USER_USERNAME")
    or os.getenv("ADMIN_BASELINE_USER_USERNAME")
    or os.getenv("ADMIN_USER_USERNAME", "madmin")
)
LIVE_ADMIN_USER_USERNAME = (
    os.getenv("LIVE_ADMIN_USER_USERNAME")
    or os.getenv("ADMIN_LIVE_USER_USERNAME")
    or BASELINE_ADMIN_USER_USERNAME
)
ADMIN_USER_USERNAME = BASELINE_ADMIN_USER_USERNAME

BASELINE_ADMIN_USER_PASSWORD = (
    os.getenv("BASELINE_ADMIN_USER_PASSWORD")
    or os.getenv("ADMIN_BASELINE_USER_PASSWORD")
    or os.getenv("ADMIN_USER_PASSWORD", "Test@1234")
)
LIVE_ADMIN_USER_PASSWORD = (
    os.getenv("LIVE_ADMIN_USER_PASSWORD")
    or os.getenv("ADMIN_LIVE_USER_PASSWORD")
    or BASELINE_ADMIN_USER_PASSWORD
)
ADMIN_USER_PASSWORD = BASELINE_ADMIN_USER_PASSWORD

BASELINE_ADMIN_POST_LOGIN_URL_PATTERN = (
    os.getenv("BASELINE_ADMIN_POST_LOGIN_URL_PATTERN")
    or os.getenv("ADMIN_BASELINE_POST_LOGIN_URL_PATTERN")
    or os.getenv("ADMIN_POST_LOGIN_URL_PATTERN", "**/admin/Controlbase/**")
)
LIVE_ADMIN_POST_LOGIN_URL_PATTERN = (
    os.getenv("LIVE_ADMIN_POST_LOGIN_URL_PATTERN")
    or os.getenv("ADMIN_LIVE_POST_LOGIN_URL_PATTERN")
    or BASELINE_ADMIN_POST_LOGIN_URL_PATTERN
)
ADMIN_POST_LOGIN_URL_PATTERN = BASELINE_ADMIN_POST_LOGIN_URL_PATTERN

# Public Auth Pages Helper
def get_trading_auth_pages(base_url: str = None) -> list:
    url = (base_url or BASELINE_URL).rstrip("/")
    return [
        f"{url}/login/",
        f"{url}/register/",
        f"{url}/reset/",
    ]

def get_admin_auth_pages(login_url: str = None) -> list:
    url = login_url or BASELINE_ADMIN_LOGIN_URL
    return [url]

BASELINE_TRADING_AUTH_PAGES = get_trading_auth_pages(BASELINE_URL)
LIVE_TRADING_AUTH_PAGES = get_trading_auth_pages(LIVE_URL)
TRADING_AUTH_PAGES = BASELINE_TRADING_AUTH_PAGES

BASELINE_ADMIN_AUTH_PAGES = get_admin_auth_pages(BASELINE_ADMIN_LOGIN_URL)
LIVE_ADMIN_AUTH_PAGES = get_admin_auth_pages(LIVE_ADMIN_LOGIN_URL)
ADMIN_AUTH_PAGES = BASELINE_ADMIN_AUTH_PAGES

# Authentication State Storage Files (stored in auth/ directory)
AUTH_STATE = AUTH_DIR / "auth_state.json"
BASELINE_AUTH_STATE = AUTH_DIR / "auth_state.json"
LIVE_AUTH_STATE = AUTH_DIR / "auth_state_live.json"

ADMIN_AUTH_STATE = AUTH_DIR / "auth_state_admin.json"
BASELINE_ADMIN_AUTH_STATE = AUTH_DIR / "auth_state_admin.json"
LIVE_ADMIN_AUTH_STATE = AUTH_DIR / "auth_state_admin_live.json"

ADMIN_OUTPUT_DIR = ROOT_DIR / "element_output_admin"
ADMIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ADMIN_REPORT_FILE = ADMIN_OUTPUT_DIR / "crawl_report.json"
ADMIN_COMPARISON_REPORT_FILE = PROJECT_ROOT / "reports" / "ui_regression" / "comparison_report_admin.json"

# ============================================================
# CRAWLER SAFETY & PERFORMANCE LIMITS
# ============================================================

MAX_DEPTH = int(os.getenv("CRAWLER_MAX_DEPTH", "10"))
MAX_PAGES = int(os.getenv("CRAWLER_MAX_PAGES", "100"))
DEFAULT_WORKERS = int(os.getenv("CRAWLER_WORKERS", "5"))
WAIT_AFTER_LOAD = int(os.getenv("CRAWLER_WAIT_AFTER_LOAD", "1000"))
TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", "60000"))
HEADLESS = os.getenv("CRAWLER_HEADLESS", "true").lower() == "true"

# ============================================================
# STATIC / DOWNLOAD FILE EXTENSIONS TO SKIP
# ============================================================

NON_HTML_EXTENSIONS = {
    # Documents / Data
    ".csv", ".pdf", ".zip", ".xlsx", ".xls", ".doc", ".docx",
    ".ppt", ".pptx", ".txt", ".json", ".xml", ".parquet", ".tsv",
    ".tar", ".gz", ".7z", ".rar", ".bz2",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp", ".tiff",
    # Fonts
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    # Scripts / Styles / Source
    ".js", ".css", ".map", ".scss", ".less", ".ts", ".jsx", ".tsx",
    # Audio / Video
    ".mp4", ".mp3", ".wav", ".avi", ".mov", ".mkv", ".webm", ".ogg", ".flac",
    # Binary / Executable
    ".exe", ".dmg", ".iso", ".bin", ".apk", ".ipa"
}

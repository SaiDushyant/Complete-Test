"""
Element Comparer & Drift Detection Module.
Compares baseline element JSON snapshots against live extracted DOM elements
to identify missing, added, and modified elements across pages and in-DOM views.
"""

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from comparer.comparer_config import (
    BASELINE_ADMIN_BASE_URL,
    BASELINE_DIR,
    BASELINE_URL,
    COMPARISON_REPORT_FILE,
    DEFAULT_VIEWPORT,
    LIVE_ADMIN_BASE_URL,
    LIVE_URL,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    get_viewport_config,
)
from crawler.crawler import extract_viewport_from_filename


def get_canonical_route(url: str, base_url: Optional[str] = None) -> str:
    """
    Extract a canonical, host-agnostic route and query from a URL for baseline vs live comparison.
    If base_url is provided and url starts with base_url, strips base_url prefix.
    Otherwise extracts normalized path and query.
    """
    if not url:
        return ""
    clean = url.split("#")[0].strip()

    if base_url:
        clean_base = base_url.split("#")[0].strip().rstrip("/")
        if clean.startswith(clean_base):
            rel = clean[len(clean_base):]
            if not rel or rel == "/":
                return "/"
            return rel.rstrip("/")

    parsed = urlparse(clean)
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    elif not path:
        path = "/"

    if parsed.query:
        return f"{path}?{parsed.query}"
    return path



class NoiseFilter:
    """
    Handles dynamic noise suppression (timestamps, fluctuating balances,
    subpixel bounding box shifts, volatile session IDs).
    """

    # Ignored attributes when diffing attributes
    DEFAULT_IGNORED_ATTRIBUTES = {
        "class",  # Classes are normalized and compared separately via set-based classes diff
        "style",  # Style tags often contain dynamic coordinates or inline transforms
        "tabindex",
        "aria-hidden",
        "aria-expanded",
        "aria-valuenow",
        "colspan",  # Datatable empty vs populated table column spans
        "valign",
        "d",  # SVG path coordinates for ApexCharts & dynamic price curves
        "clip-path",
        "transform",
        "frameborder",
        "allowfullscreen",
        "data-widget-options",  # Dynamic tradingview widget config containing session uids
        "data-v-",  # Vue scoped CSS IDs
        "data-reactid",
        "data-id",  # Dynamic entity IDs
        "data-row-id",
        "data-user-id",
        "data-account-id",
        "data-order-id",
        "data-user",
        "data-account",
        "data-order",
        "data-ticket",
        "data-pamm",
        "data-target",
        "data-bs-target",
        "data-skeleton-kind",
        "data-theme",
        "data-rendered",
        "data-high",  # Live market tick attributes
        "data-low",
        "data-offer",
        "data-bid",
        "data-price",
        "data-last",
        "data-change",
        "data-uid",
        "data-type",
        "data-live",
        "data-socket",
        # SVG & Chart dynamic coordinate and style attributes
        "x",
        "y",
        "dx",
        "dy",
        "cx",
        "cy",
        "r",
        "rx",
        "ry",
        "points",
        "offset",
        "font-family",
        "text-anchor",
        "dominant-baseline",
        "fill",
        "stroke",
        "stroke-width",
        "stroke-dasharray",
        # Session and CSRF attributes
        "data-session",
        "data-token",
        "data-csrf",
    }

    # Transient animation, market flash, table sort, and state classes to ignore during regression diffs
    VOLATILE_CLASSES = {
        # Animations & loaders
        "fade-in", "fade-out", "animsition-loading", "animsition", "fadeIn", "fadeOut",
        "animated", "show", "collapsing",
        "watchlist-skeleton", "watchlist-initial-loading", "flash-green", "flash-red",
        "redx", "bluex", "greenx", "redx-btn", "bluex-btn", "greenx-btn",
        "loader-overlay", "loader-content", "loader-index", "dashboard-skeleton", "dashboardSkeleton",
        # Directional & color utilities
        "up", "down", "positive", "negative", "green", "red",
        "text-primary", "text-success", "text-warning", "text-danger", "text-info", "text-muted",
        "bg-primary", "bg-success", "bg-warning", "bg-danger", "bg-info", "bg-secondary", "bg-dark", "bg-light", "bg-gray",
        # Dynamic icons in notifications & menus
        "fa", "fa-money-bill", "fa-check", "fa-bell", "fa-user", "fa-wallet", "fa-exchange",
        "bx", "bx-cart", "bx-user", "bx-wallet", "bx-dollar-circle", "bx-trending-up", "bx-trending-down", "bx-check", "bx-x", "bx-bell", "bx-badge",
        # Simplebar scroll container elements
        "simplebar-placeholder", "simplebar-track", "simplebar-horizontal", "simplebar-vertical",
        "simplebar-scrollbar", "simplebar-wrapper", "simplebar-mask", "simplebar-offset",
        "simplebar-content-wrapper", "simplebar-content", "simplebar-height-auto-observer-wrapper",
        "simplebar-height-auto-observer", "simplebar-dummy-scrollbar-size", "simplebar-hide-scrollbar",
        # UI badges and layout utilities
        "avatar-title", "rounded-circle", "font-size-16", "font-size-13", "font-size-14", "font-size-12",
        "avatar-sm", "avatar-xs", "avatar-md", "avatar-lg",
        "me-3", "me-2", "me-1", "ms-3", "ms-2", "ms-1",
        "flex-shrink-0", "flex-grow-1", "d-flex", "mb-1", "mb-0", "mt-1", "mt-0",
        # Trading table & watchlist dynamic state
        "allpos", "equityraw", "edit-container", "c-pointer", "time", "xbalance",
        "curPostionLength", "floatbox", "totalprofit",
        "watchlist-pnl-negative", "watchlist-pnl-positive", "watchlist-day-range",
        "dayHigh", "dayLow", "range-label", "value", "move", "placeorder", "deletewl", "favourite", "openchart",
        "active", "last-active", "selected", "fullwidth", "righthide", "option", "red-option", "change-value-dropdown",
        "pen-sorting-column", "sorting-column", "sorting-identy", "id", "child", "thead-light",
        "odd", "even", "dtr-control", "dataTables_empty", "sorting", "sorting_asc", "sorting_desc", "sorting_1",
        "sidehide", "lightTheme", "darkTheme", "ar", "en",
        "colorBUY", "colorSELL", "ltp", "ltp_0", "ltp_4", "oswap", "pnl", "cancelposition",
        "modify", "modifypartiallot", "element-partiallot", "element-sl", "element-tp",
        "mobsymbol", "mobpartial", "customPadding", "openpositionmobile", "fxPostionsList",
    }

    # Dynamic regex patterns to normalize in text content
    DEFAULT_TEXT_PATTERNS = [
        # Arbitrary multi-unit relative times: "1 Day 0 Hour 56 Minutes ago", "17 Hours 58 Minutes ago", "2 mins ago"
        (r"\b(?:\d+\s+(?:days?|hours?|hrs?|minutes?|mins?|seconds?|secs?)\s*)+ago\b", "[RELATIVE_TIME]"),
        # ISO / Date strings: 2026-09-24, 24/09/2026, Sep 24, 2026, 2026-09-04 05:41:17
        (r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?\b", "[DATE]"),
        (r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?\b", "[DATE]"),
        (r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b", "[DATE]"),
        # Clocks & timestamps: 10:45:23, 10:45 AM, 23:59:59.999
        (r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:\s*(?:AM|PM|am|pm))?\b", "[TIME]"),
        # Email addresses: bttest@mailinator.com, user@test.com
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]"),
        # User account labels in admin headers: "<Username> - <AccountID>" (e.g. Khavyaa - 10056, AnyName - 12345)
        (r"\b[A-Za-z0-9_.-]{2,30}\s*-\s*\d{4,7}\b", "[USER_ACCOUNT_LABEL]"),
        # Automated test run account slugs & dynamic user accounts (e.g. codex_stress_..., test_mam_..., user_master_...)
        (r"\b[A-Za-z0-9_-]+_(?:mam|master|follower|stress|e2e|test|account)[A-Za-z0-9_]*\b", "[ACCOUNT_NAME]"),
        (r"\b(?:codex_|test_|user_|demo_)[A-Za-z0-9_]+\b", "[ACCOUNT_NAME]"),
        # User account name with account number (e.g. Sam 10090, sapna 10031):
        (r"\b[A-Za-z0-9_.-]{2,30}\s+\d{4,7}\b", "[ACCOUNT_NAME_WITH_ID]"),
        # Generic role-based user account identifiers (e.g. master, follower1, tester, client2, manager)
        (r"\b(?:master|follower|tester|client|manager|trader)\d*\b", "[GENERIC_USER_ROLE]"),
        # Transaction & deposit request notifications: Deposit Request for $200.00, Withdraw Request for $1.00
        (r"\b(?:Deposit|Withdraw|Withdrawal|Transfer|Trade|Order)\s+Request\s+for\s+[$€£¥₹]?\s*[\d,.]+\b", "[TRANSACTION_REQUEST]"),
        # Account balance dropdown options (e.g. 10009 | $ 13,559.04, 10010 | $ 10000.00)
        (r"\b\d{4,7}\s*\|\s*[$€£¥₹]?\s*[\d,.]+\b", "[ACCOUNT_BALANCE_OPTION]"),
        # Dynamic Blob URLs (e.g. blob:https://stage.xtremenext.com/52fd1537-2f4c-...)
        (r"blob:https?://[^\s\"']+", "[BLOB_URL]"),
        # UUID strings (e.g. 52fd1537-2f4c-49b6-8b2d-491ed6a8c91d)
        (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "[UUID]"),
        # High/Low ticker market stats (e.g. H: 1.32559, L: 1.32110, H:, L:)
        (r"\b[HLhl]:(?:\s*[-+$\d,.]*)?", "[TICKER_HL]"),
        # Order directions & order actions in trading positions (e.g. BUY / SELL / Sell TP / Sell SL)
        (r"\b(?:BUY|SELL|Buy|Sell|Sell TP|Sell SL|Buy TP|Buy SL|Sell Below|Buy Above|Take Profit|Stop Loss)\b", "[ORDER_SIDE]"),
        # Symbol and pair tags (e.g. C:AUDCHF, C:USDJPY, XAUUSD, EURUSD)
        (r"\b[A-Z]{1,2}:[A-Z]{3,6}\b", "[SYMBOL_TAG]"),
        # Ticker quotes & prices: EURUSD $ 1.13823, XAUUSD 4281.65, EUR/USD, etc.
        (r"\b(?:EURUSD|GBPUSD|USDJPY|USDCHF|AUDUSD|NZDUSD|USDCAD|XAUUSD|BTCUSD|ETHUSD|[A-Z]{3,6}/[A-Z]{3,6})\s*[$€£¥₹]?\s*[+-]?[\d,]+(?:\.\d+)?\b", "[TICKER]"),
        # Dynamic position and pending order counters (e.g. Positions (5), Pending Orders (0)):
        (r"\b(?:Positions|Pending Orders|Open Positions|Closed Positions)\s*\(\d+\)", "[POSITIONS_COUNT]"),
        # Account metrics & trading headers with numbers: Balance: 13,500.00, PNL (24H) 4.96, Margin Level: 11253.94%
        (r"\b(?:Balance|Equity|Margin|Free Margin|Margin Level|Leverage|Total PNL|PNL|Profit|Positions|Request Count|Volume|Orders?|Trades?|Lots?)\s*[:(]?\s*[-+$€£¥₹]?\s*[\d,]+(?:\.\d+)?%?\)?", "[METRIC]"),
        # Empty dash table entries: "--"
        (r"(?<!\w)--(?!\w)", "[NO_VALUE]"),
        # Currency prices: $ 1.13823, $4281.65, €12.50, £100, ₹500, 100 USD, 50.5 USDT
        (r"[$€£¥₹]\s*[+-]?[\d,]+(?:\.\d+)?", "[PRICE]"),
        (r"[+-]?[\d,]+(?:\.\d+)?\s*(?:USD|EUR|GBP|JPY|AUD|CAD|CHF|USDT)\b", "[PRICE]"),
        # Percentages (both decimal and integer, positive or negative): 18.7%, 19.69%, -0.44%, +4.96%, 100%
        (r"[+-]?\d+(?:\.\d+)?%", "[PERCENT]"),
        # Formatted numbers with commas (e.g. 2,904, 10,550, 1,000,000, 1,234.56)
        (r"[+-]?\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", "[NUMBER]"),
        # Floating point numbers / decimals (1 or more decimal places): 1.13823, -0.44, +4.96, 0.08, 3097.10
        (r"[+-]?\b\d+\.\d+\b", "[FLOAT]"),
        # Datatable pagination text: "Showing 1 to 3 of 3 entries"
        (r"\bShowing\s+\d+\s+to\s+\d+\s+of\s+\d+\s+entries\b", "[PAGINATION_INFO]"),
        # Dynamic user/order/ticket IDs and tokens: user_BVT8QQ2W7C, order_12345, LWR8AUE0TS
        (r"\b(?:user|order|ticket|id|account|req)[_#-][A-Za-z0-9_]+\b", "[DYNAMIC_ID]"),
        # Alphanumeric hashes (must contain both letters and digits, 8-20 chars)
        (r"(?<!\[)\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{8,20}\b(?!\])", "[USER_HASH]"),
        # Standalone integers in table cells / stat counters (e.g. 123, 127, 4, 3, 10009, 10556)
        (r"\b\d+\b", "[INT]"),
    ]

    TRANSIENT_LOADER_PATTERNS = {
        "loader-overlay", "loader-content", "loader-index",
        "watchlist-skeleton", "dashboard-skeleton",
        "dashboardSkeleton", "animsition-loading"
    }

    DYNAMIC_TRADING_CLASSES = {
        "openpositionmobile", "fxPostionsList", "mobsymbol", "mobpartial",
        "cancelposition", "element-partiallot", "element-sl", "element-tp",
        "position-action-cell", "modify", "modifypartiallot", "chart-history-pnl-row",
        "pnlTxt", "empty-pending-row", "empty-position-row", "ltp", "ltp_0", "ltp_4",
        "oswap", "pnl", "colorBUY", "colorSELL", "totalprofitvalue", "customPadding"
    }

    def is_transient_loader(self, elem: Dict[str, Any]) -> bool:
        classes = elem.get("classes") or ""
        eid = elem.get("id") or ""
        loc = elem.get("locator") or ""
        for ind in self.TRANSIENT_LOADER_PATTERNS:
            if ind in classes or ind in loc or ind == eid:
                return True
        return False

    def is_dynamic_trading_element(self, elem: Dict[str, Any]) -> bool:
        classes = elem.get("classes") or ""
        loc = elem.get("locator") or ""
        for dtc in self.DYNAMIC_TRADING_CLASSES:
            if dtc in classes or dtc in loc:
                return True
        return False

    def __init__(
        self,
        enabled: bool = True,
        ignored_attributes: Optional[Set[str]] = None,
        text_patterns: Optional[List[Tuple[str, str]]] = None,
        ignore_bounding_box: bool = True,
        baseline_base_url: Optional[str] = None,
        live_base_url: Optional[str] = None,
        baseline_urls: Optional[List[str]] = None,
        live_urls: Optional[List[str]] = None,
    ):
        self.enabled = enabled
        self.ignored_attributes = ignored_attributes or self.DEFAULT_IGNORED_ATTRIBUTES
        self.text_patterns = text_patterns or self.DEFAULT_TEXT_PATTERNS
        self.ignore_bounding_box = ignore_bounding_box

        # Domain and URL normalization for baseline vs live comparison
        self.baseline_urls = []
        if baseline_urls:
            self.baseline_urls.extend([u.rstrip("/") for u in baseline_urls if u])
        if baseline_base_url and baseline_base_url.rstrip("/") not in self.baseline_urls:
            self.baseline_urls.append(baseline_base_url.rstrip("/"))

        self.live_urls = []
        if live_urls:
            self.live_urls.extend([u.rstrip("/") for u in live_urls if u])
        if live_base_url and live_base_url.rstrip("/") not in self.live_urls:
            self.live_urls.append(live_base_url.rstrip("/"))

        self.baseline_domains = [urlparse(u).netloc for u in self.baseline_urls if urlparse(u).netloc]
        self.live_domains = [urlparse(u).netloc for u in self.live_urls if urlparse(u).netloc]

    def normalize_text(self, text: Optional[str], source_env: Optional[str] = None) -> str:
        """Strip, collapse whitespace, and mask dynamic noise patterns."""
        if not text or not isinstance(text, str):
            return ""

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", text).strip()

        if not self.enabled:
            return cleaned

        # Normalize domain/URL references if live URL differs from baseline
        if self.baseline_urls != self.live_urls:
            if source_env == "baseline":
                for b_url in self.baseline_urls:
                    cleaned = cleaned.replace(b_url, "[BASE_URL]")
                for b_dom in self.baseline_domains:
                    if b_dom and b_dom not in self.live_domains:
                        cleaned = cleaned.replace(b_dom, "[BASE_DOMAIN]")
            elif source_env == "live":
                for l_url in self.live_urls:
                    cleaned = cleaned.replace(l_url, "[BASE_URL]")
                for l_dom in self.live_domains:
                    if l_dom and l_dom not in self.baseline_domains:
                        cleaned = cleaned.replace(l_dom, "[BASE_DOMAIN]")

        # Mask dynamic patterns
        for pattern, replacement in self.text_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        return cleaned

    def normalize_attributes(self, attrs: Optional[Dict[str, Any]], source_env: Optional[str] = None) -> Dict[str, Any]:
        """Filter out volatile attributes and normalize dynamic values."""
        if not attrs or not isinstance(attrs, dict):
            return {}

        filtered = {}
        for k, v in attrs.items():
            k_lower = k.lower()

            # Skip ignored attributes
            if self.enabled and any(k_lower.startswith(ign) or k_lower == ign for ign in self.ignored_attributes):
                continue

            # Normalize dynamic CSRF token values in inputs
            if self.enabled and k_lower == "value" and attrs.get("name") in ("admin_login_csrf", "csrf_token", "_csrf", "_token"):
                filtered[k] = "[CSRF_TOKEN]"
                continue

            # Normalize dynamic widget IDs and iframe URLs in attributes
            if self.enabled and isinstance(v, str):
                if v.startswith("blob:"):
                    v_norm = "[BLOB_URL]"
                elif re.match(r"^tradingview_[0-9a-zA-Z_]+$", v):
                    v_norm = "tradingview-dynamic-id"
                elif re.match(r"^gridRect(?:Marker)?Mask[a-z0-9]+$", v):
                    v_norm = "gridRectMask-dynamic-id"
                elif re.match(r"^Svgjs[a-zA-Z0-9]+$", v):
                    v_norm = "svgjs-dynamic-id"
                elif re.match(r"^apexcharts[a-z0-9]+$", v):
                    v_norm = "apexcharts-dynamic-id"
                elif "tradingview.com" in v:
                    v_norm = "[TRADINGVIEW_SRC]"
                else:
                    if self.baseline_urls != self.live_urls:
                        if source_env == "baseline":
                            for b_url in self.baseline_urls:
                                v = v.replace(b_url, "[BASE_URL]")
                            for b_dom in self.baseline_domains:
                                if b_dom and b_dom not in self.live_domains:
                                    v = v.replace(b_dom, "[BASE_DOMAIN]")
                        elif source_env == "live":
                            for l_url in self.live_urls:
                                v = v.replace(l_url, "[BASE_URL]")
                            for l_dom in self.live_domains:
                                if l_dom and l_dom not in self.baseline_domains:
                                    v = v.replace(l_dom, "[BASE_DOMAIN]")

                    v_norm = re.sub(r"\bapexcharts[a-z0-9]{6,12}\b", "apexcharts-id", v)
                    if k_lower in ("id", "name", "for"):
                        v_norm = self.normalize_id(v_norm) or v_norm
                    v_norm = self.normalize_text(v_norm, source_env=source_env)
                filtered[k] = v_norm
            else:
                filtered[k] = v

        return filtered

    def normalize_classes(self, classes: Optional[str]) -> Set[str]:
        """Normalize class string to a sorted set of class names with noise masking."""
        if not classes or not isinstance(classes, str):
            return set()
        
        normalized = []
        for c in classes.strip().split():
            # Skip volatile animation and price flash classes
            if self.enabled and c in self.VOLATILE_CLASSES:
                continue
            # Skip dynamic drag element indexes
            if self.enabled and re.match(r"^dragElement\d+$", c):
                continue
            # Mask dynamic apexcharts canvas class hashes (e.g. apexchartscu1wp6vj)
            if self.enabled and re.match(r"^apexcharts[a-z0-9]{6,12}$", c):
                c = "apexcharts-dynamic-canvas-id"
            # Mask dynamic user-specific classes (e.g. user_margin_level_BVT8QQ2W7C, user_LWR8AUE0TS, etc.)
            elif self.enabled and re.match(r"^user_(?:margin_level_|total_pnl_)?[A-Za-z0-9]{6,16}$", c):
                c = "user-dynamic-hash-class"
            normalized.append(c)
            
        return set(normalized)

    def normalize_id(self, id_str: Optional[str]) -> Optional[str]:
        """Normalize volatile/dynamic element IDs (e.g. tradingview, apexcharts, select2, svgjs, gridRectMask)."""
        if not id_str or not isinstance(id_str, str):
            return None
        if not self.enabled:
            return id_str.strip()
        cleaned = id_str.strip()
        if re.match(r"^tradingview_[0-9a-zA-Z_]+$", cleaned):
            return "tradingview-dynamic-id"
        if re.match(r"^gridRect(?:Marker)?Mask[a-z0-9]+$", cleaned):
            return "gridRectMask-dynamic-id"
        if re.match(r"^Svgjs[a-zA-Z0-9]+$", cleaned):
            return "svgjs-dynamic-id"
        if re.match(r"^apexcharts[a-z0-9]+$", cleaned):
            return "apexcharts-dynamic-id"
        if re.match(r"^chart_[0-9a-zA-Z_]+$", cleaned):
            return "chart-dynamic-id"
        if re.match(r"^select2-[a-z0-9_-]+$", cleaned):
            return "select2-dynamic-id"
        return cleaned

    def normalize_locator(self, loc: Optional[str]) -> Optional[str]:
        """Normalize volatile IDs or classes inside CSS locators."""
        if not loc or not isinstance(loc, str):
            return None
        if not self.enabled:
            return loc.strip()
        cleaned = loc.strip()
        cleaned = re.sub(r"#tradingview_[0-9a-zA-Z_]+", "#tradingview-dynamic-id", cleaned)
        cleaned = re.sub(r"#gridRect(?:Marker)?Mask[a-z0-9]+", "#gridRectMask-dynamic-id", cleaned)
        cleaned = re.sub(r"#Svgjs[a-zA-Z0-9]+", "#svgjs-dynamic-id", cleaned)
        cleaned = re.sub(r"#apexcharts[a-z0-9]+", "#apexcharts-dynamic-id", cleaned)
        cleaned = re.sub(r"#chart_[0-9a-zA-Z_]+", "#chart-dynamic-id", cleaned)
        cleaned = re.sub(r"#select2-[a-z0-9_-]+", "#select2-dynamic-id", cleaned)
        
        # Strip volatile animation/flash/state classes from selector
        for vc in self.VOLATILE_CLASSES:
            cleaned = re.sub(rf"\.{re.escape(vc)}\b", "", cleaned)
            
        return cleaned


class ElementComparer:
    """
    Core comparer engine that matches baseline elements against live DOM elements
    and computes structured regression / drift diffs.
    """

    def __init__(
        self,
        baseline_dir: Path = BASELINE_DIR,
        noise_filter: Optional[NoiseFilter] = None,
        baseline_base_url: Optional[str] = None,
        live_base_url: Optional[str] = None,
    ):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_base_url = baseline_base_url or BASELINE_URL
        self.live_base_url = live_base_url or LIVE_URL
        self.noise_filter = noise_filter or NoiseFilter(
            enabled=True,
            baseline_base_url=self.baseline_base_url,
            live_base_url=self.live_base_url,
        )

    def load_baseline_snapshots(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all baseline element snapshot JSON files from baseline directory.
        Excludes report files (crawl_report.json, comparison_report.json).
        Returns a dict keyed by unique viewport-aware view identifier: (url, view_name, viewport).
        """
        snapshots = {}
        if not self.baseline_dir.exists():
            return snapshots

        for json_file in sorted(self.baseline_dir.glob("*.json")):
            # Ignore report summaries
            if json_file.name in ("crawl_report.json", "comparison_report.json", "comparison_report_admin.json"):
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Ensure valid element snapshot format
                if "page" in data and "elements" in data:
                    page_info = data.get("page", {})
                    url = page_info.get("url", "")
                    view_name = page_info.get("view_name") or ""
                    viewport = page_info.get("viewport") or extract_viewport_from_filename(json_file.name) or ""
                    key = self._get_snapshot_key(url, view_name, viewport)

                    snapshots[key] = {
                        "file_name": json_file.name,
                        "file_path": str(json_file),
                        "page": page_info,
                        "elements": data.get("elements", []),
                        "statistics": data.get("statistics", {}),
                    }
            except Exception as e:
                print(f"Warning: Failed to load baseline snapshot '{json_file.name}': {e}")

        return snapshots

    @staticmethod
    def _get_snapshot_key(url: str, view_name: Optional[str] = None, viewport: Optional[str] = None) -> str:
        """Generate a consistent, viewport-aware snapshot lookup key."""
        clean_url = (url or "").split("#")[0].rstrip("/")
        clean_view = (view_name or "").strip().lower()
        clean_viewport = (viewport or "").strip().lower()

        parts = [clean_url]
        if clean_view:
            parts.append(f"view::{clean_view}")
        if clean_viewport:
            parts.append(f"viewport::{clean_viewport}")

        return "::".join(parts)

    @staticmethod
    def _get_canonical_key(
        url: str,
        view_name: Optional[str] = None,
        viewport: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> str:
        """Generate a consistent, host-agnostic canonical lookup key for matching across environments."""
        route = get_canonical_route(url, base_url)
        clean_view = (view_name or "").strip().lower()
        clean_viewport = (viewport or "").strip().lower()

        parts = [route]
        if clean_view:
            parts.append(f"view::{clean_view}")
        if clean_viewport:
            parts.append(f"viewport::{clean_viewport}")

        return "::".join(parts)


    def annotate_table_context(self, elements: List[Dict[str, Any]]) -> None:
        """Annotate elements that are inside table cells so table data text can be normalized."""
        in_td = False
        for el in elements:
            tag = (el.get("tag") or "").lower()
            if tag in ("td", "th"):
                in_td = True
                el["in_table_cell"] = True
            elif tag in ("tr", "table", "tbody", "thead"):
                in_td = False
                el["in_table_cell"] = False
            else:
                el["in_table_cell"] = in_td or bool(el.get("in_table_cell"))

    def match_and_diff_elements(
        self,
        baseline_elements: List[Dict[str, Any]],
        live_elements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Compare baseline elements against live elements using an indexed O(N) multi-tier matching strategy:
          Tier 1: Unique locator (`is_unique == True` & matching non-bare `locator` & matching `tag`)
          Tier 2: Unique ID match (`id` present and tags match, ordered FIFO to handle duplicate IDs safely)
          Tier 3: Semantic attribute signature (`name`, `data-testid`, `data-page`, `data-nav`, `aria-label`, etc.)
          Tier 4: Specific locator path & tag match (excluding bare tag selectors)
          Tier 5: Fallback matching (5a: Tag + Classes + Text, 5b: Tag + Text, 5c: Tag + Classes)
          Tier 6: Remaining bare elements with same Tag matched in document order
        """
        from collections import deque

        self.annotate_table_context(baseline_elements)
        self.annotate_table_context(live_elements)

        matched_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        matched_b_indices: Set[int] = set()
        matched_l_indices: Set[int] = set()

        # Build fast lookup indexes over live elements
        live_unique_map: Dict[Tuple[str, str], deque] = defaultdict(deque)
        live_id_map: Dict[Tuple[str, str], deque] = defaultdict(deque)
        live_semantic_map: Dict[Tuple[str, str, str], deque] = defaultdict(deque)
        live_locator_map: Dict[Tuple[str, str], deque] = defaultdict(deque)
        live_tc_map: Dict[Tuple[str, frozenset, str], deque] = defaultdict(deque)
        live_t_classes_map: Dict[Tuple[str, frozenset], deque] = defaultdict(deque)
        live_t_text_map: Dict[Tuple[str, str], deque] = defaultdict(deque)
        live_tag_map: Dict[str, deque] = defaultdict(deque)

        for l_idx, l_elem in enumerate(live_elements):
            l_tag = (l_elem.get("tag") or "").lower()
            l_loc = self.noise_filter.normalize_locator(l_elem.get("locator"))
            l_id = self.noise_filter.normalize_id(l_elem.get("id"))
            l_unique = l_elem.get("is_unique", False)
            l_classes = frozenset(self.noise_filter.normalize_classes(l_elem.get("classes")))
            l_text = self.noise_filter.normalize_text(l_elem.get("text"))
            l_attrs = l_elem.get("attributes") or {}

            if l_unique and l_loc and l_loc.lower() != l_tag:
                live_unique_map[(l_tag, l_loc)].append(l_idx)

            if l_id:
                live_id_map[(l_tag, l_id)].append(l_idx)

            for key in ("data-testid", "name", "data-nav", "data-page", "data-view", "data-offer", "data-bid", "data-symbol", "aria-label", "data-action", "data-bs-target", "data-target"):
                val = l_attrs.get(key)
                if val:
                    live_semantic_map[(l_tag, key, str(val))].append(l_idx)

            if l_loc and l_loc.lower() != l_tag:
                live_locator_map[(l_tag, l_loc)].append(l_idx)

            if l_text and l_classes:
                live_tc_map[(l_tag, l_classes, l_text)].append(l_idx)
            elif l_text and not l_classes:
                live_t_text_map[(l_tag, l_text)].append(l_idx)

            if l_classes:
                live_t_classes_map[(l_tag, l_classes)].append(l_idx)

            live_tag_map[l_tag].append(l_idx)

        def pair(b_idx: int, l_idx: int):
            matched_b_indices.add(b_idx)
            matched_l_indices.add(l_idx)
            matched_pairs.append((baseline_elements[b_idx], live_elements[l_idx]))

        # PASS 1: Unique Locators (must not be bare tags)
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_loc = self.noise_filter.normalize_locator(b_elem.get("locator"))
            b_unique = b_elem.get("is_unique", False)
            b_tag = (b_elem.get("tag") or "").lower()
            if b_unique and b_loc and b_loc.lower() != b_tag:
                dq = live_unique_map.get((b_tag, b_loc))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # PASS 2: ID Match (using deque in document order to prevent collisions)
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_id = self.noise_filter.normalize_id(b_elem.get("id"))
            b_tag = (b_elem.get("tag") or "").lower()
            if b_id:
                dq = live_id_map.get((b_tag, b_id))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # PASS 3: Semantic Attributes Match
        SEMANTIC_KEYS = ("data-testid", "name", "data-nav", "data-page", "data-view", "data-offer", "data-bid", "data-symbol", "aria-label", "data-action", "data-bs-target", "data-target")
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            b_attrs = b_elem.get("attributes") or {}
            for key in SEMANTIC_KEYS:
                val = b_attrs.get(key)
                if val:
                    sem_key = (b_tag, key, str(val))
                    dq = live_semantic_map.get(sem_key)
                    if dq:
                        while dq and dq[0] in matched_l_indices:
                            dq.popleft()
                        if dq:
                            pair(b_idx, dq.popleft())
                            break

        # PASS 4: Specific Locator path & Tag Match (EXCLUDING bare tags to prevent domino cascades)
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            b_loc = self.noise_filter.normalize_locator(b_elem.get("locator"))
            if b_loc and b_loc.lower() != b_tag:
                dq = live_locator_map.get((b_tag, b_loc))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # PASS 5: Normalized Classes & Text Fallback
        # 5a. Tag + Classes + Text
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            b_text = self.noise_filter.normalize_text(b_elem.get("text"))
            b_classes = frozenset(self.noise_filter.normalize_classes(b_elem.get("classes")))

            if b_text and b_classes:
                dq = live_tc_map.get((b_tag, b_classes, b_text))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # 5b. Tag + Text
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            b_text = self.noise_filter.normalize_text(b_elem.get("text"))
            if b_text:
                dq = live_t_text_map.get((b_tag, b_text))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # 5c. Tag + Classes
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            b_classes = frozenset(self.noise_filter.normalize_classes(b_elem.get("classes")))
            if b_classes:
                dq = live_t_classes_map.get((b_tag, b_classes))
                if dq:
                    while dq and dq[0] in matched_l_indices:
                        dq.popleft()
                    if dq:
                        pair(b_idx, dq.popleft())

        # PASS 6: Remaining bare elements with same tag in document order
        for b_idx, b_elem in enumerate(baseline_elements):
            if b_idx in matched_b_indices:
                continue
            b_tag = (b_elem.get("tag") or "").lower()
            dq = live_tag_map.get(b_tag)
            if dq:
                while dq and dq[0] in matched_l_indices:
                    dq.popleft()
                if dq:
                    pair(b_idx, dq.popleft())

        # Remaining unmatched baseline and live elements (excluding transient loaders & dynamic trading rows)
        unmatched_baseline = [
            b_elem for b_i, b_elem in enumerate(baseline_elements)
            if b_i not in matched_b_indices
            and not self.noise_filter.is_transient_loader(b_elem)
            and not self.noise_filter.is_dynamic_trading_element(b_elem)
        ]
        unmatched_live = [
            l_elem for l_i, l_elem in enumerate(live_elements)
            if l_i not in matched_l_indices
            and not self.noise_filter.is_transient_loader(l_elem)
            and not self.noise_filter.is_dynamic_trading_element(l_elem)
        ]

        # -------------------------------------------------------------
        # COMPUTE DIFFS FOR MATCHED ELEMENTS
        # -------------------------------------------------------------
        matched_unchanged = []
        modified_elements = []

        for b_elem, l_elem in matched_pairs:
            diffs = self._diff_single_element(b_elem, l_elem)
            if diffs:
                modified_elements.append({
                    "locator": l_elem.get("locator") or b_elem.get("locator"),
                    "tag": l_elem.get("tag") or b_elem.get("tag"),
                    "id": l_elem.get("id") or b_elem.get("id"),
                    "diffs": diffs,
                    "baseline": {
                        "text": b_elem.get("text"),
                        "visible": b_elem.get("visible"),
                        "classes": b_elem.get("classes"),
                        "attributes": b_elem.get("attributes"),
                    },
                    "live": {
                        "text": l_elem.get("text"),
                        "visible": l_elem.get("visible"),
                        "classes": l_elem.get("classes"),
                        "attributes": l_elem.get("attributes"),
                    },
                })
            else:
                matched_unchanged.append({
                    "locator": l_elem.get("locator") or b_elem.get("locator"),
                    "tag": l_elem.get("tag") or b_elem.get("tag"),
                })

        # Elements in baseline not found in live DOM -> Missing
        missing_elements = [
            {
                "locator": elem.get("locator"),
                "tag": elem.get("tag"),
                "id": elem.get("id"),
                "classes": elem.get("classes"),
                "text": elem.get("text"),
                "visible": elem.get("visible"),
                "attributes": elem.get("attributes"),
            }
            for elem in unmatched_baseline
        ]

        # Elements in live DOM not found in baseline -> Added
        added_elements = [
            {
                "locator": elem.get("locator"),
                "tag": elem.get("tag"),
                "id": elem.get("id"),
                "classes": elem.get("classes"),
                "text": elem.get("text"),
                "visible": elem.get("visible"),
                "attributes": elem.get("attributes"),
            }
            for elem in unmatched_live
        ]

        return {
            "matched_unchanged_count": len(matched_unchanged),
            "modified_count": len(modified_elements),
            "missing_count": len(missing_elements),
            "added_count": len(added_elements),
            "matched_unchanged": matched_unchanged,
            "modified_elements": modified_elements,
            "missing_elements": missing_elements,
            "added_elements": added_elements,
        }

    def _diff_single_element(
        self,
        b_elem: Dict[str, Any],
        l_elem: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compute specific attribute/state diffs between two matched elements."""
        diffs = {}

        # 1. Text diff (normalized for noise)
        b_direct = self.noise_filter.normalize_text(b_elem.get("direct_text"), source_env="baseline")
        l_direct = self.noise_filter.normalize_text(l_elem.get("direct_text"), source_env="live")
        b_text = self.noise_filter.normalize_text(b_elem.get("text"), source_env="baseline")
        l_text = self.noise_filter.normalize_text(l_elem.get("text"), source_env="live")

        # Dynamic table data cell handling: If both elements are table cells or within table cells,
        # and neither is a UI action control, treat non-empty record text as dynamic data
        is_table_cell = (
            b_elem.get("tag") in ("td", "th")
            or b_elem.get("in_table_cell")
            or l_elem.get("tag") in ("td", "th")
            or l_elem.get("in_table_cell")
        )
        UI_ACTION_KEYWORDS = {
            "edit", "delete", "view", "actions", "action", "active", "inactive",
            "status", "pending", "success", "failed", "approved", "rejected",
            "enabled", "disabled", "open", "close", "closed", "buy", "sell", "deposit", "withdraw", "follow"
        }
        if is_table_cell and b_text and l_text:
            b_norm_lower = b_text.strip().lower()
            l_norm_lower = l_text.strip().lower()
            if (b_norm_lower not in UI_ACTION_KEYWORDS) and (l_norm_lower not in UI_ACTION_KEYWORDS):
                b_text = "[TABLE_DATA_CELL]"
                l_text = "[TABLE_DATA_CELL]"
                b_direct = "[TABLE_DATA_CELL]"
                l_direct = "[TABLE_DATA_CELL]"

        # Position counter normalization (curPostionLength / position-text e.g. "" vs "Positions (5)")
        b_cls = b_elem.get("classes") or ""
        l_cls = l_elem.get("classes") or ""
        if "curPostionLength" in b_cls or "curPostionLength" in l_cls or "position-text" in b_cls or "position-text" in l_cls:
            b_text = "[POSITIONS_COUNT]"
            l_text = "[POSITIONS_COUNT]"
            b_direct = "[POSITIONS_COUNT]"
            l_direct = "[POSITIONS_COUNT]"

        # ApexCharts & SVG chart data text and dynamic coordinates
        b_id = b_elem.get("id") or ""
        l_id = l_elem.get("id") or ""
        is_svg_or_chart = (
            b_elem.get("tag") in ("svg", "path", "g", "text", "tspan", "rect", "circle", "line")
            or l_elem.get("tag") in ("svg", "path", "g", "text", "tspan", "rect", "circle", "line")
            or b_id.startswith("Svgjs") or l_id.startswith("Svgjs")
            or "apexcharts" in b_cls or "apexcharts" in l_cls
        )
        if is_svg_or_chart and b_text != l_text:
            b_text = "[CHART_DATA]"
            l_text = "[CHART_DATA]"
            b_direct = "[CHART_DATA]"
            l_direct = "[CHART_DATA]"

        # For container elements (with children), compare direct text to prevent cascading child ticker diffs
        is_container = (b_elem.get("is_leaf") is False) or (l_elem.get("is_leaf") is False)
        if is_container and (b_direct or l_direct):
            if b_direct != l_direct:
                diffs["text"] = {
                    "baseline": b_elem.get("direct_text") or b_elem.get("text"),
                    "live": l_elem.get("direct_text") or l_elem.get("text"),
                    "normalized_baseline": b_direct,
                    "normalized_live": l_direct,
                }
        elif not is_container:
            if b_text != l_text:
                diffs["text"] = {
                    "baseline": b_elem.get("text"),
                    "live": l_elem.get("text"),
                    "normalized_baseline": b_text,
                    "normalized_live": l_text,
                }

        # 2. Visibility diff
        b_vis = bool(b_elem.get("visible", False))
        l_vis = bool(l_elem.get("visible", False))
        if b_vis != l_vis:
            # Suppress body visibility diff when page has animsition loading transition
            if (b_elem.get("tag") == "body" or l_elem.get("tag") == "body") and (
                "animsition" in b_cls or "animsition" in l_cls or "page-register" in b_cls or "page-register" in l_cls
            ):
                pass
            elif is_svg_or_chart and (b_elem.get("tag") in ("clippath", "mask", "g", "rect", "path", "tspan", "text")):
                pass
            else:
                diffs["visible"] = {"baseline": b_vis, "live": l_vis}

        # 3. Classes diff (set comparison)
        b_classes = self.noise_filter.normalize_classes(b_elem.get("classes"))
        l_classes = self.noise_filter.normalize_classes(l_elem.get("classes"))
        if b_classes != l_classes:
            added_cls = sorted(list(l_classes - b_classes))
            removed_cls = sorted(list(b_classes - l_classes))
            diffs["classes"] = {
                "added": added_cls,
                "removed": removed_cls,
                "baseline": b_elem.get("classes"),
                "live": l_elem.get("classes"),
            }

        # 4. Attributes diff
        b_attrs = self.noise_filter.normalize_attributes(b_elem.get("attributes"), source_env="baseline")
        l_attrs = self.noise_filter.normalize_attributes(l_elem.get("attributes"), source_env="live")

        all_keys = set(b_attrs.keys()) | set(l_attrs.keys())
        attr_changes = {}
        for key in sorted(all_keys):
            b_val = b_attrs.get(key)
            l_val = l_attrs.get(key)
            if b_val != l_val:
                attr_changes[key] = {"baseline": b_val, "live": l_val}

        if attr_changes:
            diffs["attributes"] = attr_changes

        # 5. Role & ARIA labels
        b_role = b_elem.get("role")
        l_role = l_elem.get("role")
        if b_role != l_role:
            roles = {b_role, l_role}
            # Ignore dynamic datatable role="row" or bootstrap modal role="document" injection
            if not (roles in [{None, "row"}, {None, "document"}, {"", "row"}, {"", "document"}]):
                diffs["role"] = {"baseline": b_role, "live": l_role}

        b_aria = b_elem.get("aria_label")
        l_aria = l_elem.get("aria_label")
        if b_aria != l_aria:
            diffs["aria_label"] = {"baseline": b_aria, "live": l_aria}

        return diffs

    def compare_all(
        self,
        baseline_snapshots: Dict[str, Dict[str, Any]],
        live_snapshots: Dict[str, Dict[str, Any]],
        baseline_base_url: Optional[str] = None,
        live_base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compare all baseline snapshot views against live snapshot views.
        Supports cross-environment URL matching (e.g. baseline vs live on different hosts).
        Returns a complete comparison report structure.
        """
        b_base = baseline_base_url or self.baseline_base_url
        l_base = live_base_url or self.live_base_url

        # Ensure noise filter has baseline and live URLs for domain normalization
        if b_base and b_base.rstrip("/") not in self.noise_filter.baseline_urls:
            self.noise_filter.baseline_urls.append(b_base.rstrip("/"))
            b_dom = urlparse(b_base).netloc
            if b_dom and b_dom not in self.noise_filter.baseline_domains:
                self.noise_filter.baseline_domains.append(b_dom)
        if l_base and l_base.rstrip("/") not in self.noise_filter.live_urls:
            self.noise_filter.live_urls.append(l_base.rstrip("/"))
            l_dom = urlparse(l_base).netloc
            if l_dom and l_dom not in self.noise_filter.live_domains:
                self.noise_filter.live_domains.append(l_dom)

        # 1. Match views: First direct key matching, then canonical route matching
        matched_views = []       # List of (key, baseline_snap, live_snap)
        unmatched_baseline = {}  # b_key -> b_snap
        unmatched_live = {}      # l_key -> l_snap

        # Direct key matching pass
        for b_key, b_snap in baseline_snapshots.items():
            if b_key in live_snapshots:
                matched_views.append((b_key, b_snap, live_snapshots[b_key]))
            else:
                unmatched_baseline[b_key] = b_snap

        for l_key, l_snap in live_snapshots.items():
            if l_key not in baseline_snapshots:
                unmatched_live[l_key] = l_snap

        # Canonical route matching pass for remaining views across different hosts/domains
        if unmatched_baseline and unmatched_live:
            live_by_canonical = {}
            for l_key, l_snap in list(unmatched_live.items()):
                can_key = self._get_canonical_key(
                    url=l_snap.get("page", {}).get("url", ""),
                    view_name=l_snap.get("page", {}).get("view_name"),
                    viewport=l_snap.get("page", {}).get("viewport"),
                    base_url=l_base,
                )
                live_by_canonical[can_key] = (l_key, l_snap)

            for b_key, b_snap in list(unmatched_baseline.items()):
                b_can_key = self._get_canonical_key(
                    url=b_snap.get("page", {}).get("url", ""),
                    view_name=b_snap.get("page", {}).get("view_name"),
                    viewport=b_snap.get("page", {}).get("viewport"),
                    base_url=b_base,
                )
                if b_can_key in live_by_canonical:
                    l_key, l_snap = live_by_canonical.pop(b_can_key)
                    del unmatched_baseline[b_key]
                    del unmatched_live[l_key]
                    matched_views.append((b_key, b_snap, l_snap))

        # Add remaining missing baseline views
        for b_key, b_snap in unmatched_baseline.items():
            matched_views.append((b_key, b_snap, None))

        # Add remaining new live views
        for l_key, l_snap in unmatched_live.items():
            matched_views.append((l_key, None, l_snap))

        # Sort views consistently
        matched_views.sort(key=lambda item: item[0])

        pages_report = []
        total_baseline_elements = 0
        total_live_elements = 0
        total_matched_unchanged = 0
        total_modified = 0
        total_missing = 0
        total_added = 0

        for key, baseline_snap, live_snap in matched_views:
            viewport = (
                (live_snap and live_snap["page"].get("viewport"))
                or (baseline_snap and baseline_snap["page"].get("viewport"))
                or ""
            )
            viewport_size = (
                (live_snap and live_snap["page"].get("viewport_size"))
                or (baseline_snap and baseline_snap["page"].get("viewport_size"))
                or (get_viewport_config(viewport) if viewport in VIEWPORTS else None)
            )

            if baseline_snap and live_snap:
                # View exists in both -> Run element diff
                b_elems = baseline_snap.get("elements", [])
                l_elems = live_snap.get("elements", [])
                diff_result = self.match_and_diff_elements(b_elems, l_elems)

                b_count = len(b_elems)
                l_count = len(l_elems)
                total_baseline_elements += b_count
                total_live_elements += l_count
                total_matched_unchanged += diff_result["matched_unchanged_count"]
                total_modified += diff_result["modified_count"]
                total_missing += diff_result["missing_count"]
                total_added += diff_result["added_count"]

                status = "UNCHANGED"
                if diff_result["modified_count"] > 0 or diff_result["missing_count"] > 0 or diff_result["added_count"] > 0:
                    status = "DRIFT_DETECTED"

                pages_report.append({
                    "key": key,
                    "url": live_snap["page"].get("url") or baseline_snap["page"].get("url"),
                    "baseline_url": baseline_snap["page"].get("url"),
                    "live_url": live_snap["page"].get("url"),
                    "view_name": live_snap["page"].get("view_name") or baseline_snap["page"].get("view_name"),
                    "viewport": viewport,
                    "viewport_size": viewport_size,
                    "title": live_snap["page"].get("title") or baseline_snap["page"].get("title"),
                    "type": live_snap["page"].get("type") or baseline_snap["page"].get("type"),
                    "baseline_file": baseline_snap.get("file_name"),
                    "status": status,
                    "statistics": {
                        "baseline_element_count": b_count,
                        "live_element_count": l_count,
                        "matched_unchanged": diff_result["matched_unchanged_count"],
                        "modified": diff_result["modified_count"],
                        "missing": diff_result["missing_count"],
                        "added": diff_result["added_count"],
                    },
                    "missing_elements": diff_result["missing_elements"],
                    "added_elements": diff_result["added_elements"],
                    "modified_elements": diff_result["modified_elements"],
                })

            elif baseline_snap and not live_snap:
                # Entire page / view is missing in live crawl
                b_elems = baseline_snap.get("elements", [])
                b_count = len(b_elems)
                total_baseline_elements += b_count
                total_missing += b_count

                pages_report.append({
                    "key": key,
                    "url": baseline_snap["page"].get("url"),
                    "baseline_url": baseline_snap["page"].get("url"),
                    "live_url": None,
                    "view_name": baseline_snap["page"].get("view_name"),
                    "viewport": viewport,
                    "viewport_size": viewport_size,
                    "title": baseline_snap["page"].get("title"),
                    "type": baseline_snap["page"].get("type"),
                    "baseline_file": baseline_snap.get("file_name"),
                    "status": "PAGE_MISSING_IN_LIVE",
                    "statistics": {
                        "baseline_element_count": b_count,
                        "live_element_count": 0,
                        "matched_unchanged": 0,
                        "modified": 0,
                        "missing": b_count,
                        "added": 0,
                    },
                    "missing_elements": baseline_snap.get("elements", []),
                    "added_elements": [],
                    "modified_elements": [],
                })

            elif live_snap and not baseline_snap:
                # Entire page / view is new in live crawl
                l_elems = live_snap.get("elements", [])
                l_count = len(l_elems)
                total_live_elements += l_count
                total_added += l_count

                pages_report.append({
                    "key": key,
                    "url": live_snap["page"].get("url"),
                    "baseline_url": None,
                    "live_url": live_snap["page"].get("url"),
                    "view_name": live_snap["page"].get("view_name"),
                    "viewport": viewport,
                    "viewport_size": viewport_size,
                    "title": live_snap["page"].get("title"),
                    "type": live_snap["page"].get("type"),
                    "baseline_file": None,
                    "status": "NEW_PAGE_IN_LIVE",
                    "statistics": {
                        "baseline_element_count": 0,
                        "live_element_count": l_count,
                        "matched_unchanged": 0,
                        "modified": 0,
                        "missing": 0,
                        "added": l_count,
                    },
                    "missing_elements": [],
                    "added_elements": live_snap.get("elements", []),
                    "modified_elements": [],
                })

        # Compute per-viewport summary breakdown
        by_viewport = {}
        for vp in VIEWPORT_ORDER:
            by_viewport[vp] = {
                "views_compared": 0,
                "baseline_elements": 0,
                "live_elements": 0,
                "matched_unchanged": 0,
                "modified": 0,
                "missing": 0,
                "added": 0,
                "has_drift": False,
                "drift_percentage": 0.0,
            }

        for p in pages_report:
            vp = p.get("viewport")
            if vp and vp in by_viewport:
                st = p.get("statistics", {})
                by_viewport[vp]["views_compared"] += 1
                by_viewport[vp]["baseline_elements"] += st.get("baseline_element_count", 0)
                by_viewport[vp]["live_elements"] += st.get("live_element_count", 0)
                by_viewport[vp]["matched_unchanged"] += st.get("matched_unchanged", 0)
                by_viewport[vp]["modified"] += st.get("modified", 0)
                by_viewport[vp]["missing"] += st.get("missing", 0)
                by_viewport[vp]["added"] += st.get("added", 0)

        for vp, vp_data in by_viewport.items():
            vp_drift = vp_data["modified"] + vp_data["missing"] + vp_data["added"]
            vp_data["has_drift"] = vp_drift > 0
            vp_data["drift_percentage"] = round(
                (vp_drift / max(vp_data["baseline_elements"], 1)) * 100, 2
            )

        has_drift = (total_modified > 0 or total_missing > 0 or total_added > 0)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline_directory": str(self.baseline_dir),
            "baseline_url": b_base,
            "live_url": l_base,
            "summary": {
                "total_views_compared": len(pages_report),
                "total_baseline_elements": total_baseline_elements,
                "total_live_elements": total_live_elements,
                "total_matched_unchanged": total_matched_unchanged,
                "total_modified": total_modified,
                "total_missing": total_missing,
                "total_added": total_added,
                "has_drift": has_drift,
                "drift_percentage": round(
                    ((total_modified + total_missing + total_added) / max(total_baseline_elements, 1)) * 100, 2
                ),
                "by_viewport": by_viewport,
            },
            "noise_filtering": {
                "enabled": self.noise_filter.enabled,
                "ignored_attributes": list(self.noise_filter.ignored_attributes),
            },
            "pages": pages_report,
        }

        return report

    def save_report(
        self,
        report: Dict[str, Any],
        output_file: Path = COMPARISON_REPORT_FILE,
    ) -> Path:
        """Save the comparison report to JSON in the root directory."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return output_file

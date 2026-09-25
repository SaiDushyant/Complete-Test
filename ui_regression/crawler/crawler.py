import asyncio
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import (
    urldefrag,
    urljoin,
    urlparse,
)

from playwright.async_api import (
    Error as PlaywrightError,
    Page,
    Response,
)

from crawler.auth import is_session_expired
from crawler.crawler_config import (
    ALLOWED_DOMAINS,
    BASE_DOMAIN,
    BASE_URL,
    BASELINE_DOMAIN,
    BASELINE_URL,
    DEFAULT_VIEWPORT,
    DEFAULT_VIEWPORT_HEIGHT,
    LIVE_DOMAIN,
    LIVE_URL,
    MAX_DEPTH,
    MAX_PAGES,
    NON_HTML_EXTENSIONS,
    OUTPUT_DIR,
    REPORT_FILE,
    TIMEOUT,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    WAIT_AFTER_LOAD,
    get_viewport_config,
    parse_viewports,
)
from crawler.element_extractor import extract_elements


# ============================================================
# URL UTILITIES
# ============================================================

def normalize_url(url: str, base: str = None) -> str:
    """
    Normalize URL:
    - Resolves relative URLs against base
    - Strips fragment identifiers (#section)
    - Normalizes trailing slashes (preserves root '/')
    - Filters out non-HTTP schemes (javascript:, mailto:, data:, blob:, etc.)
    """
    if not url or not isinstance(url, str):
        return ""

    url = url.strip()

    # Reject non-navigable protocols
    lower_url = url.lower()
    if (
        lower_url.startswith("javascript:")
        or lower_url.startswith("mailto:")
        or lower_url.startswith("tel:")
        or lower_url.startswith("data:")
        or lower_url.startswith("blob:")
    ):
        return ""

    if base:
        url = urljoin(base, url)

    url, _ = urldefrag(url)
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""

    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    elif not path:
        path = "/"

    # Reconstruct normalized URL
    normalized = parsed._replace(path=path).geturl()
    return normalized


def is_allowed_domain(url: str, allowed_domains: list = None) -> bool:
    """Check if the URL belongs to an allowed domain."""
    domains = allowed_domains or ALLOWED_DOMAINS
    parsed = urlparse(url)
    return parsed.netloc in domains


def is_static_or_download_extension(url: str) -> bool:
    """Check if the URL ends with a known static or download file extension."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    for ext in NON_HTML_EXTENSIONS:
        if path.endswith(ext):
            return True
    return False


def filename_from_url(url: str, view_suffix: str = "", viewport: str = "") -> str:
    """
    Generate a deterministic, safe, collision-free filename for a given URL, view, and viewport.
    Combines a readable path slug with an MD5 hash segment.
    Format:
        {slug}_{viewport}_{url_hash}.json (if viewport provided)
        {slug}_{url_hash}.json (if viewport not provided)
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        slug = "home"
    else:
        slug = path.replace("/", "_")

    if view_suffix:
        slug += f"_view_{view_suffix}"

    if parsed.query:
        query_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", parsed.query)
        slug += f"_{query_clean}"

    if viewport:
        slug += f"_{viewport.strip().lower()}"

    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)[:120]

    hash_parts = [url]
    if view_suffix:
        hash_parts.append(f"view::{view_suffix}")
    if viewport:
        hash_parts.append(f"vp::{viewport.strip().lower()}")
    hash_target = "::".join(hash_parts)
    url_hash = hashlib.md5(hash_target.encode("utf-8")).hexdigest()[:8]

    return f"{slug}_{url_hash}.json"


def extract_viewport_from_filename(filename: str) -> str:
    """
    Attempt to extract the viewport name ('sm', 'md', 'lg', 'xl', '2xl') from a snapshot filename.
    Returns the viewport string if found, otherwise None.
    """
    pattern = r"_(sm|md|lg|xl|2xl)_[a-f0-9]{8}\.json$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None



# ============================================================
# SAFE NAVIGATION TARGET & VIEW EXTRACTION
# ============================================================

async def get_in_dom_views(page: Page) -> list:
    """
    Detect in-DOM sub-page containers or sidebar tabs:
    1. [data-page] containers (PHP / jQuery Dashboard shell)
    2. aside / #sidebar-nav tabs (React / Vite Client Portal)
    """
    try:
        views = await page.evaluate(
            """
            () => {
                const results = [];
                const seen = new Set();

                // 1. data-page containers (PHP Dashboard SPA)
                const pageContainers = document.querySelectorAll('[data-page]');
                if (pageContainers.length > 0) {
                    pageContainers.forEach(el => {
                        const pageName = el.getAttribute('data-page');
                        if (pageName && pageName.trim().length > 0 && !seen.has(pageName.trim())) {
                            seen.add(pageName.trim());
                            const titleEl = el.querySelector('.page_title p, .page_title, h2, h3');
                            const title = titleEl ? titleEl.innerText.trim() : pageName;
                            results.push({
                                type: 'data-page',
                                pageName: pageName.trim(),
                                title: title,
                                isHidden: el.classList.contains('hidden') || window.getComputedStyle(el).display === 'none'
                            });
                        }
                    });
                    return results;
                }

                // 2. Sidebar navigation tabs (React Client Portal)
                const sidebarButtons = document.querySelectorAll('aside button, #sidebar-nav button');
                if (sidebarButtons.length > 0) {
                    sidebarButtons.forEach(el => {
                        const text = el.innerText.trim();
                        if (text && text.length > 0 && text.length < 50 && !seen.has(text.toLowerCase())) {
                            seen.add(text.toLowerCase());
                            const cleanSlug = text.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
                            results.push({
                                type: 'sidebar-tab',
                                pageName: cleanSlug,
                                title: text,
                                buttonText: text
                            });
                        }
                    });
                    return results;
                }

                return results;
            }
            """
        )
        return views or []
    except Exception as e:
        print(f"Warning: Failed to inspect in-DOM views: {e}")
        return []


async def extract_safe_navigation_targets(page: Page, current_url: str, in_dom_page_names: set = None) -> list:
    """
    Discover safe navigation URLs from HTML elements without executing mutating actions.
    Excludes in-DOM view switches that are handled locally without HTTP requests.
    """
    in_dom_set = in_dom_page_names or set()

    try:
        raw_targets = await page.evaluate(
            """
            (inDomViews) => {
                const inDomSet = new Set(inDomViews || []);
                const results = [];
                const seen = new Set();

                function add(href, text, source) {
                    if (!href || typeof href !== 'string') return;
                    const cleanHref = href.trim();
                    if (!cleanHref || cleanHref.startsWith('#') || cleanHref.startsWith('javascript:')) return;
                    
                    // If this matches an in-DOM view container on the current page, skip treating as an external HTTP route
                    const trimmedRoute = cleanHref.replace(/^\\/+/, '').replace(/\\/+$/, '');
                    if (inDomSet.has(cleanHref) || inDomSet.has(trimmedRoute) || inDomSet.has(trimmedRoute.replace(/^dashboard\\//, ''))) {
                        return;
                    }

                    const key = cleanHref + '::' + (text || '');
                    if (!seen.has(key)) {
                        seen.add(key);
                        results.push({ href: cleanHref, text: (text || '').trim().substring(0, 200), source: source });
                    }
                }

                // 1. All anchor tags with href
                document.querySelectorAll('a[href]').forEach(el => {
                    add(el.getAttribute('href') || el.href, el.innerText, 'anchor');
                });

                // 2. Elements with role='link'
                document.querySelectorAll('[role="link"]').forEach(el => {
                    const href = el.getAttribute('href') || el.getAttribute('data-href') || el.getAttribute('data-url');
                    add(href, el.innerText, 'role-link');
                });

                // 3. Navigation menu anchors
                document.querySelectorAll('nav a, header a, [role="navigation"] a, [role="menuitem"] a').forEach(el => {
                    const href = el.getAttribute('href') || el.href;
                    add(href, el.innerText, 'navigation-menu');
                });

                // 4. Same-origin Iframes
                document.querySelectorAll('iframe[src]').forEach(el => {
                    add(el.getAttribute('src'), 'iframe', 'iframe-src');
                });

                // 5. Explicit navigation link classes (e.g. clientPortalLink -> /client-portal/)
                document.querySelectorAll('.clientPortalLink, [class*="clientPortal"]').forEach(el => {
                    add('/client-portal/', el.innerText || 'Client Portal', 'client-portal-link');
                });

                return results;
            }
            """,
            list(in_dom_set)
        )
    except Exception as err:
        print(f"Warning: Failed to extract navigation targets via JS evaluation: {err}")
        raw_targets = []

    discovered = []
    seen_urls = set()

    for item in raw_targets:
        normalized = normalize_url(item.get("href", ""), base=current_url)
        if not normalized:
            continue

        if normalized not in seen_urls:
            seen_urls.add(normalized)
            discovered.append({
                "url": normalized,
                "text": item.get("text", ""),
                "source": item.get("source", "unknown")
            })

    return discovered


# ============================================================
# CRAWLER CLASS
# ============================================================

class Crawler:
    def __init__(
        self,
        page: Page,
        start_url: str = None,
        max_depth: int = MAX_DEPTH,
        max_pages: int = MAX_PAGES,
        allowed_domains: list = None,
        timeout: int = TIMEOUT,
        wait_after_load: int = WAIT_AFTER_LOAD,
        output_dir: Path = OUTPUT_DIR,
        save_to_disk: bool = True,
        viewport: str = DEFAULT_VIEWPORT,
        viewport_size: dict = None,
    ):
        self.page = page
        effective_start = start_url or BASELINE_URL
        self.start_url = normalize_url(effective_start)
        self.max_depth = max_depth
        self.max_pages = max_pages
        
        # Determine allowed domains, ensuring start URL's domain is automatically permitted
        start_domain = urlparse(self.start_url).netloc
        domains_list = list(allowed_domains or ALLOWED_DOMAINS)
        if start_domain and start_domain not in domains_list:
            domains_list.append(start_domain)
        self.allowed_domains = domains_list
        self.base_domain = start_domain or BASELINE_DOMAIN
        self.timeout = timeout
        wait_after_load = wait_after_load
        self.wait_after_load = wait_after_load
        self.output_dir = Path(output_dir)
        self.save_to_disk = save_to_disk
        self.viewport = (viewport or DEFAULT_VIEWPORT).strip().lower()
        self.viewport_size = viewport_size or get_viewport_config(self.viewport)

        # State management
        self.visited = set()
        self.queue = deque()
        self.discovered_urls = set()
        self.extracted_snapshots = {}

        # Download event flag
        self._download_triggered = False

        # Metrics and reporting
        self.stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "start_url": self.start_url,
            "viewport": self.viewport,
            "viewport_size": self.viewport_size,
            "max_depth": self.max_depth,
            "max_pages": self.max_pages,
            "pages_discovered": 0,
            "pages_crawled": 0,
            "in_dom_views_crawled": 0,
            "pages_skipped_non_html": 0,
            "pages_skipped_external": 0,
            "pages_skipped_depth": 0,
            "pages_skipped_limit": 0,
            "errors_count": 0,
            "crawled_pages": [],
            "skipped_non_html": [],
            "skipped_external": [],
            "errors": [],
        }

        # Setup download listener
        self.page.on("download", self._on_download)

    def _on_download(self, download):
        """Handler for Playwright download events."""
        self._download_triggered = True
        print(f"SKIP: Download detected for URL: {download.url}")
        try:
            asyncio.create_task(download.cancel())
        except Exception:
            pass

    async def run(self) -> dict:
        """Run the crawler workflow."""
        self.stats["start_time"] = datetime.now(timezone.utc).isoformat()
        start_ts = datetime.now(timezone.utc)

        if not self.start_url:
            raise ValueError(f"Invalid start URL: {self.start_url or BASELINE_URL}")

        self.queue.append((self.start_url, 0))
        self.discovered_urls.add(self.start_url)

        while self.queue:
            # Check maximum page limit
            if len(self.stats["crawled_pages"]) >= self.max_pages:
                remaining = len(self.queue)
                self.stats["pages_skipped_limit"] += remaining
                print(f"Reached CRAWLER_MAX_PAGES limit ({self.max_pages}). Stopping queue processing.")
                break

            url, depth = self.queue.popleft()

            if url in self.visited:
                continue

            # Check depth limit
            if depth > self.max_depth:
                self.stats["pages_skipped_depth"] += 1
                continue

            self.visited.add(url)

            print()
            print("=" * 80)
            print(f"URL: {url} [{self.viewport}] ({self.viewport_size['width']}px)")
            print(f"Depth: {depth}")
            print(f"Visited count: {len(self.visited)}")
            print(f"Crawled entries: {len(self.stats['crawled_pages'])} / {self.max_pages}")
            print("=" * 80)

            # Skip known non-HTML static file extensions before making page requests
            if is_static_or_download_extension(url):
                print(f"SKIP: non-HTML resource by extension: {url}")
                self.stats["pages_skipped_non_html"] += 1
                self.stats["skipped_non_html"].append({"url": url, "reason": "extension"})
                continue

            # Skip external domains
            if not is_allowed_domain(url, self.allowed_domains):
                print(f"SKIP: external domain: {url}")
                self.stats["pages_skipped_external"] += 1
                self.stats["skipped_external"].append(url)
                continue

            try:
                await self.crawl_page(url, depth)
            except Exception as error:
                err_msg = repr(error)
                print(f"ERROR crawling {url} [{self.viewport}]: {err_msg}")
                self.stats["errors_count"] += 1
                self.stats["errors"].append({
                    "url": url,
                    "viewport": self.viewport,
                    "depth": depth,
                    "error": err_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

        end_ts = datetime.now(timezone.utc)
        self.stats["end_time"] = end_ts.isoformat()
        self.stats["duration_seconds"] = round((end_ts - start_ts).total_seconds(), 2)
        self.stats["pages_discovered"] = len(self.discovered_urls)

        # Save summary crawl report
        self.save_crawl_report()
        return self.stats

    async def crawl_page(self, url: str, depth: int):
        """Navigate to a single page, validate response, extract DOM, process in-DOM views, and discover new targets."""
        self._download_triggered = False

        response: Response = None
        for attempt in range(2):
            try:
                response = await self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout,
                )
                break
            except PlaywrightError as pe:
                err_str = str(pe).lower()
                if "download is starting" in err_str or "err_aborted" in err_str:
                    print(f"SKIP: non-HTML download triggered during goto: {url}")
                    self.stats["pages_skipped_non_html"] += 1
                    self.stats["skipped_non_html"].append({"url": url, "reason": "download_event"})
                    return
                if attempt == 0 and "timeout" in err_str:
                    print(f"Navigation timed out on {url} [{self.viewport}], retrying once...")
                    await self.page.wait_for_timeout(2000)
                    continue
                raise


        if self._download_triggered:
            print(f"SKIP: non-HTML download response: {url}")
            self.stats["pages_skipped_non_html"] += 1
            self.stats["skipped_non_html"].append({"url": url, "reason": "download_event"})
            return

        # Check response content-type
        status_code = response.status if response else 200
        content_type = ""
        if response:
            headers = response.headers
            content_type = headers.get("content-type", "").lower()
            print(f"HTTP status: {status_code} | Content-Type: {content_type}")

            # If response is not HTML (e.g. CSV, JSON, binary), skip DOM extraction
            if content_type and "text/html" not in content_type and "application/xhtml" not in content_type:
                print(f"SKIP: non-HTML Content-Type ({content_type}): {url}")
                self.stats["pages_skipped_non_html"] += 1
                self.stats["skipped_non_html"].append({
                    "url": url,
                    "reason": f"content_type_{content_type}",
                    "status": status_code
                })
                return

        # If we landed on /login or root while authenticated, allow client-side redirect to settle
        if "/login" in self.page.url.lower() or self.page.url.rstrip("/").endswith("xtremenext.com"):
            try:
                await self.page.wait_for_url("**/dashboard**", timeout=6000)
            except Exception:
                pass

        # Allow dynamic content to render and wait for potential page containers
        await self.page.wait_for_timeout(self.wait_after_load)
        try:
            await self.page.wait_for_selector("[data-page], .contentholder, #sidebar-nav, aside", timeout=5000)
        except Exception:
            pass

        # Wait for skeleton and loader overlays to finish loading if present
        try:
            skeleton = await self.page.query_selector("#dashboardSkeleton, .dashboard-skeleton-rail, .loader-overlay, .watchlist-initial-loading")
            if skeleton and await skeleton.is_visible():
                await self.page.wait_for_selector("#dashboardSkeleton, .loader-overlay", state="hidden", timeout=4000)
        except Exception:
            pass

        try:
            await self.page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass

        # Check for authentication expiration / login redirects
        if await is_session_expired(self.page):
            current_url = self.page.url
            raise RuntimeError(
                f"Authentication expired. Page redirected to login interface: {current_url}"
            )

        final_url = self.page.url
        page_title = await self.page.title()

        # 1. Detect all in-DOM views (e.g. data-page containers or React sidebar tabs)
        in_dom_views = await get_in_dom_views(self.page)
        in_dom_page_names = {v["pageName"] for v in in_dom_views}

        # 2. Extract initial root page elements
        elements = await extract_elements(self.page)
        print(f"Root elements found: {len(elements)} (viewport: {self.viewport})")

        # 3. Discover links on root page (excluding in-DOM view names)
        discovered_targets = await extract_safe_navigation_targets(self.page, final_url, in_dom_page_names)

        # Save root page JSON
        root_filename = filename_from_url(url, viewport=self.viewport)
        root_filepath = self.output_dir / root_filename

        page_record = {
            "page": {
                "url": url,
                "final_url": final_url,
                "title": page_title,
                "viewport": self.viewport,
                "viewport_size": self.viewport_size,
                "depth": depth,
                "http_status": status_code,
                "content_type": content_type or "text/html",
                "type": "root_page"
            },
            "in_dom_views": [v["pageName"] for v in in_dom_views],
            "statistics": {
                "element_count": len(elements),
                "link_count": len(discovered_targets),
                "in_dom_views_count": len(in_dom_views)
            },
            "elements": elements,
            "discovered_links": discovered_targets
        }

        # Store in-memory snapshot
        root_key = f"{url.split('#')[0].rstrip('/')}::viewport::{self.viewport}"
        self.extracted_snapshots[root_key] = {
            "file_name": root_filename,
            "page": page_record["page"],
            "elements": elements,
            "statistics": page_record["statistics"],
        }

        if self.save_to_disk:
            with open(root_filepath, "w", encoding="utf-8") as f:
                json.dump(page_record, f, indent=2, ensure_ascii=False)
            print(f"Saved root page [{self.viewport}]: {root_filepath}")
        else:
            print(f"Extracted root page in-memory [{self.viewport}]: {url} ({len(elements)} elements)")

        self.stats["pages_crawled"] += 1
        self.stats["crawled_pages"].append({
            "url": url,
            "final_url": final_url,
            "title": page_title,
            "viewport": self.viewport,
            "depth": depth,
            "status": status_code,
            "elements": len(elements),
            "output_file": root_filename,
            "type": "root_page"
        })

        # 4. Process each in-DOM sub-page view safely
        if in_dom_views:
            print(f"Found {len(in_dom_views)} in-DOM SPA page views on {url}: {', '.join(in_dom_page_names)}")
            for v in in_dom_views:
                pname = v["pageName"]
                view_title = v.get("title") or pname

                print(f"Activating in-DOM view: {pname} [{self.viewport}]...")
                activated = await self._activate_in_dom_view(v)
                if not activated:
                    print(f"Could not switch to in-DOM view: {pname} [{self.viewport}]")
                    continue

                await self.page.wait_for_timeout(self.wait_after_load)
                try:
                    await self.page.wait_for_load_state("networkidle", timeout=2500)
                except Exception:
                    pass

                # Extract elements in this activated view state
                view_elements = await extract_elements(self.page)
                view_links = await extract_safe_navigation_targets(self.page, final_url, in_dom_page_names)

                view_filename = filename_from_url(url, view_suffix=pname, viewport=self.viewport)
                view_filepath = self.output_dir / view_filename

                view_record = {
                    "page": {
                        "url": f"{url}#{pname}",
                        "parent_url": url,
                        "view_name": pname,
                        "viewport": self.viewport,
                        "viewport_size": self.viewport_size,
                        "title": f"{page_title} - {view_title}",
                        "depth": depth + 1,
                        "http_status": 200,
                        "content_type": "text/html",
                        "type": "in_dom_view"
                    },
                    "statistics": {
                        "element_count": len(view_elements),
                        "link_count": len(view_links)
                    },
                    "elements": view_elements,
                    "discovered_links": view_links
                }

                # Store in-memory snapshot
                view_key = f"{url.split('#')[0].rstrip('/')}::view::{pname.lower()}::viewport::{self.viewport}"
                self.extracted_snapshots[view_key] = {
                    "file_name": view_filename,
                    "page": view_record["page"],
                    "elements": view_elements,
                    "statistics": view_record["statistics"],
                }

                if self.save_to_disk:
                    with open(view_filepath, "w", encoding="utf-8") as f:
                        json.dump(view_record, f, indent=2, ensure_ascii=False)
                    print(f"Saved in-DOM view '{pname}' [{self.viewport}]: {view_filepath} ({len(view_elements)} elements)")
                else:
                    print(f"Extracted in-DOM view in-memory '{pname}' [{self.viewport}] ({len(view_elements)} elements)")

                self.stats["in_dom_views_crawled"] += 1
                self.stats["crawled_pages"].append({
                    "url": f"{url}#{pname}",
                    "final_url": final_url,
                    "title": f"{page_title} - {view_title}",
                    "viewport": self.viewport,
                    "depth": depth + 1,
                    "status": 200,
                    "elements": len(view_elements),
                    "output_file": view_filename,
                    "type": "in_dom_view"
                })

                # Merge any links discovered inside this view
                for link_item in view_links:
                    discovered_targets.append(link_item)

        # 5. Enqueue newly discovered safe targets
        for item in discovered_targets:
            target_url = item["url"]
            lower_url = target_url.lower()

            # Skip mutating / session termination endpoints
            if any(term in lower_url for term in ("/logout", "/login/logout", "/delete", "/destroy", "/remove", "/drop", "/reset")):
                continue

            self.discovered_urls.add(target_url)

            if not is_allowed_domain(target_url, self.allowed_domains):
                continue

            if is_static_or_download_extension(target_url):
                continue

            if target_url not in self.visited:
                if depth + 1 <= self.max_depth and len(self.stats["crawled_pages"]) + len(self.queue) < self.max_pages * 2:
                    self.queue.append((target_url, depth + 1))

    async def _activate_in_dom_view(self, view: dict) -> bool:
        """
        Safely activate an in-DOM view container without executing mutating actions:
        - For sidebar tabs (React client-portal), clicks the matching sidebar button.
        - For data-page containers (PHP dashboard), dispatches navigation event and toggles visibility.
        """
        vtype = view.get("type", "data-page")
        pname = view.get("pageName", "")
        btn_text = view.get("buttonText", "")

        try:
            if vtype == "sidebar-tab":
                btn = self.page.locator(f"aside button:has-text('{btn_text}'), #sidebar-nav button:has-text('{btn_text}')").first
                if await btn.count() > 0:
                    try:
                        await btn.click(timeout=3000)
                        return True
                    except Exception:
                        try:
                            await btn.dispatch_event("click")
                            return True
                        except Exception:
                            pass
                return False
            else:
                switched = await self.page.evaluate(
                    """
                    (pname) => {
                        // 1. Dispatch click on matching safe data-nav element if present
                        const navEl = document.querySelector(`[data-nav="${pname}"]`);
                        if (navEl) {
                            try {
                                navEl.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                            } catch (_) {}
                        }

                        // 2. Ensure target data-page is unhidden and siblings hidden
                        const allPages = document.querySelectorAll('[data-page]');
                        let found = false;
                        allPages.forEach(el => {
                            if (el.getAttribute('data-page') === pname) {
                                el.classList.remove('hidden');
                                el.style.display = 'block';
                                found = true;
                            } else {
                                el.classList.add('hidden');
                                el.style.display = 'none';
                            }
                        });

                        // 3. Fire registered loaders if available
                        if (typeof window.refreshDashboardOverview === 'function' && pname === 'dashboard') {
                            window.__dashboardOverviewDirty = true;
                            window.refreshDashboardOverview();
                        }
                        if (typeof window.getLastdayOrderHistory === 'function' && ['chart', 'position', 'history'].includes(pname)) {
                            try { window.getLastdayOrderHistory(); } catch (_) {}
                        }
                        return found;
                    }
                    """,
                    pname
                )
                return switched
        except Exception as e:
            print(f"Warning: Failed to activate in-DOM view '{pname}': {e}")
            return False

    def save_crawl_report(self):
        """Save overall crawl summary report as JSON."""
        if not self.save_to_disk:
            return
        try:
            report_path = self.output_dir / "crawl_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            print(f"Crawl report saved to: {report_path}")
        except Exception as e:
            print(f"Failed to save crawl report: {e}")


async def crawl_public_auth_pages(
    browser,
    urls: list,
    output_dir: Path,
    save_to_disk: bool = True,
    timeout: int = TIMEOUT,
    wait_after_load: int = WAIT_AFTER_LOAD,
    viewports: list = None,
    viewport: str = None,
    max_workers: int = 5,
) -> dict:
    """
    Crawl unauthenticated auth/public entry pages (Login, Signup/Register, Password Reset)
    in clean, unauthenticated browser contexts without session redirects across viewports concurrently.
    """
    snapshots = {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if viewports is not None:
        target_viewports = parse_viewports(viewports)
    elif viewport is not None:
        target_viewports = [viewport.strip().lower()]
    else:
        target_viewports = list(VIEWPORT_ORDER)

    sem = asyncio.Semaphore(max_workers)

    async def crawl_viewport_auth_pages(vp: str) -> dict:
        async with sem:
            vp_size = get_viewport_config(vp)
            vp_snaps = {}
            unauth_context = await browser.new_context(viewport=vp_size)

            try:
                for target_url in urls:
                    normalized = normalize_url(target_url)
                    if not normalized:
                        continue

                    page = await unauth_context.new_page()
                    print(f"Crawling public auth page [{vp}] ({vp_size['width']}px): {normalized}")

                    try:
                        response = None
                        for attempt in range(2):
                            try:
                                response = await page.goto(
                                    normalized,
                                    wait_until="domcontentloaded",
                                    timeout=timeout,
                                )
                                break
                            except Exception as auth_err:
                                if attempt == 0 and "timeout" in str(auth_err).lower():
                                    print(f"Auth page navigation timed out on {normalized} [{vp}], retrying once...")
                                    await page.wait_for_timeout(2000)
                                    continue
                                raise

                        await page.wait_for_timeout(wait_after_load)
                        try:
                            await page.wait_for_load_state("networkidle", timeout=2500)
                        except Exception:
                            pass
                        try:
                            await page.wait_for_selector(".loader-overlay, .animsition-loading", state="hidden", timeout=5000)
                        except Exception:
                            pass
                        try:
                            await page.wait_for_selector("body:not(.animsition-loading)", timeout=5000)
                        except Exception:
                            pass

                        elements = await extract_elements(page)
                        page_title = await page.title()
                        status_code = response.status if response else 200

                        page_filename = filename_from_url(normalized, viewport=vp)
                        page_filepath = output_dir / page_filename

                        page_record = {
                            "page": {
                                "url": normalized,
                                "final_url": page.url,
                                "title": page_title,
                                "viewport": vp,
                                "viewport_size": vp_size,
                                "depth": 0,
                                "http_status": status_code,
                                "content_type": "text/html",
                                "type": "auth_page",
                            },
                            "statistics": {
                                "element_count": len(elements),
                                "link_count": 0,
                            },
                            "elements": elements,
                        }

                        root_key = f"{normalized.split('#')[0].rstrip('/')}::viewport::{vp}"
                        vp_snaps[root_key] = {
                            "file_name": page_filename,
                            "page": page_record["page"],
                            "elements": elements,
                            "statistics": page_record["statistics"],
                        }

                        if save_to_disk:
                            with open(page_filepath, "w", encoding="utf-8") as f:
                                json.dump(page_record, f, indent=2, ensure_ascii=False)
                            print(f"Saved public auth page [{vp}]: {page_filepath} ({len(elements)} elements)")
                        else:
                            print(f"Extracted public auth page in-memory [{vp}]: {normalized} ({len(elements)} elements)")

                    except Exception as e:
                        print(f"Warning: Failed to crawl public auth page '{normalized}' [{vp}]: {e}")
                    finally:
                        await page.close()

            finally:
                await unauth_context.close()

            return vp_snaps

    results = await asyncio.gather(*(crawl_viewport_auth_pages(vp) for vp in target_viewports))
    for r in results:
        snapshots.update(r)

    return snapshots


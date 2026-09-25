"""
CLI Entrypoint for the Playwright Element Comparer & Drift Detector.
Runs a live comparison of the website DOM elements against baseline snapshots across 5 viewports:
sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px).

Usage:
    python -m comparer.run_comparer
    python -m comparer.run_comparer --viewports sm,md,lg,xl,2xl
    python -m comparer.run_comparer --baseline-dir element_output --headed
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

from crawler.auth import create_authenticated_context
from crawler.crawler import Crawler, crawl_public_auth_pages
from crawler.crawler_config import (
    ALLOWED_DOMAINS,
    AUTH_STATE,
    BASE_URL,
    BASELINE_AUTH_STATE,
    BASELINE_URL,
    DEFAULT_VIEWPORT,
    DEFAULT_WORKERS,
    LIVE_AUTH_STATE,
    LIVE_POST_LOGIN_URL_PATTERN,
    LIVE_TEST_USER_EMAIL,
    LIVE_TEST_USER_PASSWORD,
    LIVE_TRADING_AUTH_PAGES,
    LIVE_URL,
    MAX_DEPTH,
    MAX_PAGES,
    TIMEOUT,
    TRADING_AUTH_PAGES,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    WAIT_AFTER_LOAD,
    get_trading_auth_pages,
    get_viewport_config,
    parse_viewports,
)
from comparer.comparer import ElementComparer, NoiseFilter
from comparer.comparer_config import (
    BASELINE_DIR,
    COMPARISON_REPORT_FILE,
    HEADLESS,
)


def print_banner(
    baseline_url: str,
    live_url: str,
    baseline_dir: Path,
    report_file: Path,
    viewports: list,
    noise_filtering: bool,
    headless: bool,
):
    print()
    print("=" * 80)
    print("PLAYWRIGHT DOM ELEMENT COMPARER & DRIFT DETECTOR (5-VIEWPORT LIVE VS BASELINE)")
    print("=" * 80)
    print(f"Target Baseline URL : {baseline_url}")
    print(f"Target Live URL     : {live_url}")
    if live_url != baseline_url:
        print(f"Cross-Environment   : Active (Comparing live '{live_url}' vs baseline '{baseline_url}')")
    print(f"Baseline Directory  : {baseline_dir}")
    print(f"Report Output File  : {report_file}")
    print(f"Target Viewports    : {', '.join(viewports)} (Widths: {', '.join(str(VIEWPORTS[v]['width']) + 'px' for v in viewports)})")
    print(f"Noise Filtering     : {'Enabled' if noise_filtering else 'Disabled'}")
    print(f"Headless Mode       : {headless}")
    print("=" * 80)
    print()


def print_comparison_summary(report: dict, report_path: Path):
    summary = report.get("summary", {})
    by_viewport = summary.get("by_viewport", {})
    pages = report.get("pages", [])

    print()
    print("=" * 80)
    print("5-VIEWPORT COMPARISON & DRIFT DETECTION SUMMARY")
    print("=" * 80)
    print(f"Total Views / Pages Compared : {summary.get('total_views_compared', 0)}")
    print(f"Total Baseline Elements      : {summary.get('total_baseline_elements', 0)}")
    print(f"Total Live Elements          : {summary.get('total_live_elements', 0)}")
    print(f"Matched Unchanged Elements   : {summary.get('total_matched_unchanged', 0)}")
    print(f"Modified / Changed Elements  : {summary.get('total_modified', 0)}")
    print(f"Missing Elements in Live DOM : {summary.get('total_missing', 0)}")
    print(f"Newly Added Elements in Live : {summary.get('total_added', 0)}")
    print(f"Overall Drift Percentage     : {summary.get('drift_percentage', 0.0)}%")
    
    if summary.get("has_drift"):
        print(f"Status                       : ⚠️  UI / DOM DRIFT DETECTED")
    else:
        print(f"Status                       : ✅  NO DRIFT - DOM MATCHES BASELINE PERFECTLY")
    print("=" * 80)
    print()

    # Per-Viewport Summary Breakdown Table
    if by_viewport:
        print("PER-VIEWPORT DRIFT SUMMARY:")
        print("-" * 80)
        print(f"{'Viewport':<10} | {'Width':<8} | {'Views':<6} | {'Matched':<8} | {'Modified':<9} | {'Missing':<8} | {'Added':<6} | {'Status':<12}")
        print("-" * 80)
        for vp in VIEWPORT_ORDER:
            if vp in by_viewport:
                vp_data = by_viewport[vp]
                if vp_data.get("views_compared", 0) > 0:
                    w = f"{VIEWPORTS[vp]['width']}px" if vp in VIEWPORTS else ""
                    vc = vp_data.get("views_compared", 0)
                    mat = vp_data.get("matched_unchanged", 0)
                    mod = vp_data.get("modified", 0)
                    mis = vp_data.get("missing", 0)
                    add = vp_data.get("added", 0)
                    st = "⚠️ DRIFT" if vp_data.get("has_drift") else "✅ MATCH"
                    print(f"{vp:<10} | {w:<8} | {vc:<6} | {mat:<8} | {mod:<9} | {mis:<8} | {add:<6} | {st:<12}")
        print("-" * 80)
        print()

    # Per-View Breakdown Table
    print("VIEW / PAGE BREAKDOWN ACROSS VIEWPORTS:")
    print("-" * 90)
    print(f"{'View / Page Name':<34} | {'VP':<5} | {'Status':<16} | {'Match':<6} | {'Mod':<5} | {'Miss':<5} | {'Add':<5}")
    print("-" * 90)

    for p in pages:
        vname = p.get("view_name") or p.get("url", "")
        if len(vname) > 32:
            vname = vname[:29] + "..."
        
        vp = p.get("viewport") or "-"
        status = p.get("status", "UNKNOWN")
        stats = p.get("statistics", {})
        matched = stats.get("matched_unchanged", 0)
        mod = stats.get("modified", 0)
        miss = stats.get("missing", 0)
        add = stats.get("added", 0)

        status_icon = "✅ UNCHANGED" if status == "UNCHANGED" else "⚠️ DRIFT"
        if status == "PAGE_MISSING_IN_LIVE":
            status_icon = "❌ MISSING PAGE"
        elif status == "NEW_PAGE_IN_LIVE":
            status_icon = "✨ NEW PAGE"

        print(f"{vname:<34} | {vp:<5} | {status_icon:<16} | {matched:<6} | {mod:<5} | {miss:<5} | {add:<5}")

    print("-" * 90)

    # Detailed Drift Highlights (if any)
    drifted_pages = [p for p in pages if p.get("status") not in ("UNCHANGED",)]
    if drifted_pages:
        print()
        print("=" * 80)
        print("DRIFT DETAILS & HIGHLIGHTS")
        print("=" * 80)

        for p in drifted_pages:
            vname = p.get("view_name") or p.get("url")
            vp = p.get("viewport") or ""
            vp_label = f" [{vp}]" if vp else ""
            print(f"\n📍 View: {vname}{vp_label} ({p.get('url')})")
            
            # Show modified elements
            modified = p.get("modified_elements", [])
            if modified:
                print(f"   🟡 Modified Elements ({len(modified)}):")
                for mod_item in modified[:5]:
                    loc = mod_item.get("locator") or f"<{mod_item.get('tag')}>"
                    diffs = mod_item.get("diffs", {})
                    diff_keys = ", ".join(diffs.keys())
                    print(f"      - {loc} -> Changes in: [{diff_keys}]")
                    for k, d in diffs.items():
                        if isinstance(d, dict) and "baseline" in d and "live" in d:
                            b_val = str(d['baseline'])[:60]
                            l_val = str(d['live'])[:60]
                            print(f"          • {k}: baseline='{b_val}' vs live='{l_val}'")
                if len(modified) > 5:
                    print(f"      ... and {len(modified) - 5} more modified elements (see full JSON report)")

            # Show missing elements
            missing = p.get("missing_elements", [])
            if missing:
                print(f"   🔴 Missing Elements ({len(missing)}):")
                for miss_item in missing[:5]:
                    loc = miss_item.get("locator") or f"<{miss_item.get('tag')}>"
                    text = (miss_item.get("text") or "")[:40]
                    txt_preview = f" (text='{text}')" if text else ""
                    print(f"      - {loc}{txt_preview}")
                if len(missing) > 5:
                    print(f"      ... and {len(missing) - 5} more missing elements (see full JSON report)")

            # Show added elements
            added = p.get("added_elements", [])
            if added:
                print(f"   🟢 Added Elements ({len(added)}):")
                for add_item in added[:5]:
                    loc = add_item.get("locator") or f"<{add_item.get('tag')}>"
                    text = (add_item.get("text") or "")[:40]
                    txt_preview = f" (text='{text}')" if text else ""
                    print(f"      - {loc}{txt_preview}")
                if len(added) > 5:
                    print(f"      ... and {len(added) - 5} more added elements (see full JSON report)")

        print("=" * 80)

    print()
    print(f"Full structured comparison report saved to: {report_path}")
    print()


async def run_comparison(
    viewports: list = None,
    baseline_dir: Path = BASELINE_DIR,
    report_file: Path = COMPARISON_REPORT_FILE,
    enable_noise_filter: bool = True,
    headless: bool = HEADLESS,
    workers: int = DEFAULT_WORKERS,
    baseline_url: str = None,
    live_url: str = None,
):
    selected_viewports = parse_viewports(viewports)
    target_baseline_url = baseline_url or BASELINE_URL
    target_live_url = live_url or LIVE_URL

    print_banner(
        baseline_url=target_baseline_url,
        live_url=target_live_url,
        baseline_dir=baseline_dir,
        report_file=report_file,
        viewports=selected_viewports,
        noise_filtering=enable_noise_filter,
        headless=headless,
    )

    # 1. Initialize Comparer and load baseline snapshots
    noise_filter = NoiseFilter(
        enabled=enable_noise_filter,
        baseline_base_url=target_baseline_url,
        live_base_url=target_live_url,
    )
    comparer = ElementComparer(
        baseline_dir=baseline_dir,
        noise_filter=noise_filter,
        baseline_base_url=target_baseline_url,
        live_base_url=target_live_url,
    )

    print(f"Loading baseline snapshots from '{baseline_dir}'...")
    all_baseline_snapshots = comparer.load_baseline_snapshots()

    if not all_baseline_snapshots:
        print(f"\n[ERROR] No baseline snapshots found in directory: {baseline_dir}")
        print("Please run the crawler first to generate baseline element snapshots:")
        print("    python -m crawler.run_crawler\n")
        sys.exit(1)

    # Filter baseline snapshots to selected viewports if specified
    baseline_snapshots = {}
    for k, v in all_baseline_snapshots.items():
        vp = v.get("page", {}).get("viewport")
        if not vp or vp in selected_viewports:
            baseline_snapshots[k] = v

    print(f"Loaded {len(baseline_snapshots)} baseline view snapshot(s) across selected viewports: {', '.join(selected_viewports)}")
    print()

    # 2. Launch browser for live extraction
    start_time = time.time()
    live_snapshots = {}
    effective_auth_state = LIVE_AUTH_STATE if target_live_url != target_baseline_url else AUTH_STATE
    live_auth_pages = get_trading_auth_pages(target_live_url)

    async with async_playwright() as playwright:
        print(f"Launching Chromium browser for live DOM extraction ({target_live_url})...")
        browser = await playwright.chromium.launch(headless=headless)
        try:
            # 3. Extract public auth entry pages in-memory across selected viewports concurrently
            print("\n--- Extracting Public Auth Pages (In-Memory) ---")
            auth_snapshots = await crawl_public_auth_pages(
                browser=browser,
                urls=live_auth_pages,
                output_dir=baseline_dir,
                save_to_disk=False,
                timeout=TIMEOUT,
                wait_after_load=WAIT_AFTER_LOAD,
                viewports=selected_viewports,
                max_workers=workers,
            )
            live_snapshots.update(auth_snapshots)

            # 4. Authenticate once
            print(f"\n--- Initializing / Verifying Authenticated Session on {target_live_url} ---")
            auth_context = await create_authenticated_context(
                browser=browser,
                base_url=target_live_url,
                email=LIVE_TEST_USER_EMAIL,
                password=LIVE_TEST_USER_PASSWORD,
                post_login_url_pattern=LIVE_POST_LOGIN_URL_PATTERN,
                auth_state_path=effective_auth_state,
            )
            await auth_context.close()

            # 5. Extract live application DOM for each viewport in-memory concurrently
            print(f"\n--- Extracting Live DOM across {len(selected_viewports)} Viewports ({workers} workers) ---")
            sem = asyncio.Semaphore(max(1, workers))

            async def extract_single_viewport(vp: str) -> dict:
                async with sem:
                    vp_size = get_viewport_config(vp)
                    print(f"\n[Worker] EXTRACTING LIVE DOM FOR VIEWPORT: {vp.upper()} ({vp_size['width']}x{vp_size['height']})")

                    context = await browser.new_context(
                        storage_state=str(effective_auth_state),
                        viewport=vp_size,
                    )
                    page = await context.new_page()

                    try:
                        crawler = Crawler(
                            page=page,
                            start_url=target_live_url,
                            max_depth=MAX_DEPTH,
                            max_pages=MAX_PAGES,
                            allowed_domains=ALLOWED_DOMAINS,
                            timeout=TIMEOUT,
                            wait_after_load=WAIT_AFTER_LOAD,
                            output_dir=baseline_dir,
                            save_to_disk=False,  # Keep baseline files untouched during comparison
                            viewport=vp,
                            viewport_size=vp_size,
                        )

                        await crawler.run()
                        return crawler.extracted_snapshots
                    finally:
                        await page.close()
                        await context.close()

            results = await asyncio.gather(*(extract_single_viewport(vp) for vp in selected_viewports))
            for vp_snaps in results:
                live_snapshots.update(vp_snaps)

            print(f"\nLive extraction complete. Captured {len(live_snapshots)} total view(s) across all viewports in-memory.")

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Live extraction failed: {e}", file=sys.stderr)
            await browser.close()
            sys.exit(1)

        await browser.close()

    # 5. Perform comparison and diff analysis
    print("\nRunning multi-tier element matching and drift analysis across viewports...")
    report = comparer.compare_all(
        baseline_snapshots,
        live_snapshots,
        baseline_base_url=target_baseline_url,
        live_base_url=target_live_url,
    )
    report["execution_duration_seconds"] = round(time.time() - start_time, 2)

    # 6. Save JSON report to root directory
    saved_path = comparer.save_report(report, report_file)

    # 7. Print formatted summary
    print_comparison_summary(report, saved_path)


def main():
    parser = argparse.ArgumentParser(
        description="Compare live website DOM elements against baseline JSON snapshots across 5 viewports."
    )
    parser.add_argument(
        "--live-url",
        type=str,
        default=LIVE_URL,
        help=f"Target live URL to crawl and compare (default: {LIVE_URL})",
    )
    parser.add_argument(
        "--baseline-url",
        type=str,
        default=BASELINE_URL,
        help=f"Baseline URL used to match existing snapshots (default: {BASELINE_URL})",
    )
    parser.add_argument(
        "--viewports",
        type=str,
        default=",".join(VIEWPORT_ORDER),
        help=f"Comma-separated viewports to compare (default: {','.join(VIEWPORT_ORDER)})",
    )
    parser.add_argument(
        "--baseline-dir",
        type=str,
        default=str(BASELINE_DIR),
        help=f"Directory containing baseline element snapshot JSON files (default: {BASELINE_DIR})",
    )
    parser.add_argument(
        "--report-file",
        type=str,
        default=str(COMPARISON_REPORT_FILE),
        help=f"File path where comparison report will be saved (default: {COMPARISON_REPORT_FILE})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of concurrent viewport workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--no-noise-filter",
        action="store_true",
        help="Disable dynamic noise filtering (timestamps, relative times, tokens)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed (visible) mode",
    )

    args = parser.parse_args()

    baseline_dir = Path(args.baseline_dir)
    report_file = Path(args.report_file)
    enable_noise_filter = not args.no_noise_filter
    headless = False if args.headed else HEADLESS

    asyncio.run(
        run_comparison(
            viewports=args.viewports,
            baseline_dir=baseline_dir,
            report_file=report_file,
            enable_noise_filter=enable_noise_filter,
            headless=headless,
            workers=args.workers,
            baseline_url=args.baseline_url,
            live_url=args.live_url,
        )
    )


if __name__ == "__main__":
    main()


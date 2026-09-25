"""
CLI Entrypoint for the Admin DOM Element Comparer & Drift Detector.
Runs a live comparison of the Admin website DOM elements against baseline snapshots across 5 viewports:
sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px).

Usage:
    python -m comparer.run_comparer_admin
    python -m comparer.run_comparer_admin --viewports sm,md,lg,xl,2xl
    python -m comparer.run_comparer_admin --headed
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

from crawler.auth_admin import create_authenticated_admin_context
from crawler.crawler import Crawler, crawl_public_auth_pages
from crawler.crawler_config import (
    ADMIN_AUTH_PAGES,
    ADMIN_AUTH_STATE,
    ADMIN_BASE_URL,
    ALLOWED_DOMAINS,
    BASELINE_ADMIN_AUTH_PAGES,
    BASELINE_ADMIN_AUTH_STATE,
    BASELINE_ADMIN_BASE_URL,
    BASELINE_ADMIN_LOGIN_URL,
    DEFAULT_VIEWPORT,
    DEFAULT_WORKERS,
    LIVE_ADMIN_AUTH_PAGES,
    LIVE_ADMIN_AUTH_STATE,
    LIVE_ADMIN_BASE_URL,
    LIVE_ADMIN_LOGIN_URL,
    LIVE_ADMIN_POST_LOGIN_URL_PATTERN,
    LIVE_ADMIN_USER_PASSWORD,
    LIVE_ADMIN_USER_USERNAME,
    MAX_DEPTH,
    MAX_PAGES,
    TIMEOUT,
    VIEWPORT_NAMES,
    VIEWPORT_ORDER,
    VIEWPORTS,
    WAIT_AFTER_LOAD,
    get_admin_auth_pages,
    get_viewport_config,
    parse_viewports,
)
from comparer.comparer import ElementComparer, NoiseFilter
from comparer.comparer_config import (
    ADMIN_BASELINE_DIR,
    ADMIN_COMPARISON_REPORT_FILE,
    HEADLESS,
)
from comparer.run_comparer import print_comparison_summary


def print_admin_banner(
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
    print("PLAYWRIGHT ADMIN DOM ELEMENT COMPARER & DRIFT DETECTOR (5-VIEWPORT LIVE VS BASELINE)")
    print("=" * 80)
    print(f"Target Baseline Admin URL : {baseline_url}")
    print(f"Target Live Admin URL     : {live_url}")
    if live_url != baseline_url:
        print(f"Cross-Environment         : Active (Comparing live '{live_url}' vs baseline '{baseline_url}')")
    print(f"Baseline Directory        : {baseline_dir}")
    print(f"Report Output File        : {report_file}")
    print(f"Target Viewports          : {', '.join(viewports)} (Widths: {', '.join(str(VIEWPORTS[v]['width']) + 'px' for v in viewports)})")
    print(f"Noise Filtering           : {'Enabled' if noise_filtering else 'Disabled'}")
    print(f"Headless Mode             : {headless}")
    print("=" * 80)
    print()


async def run_admin_comparison(
    viewports: list = None,
    baseline_dir: Path = ADMIN_BASELINE_DIR,
    report_file: Path = ADMIN_COMPARISON_REPORT_FILE,
    enable_noise_filter: bool = True,
    headless: bool = HEADLESS,
    workers: int = DEFAULT_WORKERS,
    baseline_url: str = None,
    live_url: str = None,
):
    selected_viewports = parse_viewports(viewports)
    target_baseline_url = baseline_url or BASELINE_ADMIN_BASE_URL
    target_live_url = live_url or LIVE_ADMIN_BASE_URL

    print_admin_banner(
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

    print(f"Loading admin baseline snapshots from '{baseline_dir}'...")
    all_baseline_snapshots = comparer.load_baseline_snapshots()

    if not all_baseline_snapshots:
        print(f"\n[ERROR] No baseline snapshots found in directory: {baseline_dir}")
        print("Please run the admin crawler first to generate baseline element snapshots:")
        print("    python -m crawler.run_crawler_admin\n")
        sys.exit(1)

    # Filter baseline snapshots to selected viewports
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
    effective_auth_state = LIVE_ADMIN_AUTH_STATE if target_live_url != target_baseline_url else ADMIN_AUTH_STATE
    live_auth_pages = get_admin_auth_pages(LIVE_ADMIN_LOGIN_URL)

    async with async_playwright() as playwright:
        print(f"Launching Chromium browser for live Admin DOM extraction ({target_live_url})...")
        browser = await playwright.chromium.launch(headless=headless)

        try:
            # 3. Extract public admin auth pages unauthenticated across selected viewports concurrently
            print("\n--- Extracting Public Admin Auth Pages (In-Memory) ---")
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
            print(f"\n--- Initializing / Verifying Admin Authenticated Session on {target_live_url} ---")
            auth_context = await create_authenticated_admin_context(
                browser=browser,
                admin_base_url=target_live_url,
                admin_login_url=LIVE_ADMIN_LOGIN_URL,
                username=LIVE_ADMIN_USER_USERNAME,
                password=LIVE_ADMIN_USER_PASSWORD,
                post_login_url_pattern=LIVE_ADMIN_POST_LOGIN_URL_PATTERN,
                auth_state_path=effective_auth_state,
            )
            await auth_context.close()

            # 5. Extract live Admin application DOM for each viewport in-memory concurrently
            print(f"\n--- Extracting Live Admin DOM across {len(selected_viewports)} Viewports ({workers} workers) ---")
            sem = asyncio.Semaphore(max(1, workers))

            async def extract_single_admin_viewport(vp: str) -> dict:
                async with sem:
                    vp_size = get_viewport_config(vp)
                    print(f"\n[Worker] EXTRACTING LIVE ADMIN DOM FOR VIEWPORT: {vp.upper()} ({vp_size['width']}x{vp_size['height']})")

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

            results = await asyncio.gather(*(extract_single_admin_viewport(vp) for vp in selected_viewports))
            for vp_snaps in results:
                live_snapshots.update(vp_snaps)

            print(f"\nLive Admin extraction complete. Captured {len(live_snapshots)} total view(s) across all viewports in-memory.")

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Admin live extraction failed: {e}", file=sys.stderr)
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
        description="Compare live Admin website DOM elements against baseline JSON snapshots across 5 viewports."
    )
    parser.add_argument(
        "--live-url",
        type=str,
        default=LIVE_ADMIN_BASE_URL,
        help=f"Target live Admin URL to crawl and compare (default: {LIVE_ADMIN_BASE_URL})",
    )
    parser.add_argument(
        "--baseline-url",
        type=str,
        default=BASELINE_ADMIN_BASE_URL,
        help=f"Baseline Admin URL used to match existing snapshots (default: {BASELINE_ADMIN_BASE_URL})",
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
        default=str(ADMIN_BASELINE_DIR),
        help=f"Directory containing baseline element snapshot JSON files (default: {ADMIN_BASELINE_DIR})",
    )
    parser.add_argument(
        "--report-file",
        type=str,
        default=str(ADMIN_COMPARISON_REPORT_FILE),
        help=f"File path where comparison report will be saved (default: {ADMIN_COMPARISON_REPORT_FILE})",
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
        run_admin_comparison(
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


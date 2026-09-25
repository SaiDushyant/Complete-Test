"""
CLI Entrypoint for the Admin Console Playwright Crawler.
Discovers and extracts DOM elements from all Admin panel pages and views across 5 viewports:
sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px).

Usage:
    python -m crawler.run_crawler_admin
    python -m crawler.run_crawler_admin --viewports sm,md,lg,xl,2xl
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

from crawler.auth_admin import create_authenticated_admin_context
from crawler.crawler import Crawler, crawl_public_auth_pages
from crawler.crawler_config import (
    ADMIN_AUTH_PAGES,
    ADMIN_AUTH_STATE,
    ADMIN_BASE_URL,
    ADMIN_OUTPUT_DIR,
    ADMIN_REPORT_FILE,
    ALLOWED_DOMAINS,
    BASELINE_ADMIN_AUTH_PAGES,
    BASELINE_ADMIN_AUTH_STATE,
    BASELINE_ADMIN_BASE_URL,
    BASELINE_ADMIN_LOGIN_URL,
    BASELINE_ADMIN_POST_LOGIN_URL_PATTERN,
    BASELINE_ADMIN_USER_PASSWORD,
    BASELINE_ADMIN_USER_USERNAME,
    DEFAULT_VIEWPORT,
    DEFAULT_WORKERS,
    HEADLESS,
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


async def run_admin_crawler_workflow(
    start_url: str = None,
    viewports: list = None,
    output_dir: Path = ADMIN_OUTPUT_DIR,
    headless: bool = HEADLESS,
    timeout: int = TIMEOUT,
    wait_after_load: int = WAIT_AFTER_LOAD,
    max_depth: int = MAX_DEPTH,
    max_pages: int = MAX_PAGES,
    workers: int = DEFAULT_WORKERS,
):
    selected_viewports = parse_viewports(viewports)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    effective_start_url = start_url or BASELINE_ADMIN_BASE_URL
    admin_auth_pages = get_admin_auth_pages()

    print()
    print("=" * 80)
    print("PLAYWRIGHT ADMIN APPLICATION BASELINE CRAWLER (5-VIEWPORT REGRESSION TESTING)")
    print("=" * 80)
    print(f"Admin Baseline URL: {effective_start_url}")
    print(f"Allowed Domains   : {', '.join(ALLOWED_DOMAINS)}")
    print(f"Target Viewports  : {', '.join(selected_viewports)} (Widths: {', '.join(str(VIEWPORTS[v]['width']) + 'px' for v in selected_viewports)})")
    print(f"Max Workers       : {workers}")
    print(f"Max Depth         : {max_depth}")
    print(f"Max Pages / VP    : {max_pages}")
    print(f"Timeout (ms)      : {timeout}")
    print(f"Wait After Load   : {wait_after_load} ms")
    print(f"Headless          : {headless}")
    print(f"Output Directory  : {output_dir}")
    print("=" * 80)
    print()

    overall_start_time = time.time()
    per_viewport_stats = {}

    async with async_playwright() as playwright:
        print("Launching Chromium browser for Admin Crawl...")
        browser = await playwright.chromium.launch(headless=headless)

        try:
            # 1. Crawl public admin auth page unauthenticated across all viewports
            print("\n--- Crawling Public Admin Auth Pages (Unauthenticated) ---")
            auth_snapshots = await crawl_public_auth_pages(
                browser=browser,
                urls=admin_auth_pages,
                output_dir=output_dir,
                save_to_disk=True,
                timeout=timeout,
                wait_after_load=wait_after_load,
                viewports=selected_viewports,
                max_workers=workers,
            )

            # 2. Establish authenticated admin session once
            print("\n--- Initializing / Verifying Admin Authenticated Session ---")
            auth_context = await create_authenticated_admin_context(
                browser=browser,
                admin_base_url=effective_start_url,
                admin_login_url=BASELINE_ADMIN_LOGIN_URL,
                username=BASELINE_ADMIN_USER_USERNAME,
                password=BASELINE_ADMIN_USER_PASSWORD,
                post_login_url_pattern=BASELINE_ADMIN_POST_LOGIN_URL_PATTERN,
                auth_state_path=BASELINE_ADMIN_AUTH_STATE,
            )
            await auth_context.close()

            # 3. Crawl authenticated admin application concurrently across viewports with worker pool
            print(f"\n--- Starting Concurrent Admin Crawling across {len(selected_viewports)} Viewports ({workers} workers) ---")
            sem = asyncio.Semaphore(max(1, workers))

            async def crawl_single_admin_viewport(vp: str):
                async with sem:
                    vp_size = get_viewport_config(vp)
                    print(f"\n[Worker] STARTING ADMIN CRAWL FOR VIEWPORT: {vp.upper()} ({vp_size['width']}x{vp_size['height']})")

                    context = await browser.new_context(
                        storage_state=str(BASELINE_ADMIN_AUTH_STATE),
                        viewport=vp_size,
                    )
                    page = await context.new_page()

                    try:
                        crawler = Crawler(
                            page=page,
                            start_url=effective_start_url,
                            max_depth=max_depth,
                            max_pages=max_pages,
                            allowed_domains=ALLOWED_DOMAINS,
                            timeout=timeout,
                            wait_after_load=wait_after_load,
                            output_dir=output_dir,
                            save_to_disk=True,
                            viewport=vp,
                            viewport_size=vp_size,
                        )

                        stats = await crawler.run()
                        return vp, stats
                    finally:
                        await page.close()
                        await context.close()

            results = await asyncio.gather(*(crawl_single_admin_viewport(vp) for vp in selected_viewports))
            for vp, stats in results:
                per_viewport_stats[vp] = stats

        except Exception as e:
            print(f"\nCRITICAL ADMIN CRAWLER ERROR: {e}", file=sys.stderr)
            await browser.close()
            sys.exit(1)

        await browser.close()

    total_duration = round(time.time() - overall_start_time, 2)
    total_pages_crawled = sum(s.get("pages_crawled", 0) for s in per_viewport_stats.values())
    total_in_dom_views = sum(s.get("in_dom_views_crawled", 0) for s in per_viewport_stats.values())
    total_errors = sum(s.get("errors_count", 0) for s in per_viewport_stats.values())

    master_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline_url": effective_start_url,
        "base_url": effective_start_url,
        "total_duration_seconds": total_duration,
        "viewports": selected_viewports,
        "summary": {
            "viewports_count": len(selected_viewports),
            "total_pages_crawled": total_pages_crawled,
            "total_in_dom_views_crawled": total_in_dom_views,
            "total_errors": total_errors,
        },
        "by_viewport": per_viewport_stats,
    }

    report_file = output_dir / "crawl_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print("ADMIN 5-VIEWPORT CRAWLING SUMMARY")
    print("=" * 80)
    print(f"Total Duration       : {total_duration}s")
    print(f"Viewports Completed  : {', '.join(selected_viewports)}")
    print(f"Total Pages Crawled  : {total_pages_crawled}")
    print(f"Total In-DOM Views   : {total_in_dom_views}")
    print(f"Total Errors         : {total_errors}")
    print(f"Report File          : {report_file}")
    print(f"JSON Files Saved In  : {output_dir}")
    print("-" * 80)
    print(f"{'Viewport':<10} | {'Width':<8} | {'Pages Crawled':<15} | {'In-DOM Views':<14} | {'Errors':<8}")
    print("-" * 80)
    for vp in selected_viewports:
        st = per_viewport_stats.get(vp, {})
        w = f"{VIEWPORTS[vp]['width']}px"
        pc = st.get("pages_crawled", 0)
        vc = st.get("in_dom_views_crawled", 0)
        ec = st.get("errors_count", 0)
        print(f"{vp:<10} | {w:<8} | {pc:<15} | {vc:<14} | {ec:<8}")
    print("=" * 80)
    print()


def main():
    parser = argparse.ArgumentParser(description="Playwright 5-Viewport Admin Application Crawler")
    parser.add_argument(
        "--start-url",
        "--baseline-url",
        dest="start_url",
        type=str,
        default=BASELINE_ADMIN_BASE_URL,
        help=f"Baseline start URL to crawl (default: {BASELINE_ADMIN_BASE_URL})",
    )
    parser.add_argument(
        "--viewports",
        type=str,
        default=",".join(VIEWPORT_ORDER),
        help=f"Comma-separated viewports to crawl (default: {','.join(VIEWPORT_ORDER)})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ADMIN_OUTPUT_DIR),
        help=f"Output directory for JSON element snapshots (default: {ADMIN_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=MAX_PAGES,
        help=f"Max pages to crawl per viewport (default: {MAX_PAGES})",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=MAX_DEPTH,
        help=f"Max crawl depth (default: {MAX_DEPTH})",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of concurrent viewport workers (default: {DEFAULT_WORKERS})",
    )

    args = parser.parse_args()
    headless = False if args.headed else HEADLESS

    asyncio.run(
        run_admin_crawler_workflow(
            start_url=args.start_url,
            viewports=args.viewports,
            output_dir=Path(args.output_dir),
            headless=headless,
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            workers=args.workers,
        )
    )


if __name__ == "__main__":
    main()


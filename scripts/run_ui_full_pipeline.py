#!/usr/bin/env python3
"""
Full UI Regression Pipeline (Re-crawl + Compare + Diagnostics Status).

Executes the complete end-to-end UI regression and drift detection pipeline:
  Step 1: Re-crawls application pages to refresh baseline snapshots.
  Step 2: Compares live pages against baselines with full runtime diagnostics
          (Console JS errors, uncaught exceptions, failed network requests, HTTP 4xx/5xx).
  Step 3: Parses generated comparison reports and displays a structured
          breakdown of drift statuses and runtime error incidents.

Default execution mode: HEADLESS (use --headed to visually watch browser execution).

Usage:
    python scripts/run_ui_full_pipeline.py [OPTIONS]

Examples:
    python scripts/run_ui_full_pipeline.py                     # Run complete pipeline for all portals
    python scripts/run_ui_full_pipeline.py --portal admin      # Run pipeline only for Admin portal
    python scripts/run_ui_full_pipeline.py --portal client     # Run pipeline only for Client portal
    python scripts/run_ui_full_pipeline.py --skip-crawl        # Skip crawl, only compare & report
    python scripts/run_ui_full_pipeline.py --headed            # Run with visible browser
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
UI_REGRESSION_DIR = ROOT_DIR / "ui_regression"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(UI_REGRESSION_DIR) not in sys.path:
    sys.path.insert(0, str(UI_REGRESSION_DIR))

from scripts.status import find_all_statuses


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Full UI Regression Pipeline (Re-crawl + Compare + Diagnostics Status).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--portal",
        choices=["admin", "client", "both"],
        default="both",
        help="Portal to process: admin, client, or both (default: both)",
    )
    parser.add_argument(
        "--viewports",
        nargs="+",
        default=None,
        help="Viewports to process: desktop, mobile, tablet (default: all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in visible/headed mode (default: headless)",
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        default=False,
        help="Skip re-crawling baselines, execute comparison directly",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to crawl per viewport",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum crawl depth from entry page",
    )
    return parser.parse_args()


async def run_pipeline():
    args = parse_arguments()
    headless = not args.headed

    print("=" * 80)
    print("🚀 FULL UI REGRESSION & DRIFT PIPELINE")
    print("=" * 80)
    print(f"  Target Portal(s)    : {args.portal.upper()}")
    print(f"  Execution Mode      : {'HEADED (Visible Browser)' if args.headed else 'HEADLESS (Background)'}")
    print(f"  Skip Re-crawl       : {args.skip_crawl}")
    print(f"  Viewports           : {args.viewports or 'All configured'}")
    print("=" * 80)
    print()

    # Set environment variables
    os.environ["BROWSER_HEADLESS"] = "false" if args.headed else "true"
    os.environ["CRAWLER_HEADLESS"] = "false" if args.headed else "true"

    reports_dir = ROOT_DIR / "reports" / "ui_regression"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # STEP 1: RE-CRAWL BASELINES (IF NOT SKIPPED)
    # -------------------------------------------------------------
    if not args.skip_crawl:
        print("\n" + "=" * 80)
        print("PHASE 1: RE-CRAWLING APPLICATION BASELINES")
        print("=" * 80)

        if args.portal in ("admin", "both"):
            print("\n🏢 Re-crawling Admin Portal...")
            from ui_regression.crawler.run_crawler_admin import run_crawler_workflow as run_admin_crawl
            admin_crawl_kwargs = {"viewports": args.viewports, "headless": headless}
            if args.max_pages is not None:
                admin_crawl_kwargs["max_pages"] = args.max_pages
            if args.max_depth is not None:
                admin_crawl_kwargs["max_depth"] = args.max_depth
            await run_admin_crawl(**admin_crawl_kwargs)

        if args.portal in ("client", "both"):
            print("\n👤 Re-crawling Client Portal...")
            from ui_regression.crawler.run_crawler import run_crawler_workflow as run_client_crawl
            client_crawl_kwargs = {"viewports": args.viewports, "headless": headless}
            if args.max_pages is not None:
                client_crawl_kwargs["max_pages"] = args.max_pages
            if args.max_depth is not None:
                client_crawl_kwargs["max_depth"] = args.max_depth
            await run_client_crawl(**client_crawl_kwargs)
    else:
        print("\n⏭️  Skipping Phase 1 (Re-crawl). Using existing baseline snapshots.")

    # -------------------------------------------------------------
    # STEP 2: RUN DOM COMPARISON WITH TELEMETRY DIAGNOSTICS
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 2: RUNNING DOM COMPARISON & RUNTIME DIAGNOSTICS")
    print("=" * 80)

    generated_reports = []

    if args.portal in ("admin", "both"):
        print("\n🏢 Comparing Admin Portal DOM...")
        from ui_regression.comparer.run_comparer_admin import run_comparer_workflow as run_admin_compare
        admin_report = await run_admin_compare(
            viewports=args.viewports,
            output_dir=reports_dir,
            headless=headless,
        )
        generated_reports.append(("Admin Portal", admin_report))

    if args.portal in ("client", "both"):
        print("\n👤 Comparing Client Portal DOM...")
        from ui_regression.comparer.run_comparer import run_comparer_workflow as run_client_compare
        client_report = await run_client_compare(
            viewports=args.viewports,
            output_dir=reports_dir,
            headless=headless,
        )
        generated_reports.append(("Client Portal", client_report))

    # -------------------------------------------------------------
    # STEP 3: DISPLAY DIAGNOSTICS & STATUS INSPECTION
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 3: COMPREHENSIVE STATUS & DIAGNOSTIC INSPECTION")
    print("=" * 80)

    for portal_name, report_path in generated_reports:
        print(f"\n==================== {portal_name.upper()} BREAKDOWN ====================")
        if Path(report_path).exists():
            find_all_statuses(report_path)
        else:
            print(f"Warning: Report file {report_path} not found.")

    print("\n" + "=" * 80)
    print("🎉 FULL UI REGRESSION PIPELINE COMPLETE")
    print("=" * 80)


def main():
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()

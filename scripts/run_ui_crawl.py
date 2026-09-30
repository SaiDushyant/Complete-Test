#!/usr/bin/env python3
"""
UI Crawler & Baseline Generator (Re-Crawl Only).

Crawls the web applications (Admin Portal, Client Portal) across multiple viewports,
extracts full DOM element structures, and generates/updates baseline snapshot JSON files
in `ui_regression/element_output/` and `ui_regression/element_output_admin/`.

Default execution mode: HEADLESS (use --headed to visually observe crawler navigation).

Usage:
    python scripts/run_ui_crawl.py [OPTIONS]

Examples:
    python scripts/run_ui_crawl.py                         # Re-crawl both Admin and Client portals
    python scripts/run_ui_crawl.py --portal admin          # Re-crawl only Admin Portal
    python scripts/run_ui_crawl.py --portal client         # Re-crawl only Client Portal
    python scripts/run_ui_crawl.py --headed                # Visually observe crawler in browser
    python scripts/run_ui_crawl.py --viewports desktop     # Re-crawl only desktop viewport
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


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UI Crawler & Baseline Generator (Re-Crawl Only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--portal",
        choices=["admin", "client", "both"],
        default="both",
        help="Portal to crawl: admin, client, or both (default: both)",
    )
    parser.add_argument(
        "--viewports",
        nargs="+",
        default=None,
        help="Viewports to crawl: desktop, mobile, tablet (default: all)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in visible/headed mode (default: headless)",
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


async def main_async():
    args = parse_arguments()
    headless = not args.headed

    print("=" * 80)
    print("🕷️ UI CRAWLER & BASELINE GENERATOR")
    print("=" * 80)
    print(f"  Target Portal(s)    : {args.portal.upper()}")
    print(f"  Execution Mode      : {'HEADED (Visible Browser)' if args.headed else 'HEADLESS (Background)'}")
    print(f"  Viewports           : {args.viewports or 'All configured'}")
    if args.max_pages:
        print(f"  Max Pages           : {args.max_pages}")
    if args.max_depth:
        print(f"  Max Depth           : {args.max_depth}")
    print("=" * 80)
    print()

    # Set environment variables
    os.environ["BROWSER_HEADLESS"] = "false" if args.headed else "true"
    os.environ["CRAWLER_HEADLESS"] = "false" if args.headed else "true"

    # 1. Admin Portal Crawl
    if args.portal in ("admin", "both"):
        print("\n" + "=" * 60)
        print("🏢 Starting Admin Portal Crawler...")
        print("=" * 60)
        from ui_regression.crawler.run_crawler_admin import run_crawler_workflow as run_admin_crawl
        kwargs = {"viewports": args.viewports, "headless": headless}
        if args.max_pages is not None:
            kwargs["max_pages"] = args.max_pages
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth

        await run_admin_crawl(**kwargs)

    # 2. Client Portal Crawl
    if args.portal in ("client", "both"):
        print("\n" + "=" * 60)
        print("👤 Starting Client Portal Crawler...")
        print("=" * 60)
        from ui_regression.crawler.run_crawler import run_crawler_workflow as run_client_crawl
        kwargs = {"viewports": args.viewports, "headless": headless}
        if args.max_pages is not None:
            kwargs["max_pages"] = args.max_pages
        if args.max_depth is not None:
            kwargs["max_depth"] = args.max_depth

        await run_client_crawl(**kwargs)

    print()
    print("=" * 80)
    print("✅ BASELINE CRAWL COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"  📁 Admin Baselines   : {ROOT_DIR / 'ui_regression' / 'element_output_admin'}")
    print(f"  📁 Client Baselines  : {ROOT_DIR / 'ui_regression' / 'element_output'}")
    print("=" * 80)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

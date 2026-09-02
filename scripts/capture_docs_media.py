"""Capture README and recipe screenshots from the usage.py demo app."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "great-docs" / "assets" / "examples"
DEFAULT_BASE_URL = "http://127.0.0.1:65500"

CAPTURES = [
    ("hero-basic-formatting.png", "#section-basic", 1280, 720),
    ("client-side-selection.png", "#section-selection", 1280, 640),
    ("column-filtering.png", "#section-column-filtering", 1280, 760),
    ("row-expansion.png", "#section-expansion", 1280, 760),
    ("server-pagination.png", "#section-server", 1280, 720),
    ("row-dragging.png", "#section-row-dragging", 1280, 640),
]


def ensure_playwright() -> None:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required for docs media capture. Install with:\n"
            "  python -m pip install playwright\n"
            "  python -m playwright install chromium"
        ) from exc


def capture(base_url: str) -> None:
    from playwright.sync_api import sync_playwright

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for filename, anchor, width, height in CAPTURES:
            page.goto(f"{base_url}/{anchor}", wait_until="networkidle")
            page.wait_for_timeout(1200)
            target = page.locator(f"{anchor} .dash-mantine-datatable-root").first
            if target.count() == 0:
                target = page.locator(f"{anchor}").first
            output_path = ASSETS_DIR / filename
            target.screenshot(path=str(output_path))
            print(f"Captured {output_path}")

        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--launch-demo",
        action="store_true",
        help="Launch usage.py in the background before capturing screenshots.",
    )
    args = parser.parse_args()

    ensure_playwright()
    demo_process = None

    if args.launch_demo:
        demo_process = subprocess.Popen(
            [sys.executable, str(ROOT / "usage.py")],
            cwd=ROOT,
        )
        time.sleep(6)

    try:
        capture(args.base_url.rstrip("/"))
    finally:
        if demo_process is not None:
            demo_process.terminate()
            demo_process.wait(timeout=10)


if __name__ == "__main__":
    main()

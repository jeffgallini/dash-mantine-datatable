"""Build the Great Docs Quarto site for GitHub Pages."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREAT_DOCS_DIR = ROOT / "great-docs"
SITE_DIR = GREAT_DOCS_DIR / "_site"
BUILD_ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
}


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True, cwd=cwd or ROOT, env=BUILD_ENV)


def main() -> None:
    run([sys.executable, str(ROOT / "scripts" / "generate_recipes.py")])
    run(["quarto", "render", str(GREAT_DOCS_DIR)])

    if not SITE_DIR.exists():
        raise FileNotFoundError(f"Expected Quarto output in {SITE_DIR}")

    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Great Docs site ready at {SITE_DIR}")


if __name__ == "__main__":
    main()

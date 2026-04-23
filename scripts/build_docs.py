from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "site"
PACKAGE = "dash_mantine_datatable"


def ensure_site_entrypoint() -> None:
    index_path = OUTPUT_DIR / "index.html"
    if index_path.exists():
        return

    candidates = [
        OUTPUT_DIR / f"{PACKAGE}.html",
        OUTPUT_DIR / PACKAGE / "index.html",
    ]
    for candidate in candidates:
        if candidate.exists():
            relative_target = candidate.relative_to(OUTPUT_DIR).as_posix()
            index_path.write_text(
                "\n".join(
                    [
                        "<!doctype html>",
                        '<html lang="en">',
                        "  <head>",
                        '    <meta charset="utf-8">',
                        f'    <meta http-equiv="refresh" content="0; url={relative_target}">',
                        f'    <link rel="canonical" href="{relative_target}">',
                        "    <title>dash-mantine-datatable docs</title>",
                        "  </head>",
                        "  <body>",
                        f'    <p>Redirecting to <a href="{relative_target}">{relative_target}</a>...</p>',
                        "  </body>",
                        "</html>",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            return

    raise FileNotFoundError(
        "pdoc did not create an index.html or a recognizable package landing page "
        f"in {OUTPUT_DIR}."
    )


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pdoc",
            "--docformat",
            "numpy",
            "-o",
            str(OUTPUT_DIR),
            PACKAGE,
        ],
        check=True,
        cwd=ROOT,
    )

    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    ensure_site_entrypoint()


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from datetime import date
import os
import sys

from release_helpers import (
    ReleaseValidationError,
    apply_release_version,
    ensure_consistent_versions,
    ensure_release_notes_source,
    ensure_release_version_progression,
    parse_release_title,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply the release version requested by a release PR title."
    )
    parser.add_argument(
        "--title",
        default=os.environ.get("PR_TITLE"),
        help="Pull request title. Defaults to the PR_TITLE environment variable.",
    )
    parser.add_argument(
        "--release-date",
        default=os.environ.get("RELEASE_DATE") or date.today().isoformat(),
        help="Date to write into the changelog heading.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()

    try:
        if not args.title:
            raise ReleaseValidationError("A PR title is required to apply a release version.")

        release = parse_release_title(args.title)
        current_version = ensure_consistent_versions()
        ensure_release_version_progression(
            release.version,
            current_version,
            allow_equal=True,
        )
        ensure_release_notes_source(release.version, release.summary)

        apply_release_version(
            release.version,
            release_date=args.release_date,
            summary=release.summary,
        )
        ensure_consistent_versions(expected_version=release.version)
        print(release.version)
        return 0
    except ReleaseValidationError as error:
        print(f"Could not apply release version: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

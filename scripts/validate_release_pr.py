from __future__ import annotations

import argparse
import os
import sys

from release_helpers import (
    ReleaseValidationError,
    ensure_consistent_versions,
    ensure_release_notes_source,
    ensure_release_version_progression,
    parse_release_title,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a staging-to-main release pull request."
    )
    parser.add_argument(
        "--title",
        default=os.environ.get("PR_TITLE"),
        help="Pull request title. Defaults to the PR_TITLE environment variable.",
    )
    parser.add_argument(
        "--base-ref",
        default=os.environ.get("PR_BASE_REF"),
        help="Pull request base branch. Defaults to the PR_BASE_REF environment variable.",
    )
    parser.add_argument(
        "--head-ref",
        default=os.environ.get("PR_HEAD_REF"),
        help="Pull request head branch. Defaults to the PR_HEAD_REF environment variable.",
    )
    parser.add_argument(
        "--expected-base",
        default="main",
        help="Branch that release PRs must target.",
    )
    parser.add_argument(
        "--expected-head",
        default="staging",
        help="Branch that release PRs must originate from.",
    )
    parser.add_argument(
        "--allow-current-version",
        action="store_true",
        help="Allow the requested release version to match the current repo version.",
    )
    parser.add_argument(
        "--print-version",
        action="store_true",
        help="Print the validated release version to stdout.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()

    try:
        if not args.title:
            raise ReleaseValidationError("A PR title is required for release validation.")
        if not args.base_ref:
            raise ReleaseValidationError(
                "A PR base branch is required for release validation."
            )
        if not args.head_ref:
            raise ReleaseValidationError(
                "A PR head branch is required for release validation."
            )

        if args.base_ref != args.expected_base:
            raise ReleaseValidationError(
                f"Release PRs must target '{args.expected_base}', not '{args.base_ref}'."
            )
        if args.head_ref != args.expected_head:
            raise ReleaseValidationError(
                f"Release PRs must come from '{args.expected_head}', not '{args.head_ref}'."
            )

        release = parse_release_title(args.title)
        current_version = ensure_consistent_versions()
        ensure_release_version_progression(
            release.version,
            current_version,
            allow_equal=args.allow_current_version,
        )
        ensure_release_notes_source(release.version, release.summary)

        if args.print_version:
            print(release.version)
        else:
            print(
                f"Validated release PR '{args.title}' for {args.head_ref} -> "
                f"{args.base_ref}. Requested version {release.version} advances "
                f"from current version {current_version}."
            )
        return 0
    except ReleaseValidationError as error:
        print(f"Release PR validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

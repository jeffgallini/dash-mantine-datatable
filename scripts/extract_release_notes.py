from __future__ import annotations

import argparse
import sys

from release_helpers import ReleaseValidationError, extract_changelog_section


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the changelog section for a release version."
    )
    parser.add_argument("version", help="Version to extract from CHANGELOG.md.")
    args = parser.parse_args()

    try:
        sys.stdout.write(extract_changelog_section(args.version))
        return 0
    except ReleaseValidationError as error:
        print(f"Could not extract release notes: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

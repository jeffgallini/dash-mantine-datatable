from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_TITLE_PATTERN = re.compile(
    r"^v(?P<version>\d+\.\d+\.\d+) Release(?:\b.*)?$"
)
CHANGELOG_HEADING_PATTERN = re.compile(r"^##\s+v?(?P<version>\d+\.\d+\.\d+)\b")


class ReleaseValidationError(RuntimeError):
    """Raised when the repository is not ready for a release publish."""


def parse_release_title(title: str) -> str:
    match = RELEASE_TITLE_PATTERN.fullmatch(title.strip())
    if not match:
        raise ReleaseValidationError(
            "Release PR titles must match 'vX.Y.Z Release' and may optionally "
            "include extra descriptive text after that prefix."
        )
    return match.group("version")


def _load_json_version(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ReleaseValidationError(f"Missing a non-empty version in '{path}'.")
    return version.strip()


def _load_package_lock_version(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    top_level_version = payload.get("version")
    root_package_version = payload.get("packages", {}).get("", {}).get("version")
    versions = {
        value.strip()
        for value in (top_level_version, root_package_version)
        if isinstance(value, str) and value.strip()
    }

    if len(versions) != 1:
        raise ReleaseValidationError(
            "package-lock.json must contain the same version in both the top-level "
            "metadata and the root package entry."
        )

    return versions.pop()


def _load_project_toml_version(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"(?P<version>[^"]+)"\s*$', content)
    if not match:
        raise ReleaseValidationError(f"Could not find a version entry in '{path}'.")
    return match.group("version").strip()


def collect_version_map() -> dict[str, str]:
    version_files = {
        "package.json": _load_json_version(REPO_ROOT / "package.json"),
        "dash_mantine_datatable/package-info.json": _load_json_version(
            REPO_ROOT / "dash_mantine_datatable" / "package-info.json"
        ),
        "Project.toml": _load_project_toml_version(REPO_ROOT / "Project.toml"),
        "package-lock.json": _load_package_lock_version(REPO_ROOT / "package-lock.json"),
    }
    return version_files


def ensure_consistent_versions(expected_version: str | None = None) -> str:
    versions = collect_version_map()
    unique_versions = sorted(set(versions.values()))

    if len(unique_versions) != 1:
        formatted = ", ".join(
            f"{path}={version}" for path, version in sorted(versions.items())
        )
        raise ReleaseValidationError(
            "Release metadata versions do not match across source files: "
            f"{formatted}"
        )

    actual_version = unique_versions[0]
    if expected_version is not None and actual_version != expected_version:
        raise ReleaseValidationError(
            f"Release PR title version '{expected_version}' does not match the "
            f"package version '{actual_version}'."
        )

    return actual_version


def extract_changelog_section(version: str) -> str:
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    lines = changelog_path.read_text(encoding="utf-8").splitlines()

    start_index: int | None = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        match = CHANGELOG_HEADING_PATTERN.match(line.strip())
        if not match:
            continue

        if start_index is None and match.group("version") == version:
            start_index = index
            continue

        if start_index is not None:
            end_index = index
            break

    if start_index is None:
        raise ReleaseValidationError(
            f"CHANGELOG.md does not contain a '## {version} ...' section."
        )

    section = "\n".join(lines[start_index:end_index]).strip()
    if not section:
        raise ReleaseValidationError(
            f"CHANGELOG.md contains an empty section for version '{version}'."
        )

    return section + "\n"

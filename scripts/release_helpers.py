from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_PATH = REPO_ROOT / "package.json"
PACKAGE_LOCK_PATH = REPO_ROOT / "package-lock.json"
PACKAGE_INFO_PATH = REPO_ROOT / "dash_mantine_datatable" / "package-info.json"
PROJECT_TOML_PATH = REPO_ROOT / "Project.toml"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"

RELEASE_TITLE_PATTERN = re.compile(
    r"^v(?P<version>\d+\.\d+\.\d+) Release(?:\s*-\s*(?P<summary>.+))?$"
)
CHANGELOG_VERSION_HEADING_PATTERN = re.compile(r"^##\s+v?(?P<version>\d+\.\d+\.\d+)\b")
UNRELEASED_HEADING_PATTERN = re.compile(r"^##\s+Unreleased\b", re.IGNORECASE)


class ReleaseValidationError(RuntimeError):
    """Raised when release automation cannot safely proceed."""


@dataclass(frozen=True)
class ReleaseTitle:
    version: str
    summary: str | None = None


def parse_release_title(title: str) -> ReleaseTitle:
    match = RELEASE_TITLE_PATTERN.fullmatch(title.strip())
    if not match:
        raise ReleaseValidationError(
            "Release PR titles must match 'vX.Y.Z Release' and may optionally "
            "include a summary after ' - '."
        )

    summary = match.group("summary")
    return ReleaseTitle(
        version=match.group("version"),
        summary=summary.strip() if summary else None,
    )


def parse_version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ReleaseValidationError(f"Invalid semantic version '{version}'.")
    return tuple(int(part) for part in parts)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_json_version(path: Path) -> str:
    version = _load_json(path).get("version")
    if not isinstance(version, str) or not version.strip():
        raise ReleaseValidationError(f"Missing a non-empty version in '{path}'.")
    return version.strip()


def _load_package_lock_version(path: Path) -> str:
    payload = _load_json(path)
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
    return {
        "package.json": _load_json_version(PACKAGE_JSON_PATH),
        "dash_mantine_datatable/package-info.json": _load_json_version(PACKAGE_INFO_PATH),
        "Project.toml": _load_project_toml_version(PROJECT_TOML_PATH),
        "package-lock.json": _load_package_lock_version(PACKAGE_LOCK_PATH),
    }


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
            f"Release metadata version '{actual_version}' does not match the "
            f"expected version '{expected_version}'."
        )

    return actual_version


def ensure_release_version_progression(
    requested_version: str,
    current_version: str,
    *,
    allow_equal: bool = False,
) -> None:
    requested = parse_version_tuple(requested_version)
    current = parse_version_tuple(current_version)

    if requested == current and allow_equal:
        return
    if requested <= current:
        comparator = "match or exceed" if allow_equal else "be greater than"
        raise ReleaseValidationError(
            f"Release PR title version '{requested_version}' must {comparator} the "
            f"current package version '{current_version}'."
        )


def _find_version_section_indexes(
    lines: list[str],
    version: str,
) -> tuple[int, int] | None:
    start_index: int | None = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        match = CHANGELOG_VERSION_HEADING_PATTERN.match(line.strip())
        if not match:
            continue

        if start_index is None and match.group("version") == version:
            start_index = index
            continue

        if start_index is not None:
            end_index = index
            break

    if start_index is None:
        return None

    return start_index, end_index


def extract_changelog_section(version: str) -> str:
    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()
    section_indexes = _find_version_section_indexes(lines, version)
    if section_indexes is None:
        raise ReleaseValidationError(
            f"CHANGELOG.md does not contain a '## {version} ...' section."
        )

    start_index, end_index = section_indexes
    section = "\n".join(lines[start_index:end_index]).strip()
    if not section:
        raise ReleaseValidationError(
            f"CHANGELOG.md contains an empty section for version '{version}'."
        )

    return section + "\n"


def _find_unreleased_section_indexes(lines: list[str]) -> tuple[int, int] | None:
    start_index: int | None = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if start_index is None and UNRELEASED_HEADING_PATTERN.match(line.strip()):
            start_index = index
            continue

        if start_index is not None and line.startswith("## "):
            end_index = index
            break

    if start_index is None:
        return None

    return start_index, end_index


def ensure_release_notes_source(version: str, summary: str | None = None) -> None:
    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()
    if _find_version_section_indexes(lines, version) is not None:
        return
    if _find_unreleased_section_indexes(lines) is not None:
        return
    if summary:
        return

    raise ReleaseValidationError(
        "GitHub release notes require either a CHANGELOG '## Unreleased' section, "
        f"an existing '## {version}' section, or a summary in the PR title like "
        "'vX.Y.Z Release - Summary'."
    )


def _update_json_version(path: Path, version: str) -> None:
    payload = _load_json(path)
    payload["version"] = version
    _write_json(path, payload)


def _update_package_lock_version(version: str) -> None:
    payload = _load_json(PACKAGE_LOCK_PATH)
    payload["version"] = version

    packages = payload.setdefault("packages", {})
    root_package = packages.setdefault("", {})
    root_package["version"] = version

    _write_json(PACKAGE_LOCK_PATH, payload)


def _update_project_toml_version(version: str) -> None:
    content = PROJECT_TOML_PATH.read_text(encoding="utf-8")
    updated_content, replacement_count = re.subn(
        r'(?m)^version\s*=\s*"[^"]+"\s*$',
        f'version = "{version}"',
        content,
        count=1,
    )
    if replacement_count != 1:
        raise ReleaseValidationError(
            f"Could not update the version entry in '{PROJECT_TOML_PATH}'."
        )
    PROJECT_TOML_PATH.write_text(updated_content, encoding="utf-8")


def _normalize_release_body(
    body_lines: list[str],
    summary: str | None,
) -> list[str]:
    trimmed = list(body_lines)
    while trimmed and not trimmed[0].strip():
        trimmed.pop(0)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()

    if not trimmed:
        trimmed = [f"- {summary}"] if summary else ["- Release updates."]

    return ["", *trimmed, ""]


def _update_changelog(version: str, release_date: str, summary: str | None) -> None:
    content = CHANGELOG_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    version_heading = f"## {version} - {release_date}"

    if _find_version_section_indexes(lines, version) is not None:
        return

    unreleased_indexes = _find_unreleased_section_indexes(lines)
    if unreleased_indexes is not None:
        start_index, end_index = unreleased_indexes
        release_body = _normalize_release_body(lines[start_index + 1:end_index], summary)
        replacement = ["## Unreleased", "", version_heading, *release_body]
        new_lines = [*lines[:start_index], *replacement, *lines[end_index:]]
    else:
        release_body = _normalize_release_body([], summary)
        if lines and lines[0].startswith("# "):
            insertion = ["", "## Unreleased", "", version_heading, *release_body]
            new_lines = [lines[0], *insertion, *lines[1:]]
        else:
            new_lines = ["## Unreleased", "", version_heading, *release_body, *lines]

    CHANGELOG_PATH.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def apply_release_version(
    version: str,
    *,
    release_date: str | None = None,
    summary: str | None = None,
) -> None:
    effective_date = release_date or date.today().isoformat()

    _update_json_version(PACKAGE_JSON_PATH, version)
    _update_json_version(PACKAGE_INFO_PATH, version)
    _update_package_lock_version(version)
    _update_project_toml_version(version)
    _update_changelog(version, effective_date, summary)


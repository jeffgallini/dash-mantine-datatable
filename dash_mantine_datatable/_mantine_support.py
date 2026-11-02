"""Choose the JavaScript bundle that matches the installed Mantine major."""

from __future__ import annotations

BUNDLE_V8 = "dash_mantine_datatable.v8.min.js"
BUNDLE_V9 = "dash_mantine_datatable.v9.min.js"
REACT_19 = "19.2.4"


def major_version(version_string: str | None) -> int:
    """Return the numeric major from a version string such as ``3.0.0``."""

    if not version_string:
        return 0

    head = str(version_string).strip().split(".", 1)[0]
    digits: list[str] = []
    for char in head:
        if char.isdigit():
            digits.append(char)
        elif digits:
            break
    return int("".join(digits) or "0")


def bundle_name_for_dmc_version(version_string: str | None) -> str:
    """Return the prebuilt bundle for a dash-mantine-components version."""

    if major_version(version_string) >= 3:
        return BUNDLE_V9
    return BUNDLE_V8


def js_dist_for_dmc_version(version_string: str | None, namespace: str) -> list[dict]:
    """List both bundles, loading only the one that matches ``version_string``."""

    active = bundle_name_for_dmc_version(version_string)
    entries: list[dict] = []
    for bundle in (BUNDLE_V8, BUNDLE_V9):
        entry = {
            "relative_package_path": bundle,
            "namespace": namespace,
        }
        if bundle != active:
            entry["dynamic"] = True
        entries.append(entry)
        entries.append(
            {
                "relative_package_path": f"{bundle}.map",
                "namespace": namespace,
                "dynamic": True,
            }
        )
    return entries


def installed_distribution_version(distribution_name: str) -> str | None:
    """Return an installed distribution version, or ``None`` when it is absent."""

    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:  # pragma: no cover - Python 3.8+ provides importlib.metadata
        return None

    try:
        return version(distribution_name)
    except PackageNotFoundError:
        return None


def _version_pair(version_string: str) -> tuple[int, int]:
    parts = str(version_string).split(".")
    major = major_version(version_string)
    minor_token = parts[1] if len(parts) > 1 else "0"
    minor_digits = "".join(char for char in minor_token if char.isdigit())
    return major, int(minor_digits or "0")


def assert_dash_supports_dmc3(dash_module) -> None:
    """Require Dash 4.5+ and select the React build DMC 3 needs."""

    dash_version = str(getattr(dash_module, "__version__", "0"))
    if _version_pair(dash_version) < (4, 5):
        raise ImportError(
            "dash-mantine-components 3 requires Dash 4.5 or newer and React "
            f"{REACT_19}. Found Dash {dash_version}."
        )

    renderer = getattr(dash_module, "_dash_renderer", None)
    setter = getattr(renderer, "_set_react_version", None)
    if setter is None:
        raise ImportError(
            "This Dash install cannot select React "
            f"{REACT_19}, which dash-mantine-components 3 requires."
        )

    setter(REACT_19)

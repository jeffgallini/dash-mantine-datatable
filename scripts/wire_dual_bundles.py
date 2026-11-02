"""Keep R and Julia bindings pointed at one Mantine bundle after code generation."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "dash_mantine_datatable"
R_METADATA = REPO_ROOT / "R" / "internal.R"
JULIA_MODULE = REPO_ROOT / "src" / "DashMantineDatatable.jl"

LEGACY_BUNDLE_FILES = (
    "dash_mantine_datatable.min.js",
    "dash_mantine_datatable.min.js.map",
    "dash_mantine_datatable.min.js.LICENSE.txt",
)

SCRIPT_PATTERN = re.compile(r"script = '([^']+)'")
JULIA_BUNDLE_START = "# DUAL_MANTINE_BUNDLE_START"
JULIA_BUNDLE_END = "# DUAL_MANTINE_BUNDLE_END"
JULIA_SNIPPET = f"""{JULIA_BUNDLE_START}
    function _datatable_bundle()
        major = 2
        for (_, dep) in Pkg.dependencies()
            if dep.name == "DashMantineComponents" && dep.version !== nothing
                major = dep.version.major
            end
        end
        return major >= 3 ? "dash_mantine_datatable.v9.min.js" : "dash_mantine_datatable.v8.min.js"
    end
    bundle = _datatable_bundle()
{JULIA_BUNDLE_END}"""


def _remove_legacy_bundles() -> None:
    versioned = (
        PACKAGE_DIR / "dash_mantine_datatable.v8.min.js",
        PACKAGE_DIR / "dash_mantine_datatable.v9.min.js",
    )
    if not all(path.exists() for path in versioned):
        return

    for name in LEGACY_BUNDLE_FILES:
        path = PACKAGE_DIR / name
        if path.exists():
            path.unlink()


def _preserved_scripts(source: str) -> list[str]:
    preserved: list[str] = []
    for script in SCRIPT_PATTERN.findall(source):
        if "dash_mantine_datatable.v8.min" in script or "dash_mantine_datatable.v9.min" in script:
            continue
        if script in {
            "dash_mantine_datatable.min.js",
            "dash_mantine_datatable.min.js.map",
        }:
            continue
        if script not in preserved:
            preserved.append(script)
    return preserved


def _r_dependency(script: str, *, dynamic: bool = False, async_script: bool = False) -> str:
    if async_script:
        extra = "all_files = FALSE, async = TRUE"
    elif dynamic:
        extra = "all_files = FALSE, dynamic = TRUE"
    else:
        extra = "all_files = FALSE"
    return (
        '`dash_mantine_datatable` = structure(list(name = "dash_mantine_datatable",\n'
        'version = "0.1.0", src = list(href = NULL,\n'
        'file = "deps"), meta = NULL,\n'
        f"script = {script},\n"
        'stylesheet = NULL, head = NULL, attachment = NULL, package = "dashMantineDatatable",\n'
        f"{extra}), class = \"html_dependency\")"
    )


def _render_r(extra_scripts: list[str]) -> str:
    dependencies = [
        _r_dependency(
            f"'{script}'",
            dynamic=script.endswith(".map"),
            async_script=script.startswith("async-") and not script.endswith(".map"),
        )
        for script in extra_scripts
    ]
    dependencies.append(_r_dependency(".dashMantineDatatableBundle()"))
    dependencies.append(
        _r_dependency("paste0(.dashMantineDatatableBundle(), '.map')", dynamic=True)
    )
    rendered = ",\n".join(dependencies)
    return f"""# Bundle selection is reapplied by scripts/wire_dual_bundles.py after dash-generate-components.
.dashMantineDatatableBundle <- function() {{
  candidates <- c("dashMantineComponents")
  for (name in candidates) {{
    version <- tryCatch(
      as.character(utils::packageVersion(name)),
      error = function(...) NA_character_
    )
    if (!is.na(version)) {{
      major <- suppressWarnings(as.integer(strsplit(version, ".", fixed = TRUE)[[1]][[1]]))
      if (!is.na(major) && major >= 3) {{
        return("dash_mantine_datatable.v9.min.js")
      }}
      return("dash_mantine_datatable.v8.min.js")
    }}
  }}
  "dash_mantine_datatable.v8.min.js"
}}

.dashMantineDatatable_js_metadata <- function() {{
deps_metadata <- list({rendered})
return(deps_metadata)
}}
"""


def _rewrite_r() -> None:
    source = R_METADATA.read_text(encoding="utf-8") if R_METADATA.exists() else ""
    R_METADATA.write_text(_render_r(_preserved_scripts(source)), encoding="utf-8")


def _rewrite_julia() -> None:
    source = JULIA_MODULE.read_text(encoding="utf-8")
    if "using Pkg" not in source:
        source = source.replace("using Dash\n", "using Dash\nusing Pkg\n", 1)

    if JULIA_BUNDLE_START in source and JULIA_BUNDLE_END in source:
        source = re.sub(
            rf"{re.escape(JULIA_BUNDLE_START)}.*?{re.escape(JULIA_BUNDLE_END)}",
            JULIA_SNIPPET.strip("\n"),
            source,
            count=1,
            flags=re.DOTALL,
        )
    else:
        source = source.replace(
            "function __init__()\n",
            "function __init__()\n" + JULIA_SNIPPET + "\n",
            1,
        )

    source = source.replace(
        'relative_package_path = "dash_mantine_datatable.min.js",',
        "relative_package_path = bundle,",
    )
    source = source.replace(
        'relative_package_path = "dash_mantine_datatable.min.js.map",',
        'relative_package_path = bundle * ".map",',
    )
    source = re.sub(
        r'relative_package_path = "dash_mantine_datatable\.v[89]\.min\.js",',
        "relative_package_path = bundle,",
        source,
    )
    source = re.sub(
        r'relative_package_path = "dash_mantine_datatable\.v[89]\.min\.js\.map",',
        'relative_package_path = bundle * ".map",',
        source,
    )
    JULIA_MODULE.write_text(source, encoding="utf-8")


def main() -> None:
    _remove_legacy_bundles()
    _rewrite_r()
    _rewrite_julia()


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

from release_helpers import REPO_ROOT, ensure_consistent_versions


ARTIFACT_PATHS = (
    "build",
    "dist",
    "dash_mantine_datatable.egg-info",
    ".release-tmp",
)

SDIST_REQUIRED_PATHS = {
    "README.md",
    "LICENSE",
    "dash_mantine_datatable/metadata.json",
    "dash_mantine_datatable/package-info.json",
    "dash_mantine_datatable/dash_mantine_datatable.min.js",
}

WHEEL_REQUIRED_PATHS = {
    "dash_mantine_datatable/metadata.json",
    "dash_mantine_datatable/package-info.json",
    "dash_mantine_datatable/dash_mantine_datatable.min.js",
}


def _remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _run(command: list[str], *, env: dict[str, str]) -> None:
    resolved_executable = shutil.which(command[0]) or command[0]
    resolved_command = [resolved_executable, *command[1:]]
    print(f"+ {' '.join(command)}")
    subprocess.run(resolved_command, check=True, cwd=REPO_ROOT, env=env)


def _verify_artifacts(dist_dir: Path) -> None:
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    wheels = sorted(dist_dir.glob("*.whl"))

    if len(sdists) != 1:
        raise RuntimeError(f"Expected exactly one sdist in '{dist_dir}', found {len(sdists)}.")
    if len(wheels) != 1:
        raise RuntimeError(f"Expected exactly one wheel in '{dist_dir}', found {len(wheels)}.")

    sdist_path = sdists[0]
    wheel_path = wheels[0]
    package_root = f"{sdist_path.name[:-7]}/"

    with tarfile.open(sdist_path) as sdist:
        sdist_names = set(sdist.getnames())
        missing_sdist = sorted(
            package_root + required
            for required in SDIST_REQUIRED_PATHS
            if package_root + required not in sdist_names
        )
        if missing_sdist:
            raise RuntimeError(f"Missing from sdist: {missing_sdist}")

        license_member = sdist.extractfile(package_root + "LICENSE")
        license_text = ""
        if license_member is not None:
            license_text = license_member.read().decode("utf-8").strip()
        if not license_text:
            raise RuntimeError("LICENSE is empty in the source distribution.")

    with zipfile.ZipFile(wheel_path) as wheel:
        wheel_names = set(wheel.namelist())
        missing_wheel = sorted(
            required for required in WHEEL_REQUIRED_PATHS if required not in wheel_names
        )
        if missing_wheel:
            raise RuntimeError(f"Missing from wheel: {missing_wheel}")

    print(f"Release artifacts verified: {sdist_path.name}, {wheel_path.name}")


def main() -> int:
    ensure_consistent_versions()

    for artifact_path in ARTIFACT_PATHS:
        _remove_path(REPO_ROOT / artifact_path)

    temp_root = REPO_ROOT / ".release-tmp"
    temp_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["TMP"] = str(temp_root)
    env["TEMP"] = str(temp_root)
    env["TMPDIR"] = str(temp_root)

    python = sys.executable

    _run(["npm", "run", "build"], env=env)
    _run([python, "-m", "pytest"], env=env)
    _run([python, "-m", "build"], env=env)

    dist_dir = REPO_ROOT / "dist"
    dist_artifacts = sorted(str(path) for path in dist_dir.iterdir() if path.is_file())
    if not dist_artifacts:
        raise RuntimeError("No distribution artifacts were created in 'dist'.")

    _run([python, "-m", "twine", "check", *dist_artifacts], env=env)
    _verify_artifacts(dist_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

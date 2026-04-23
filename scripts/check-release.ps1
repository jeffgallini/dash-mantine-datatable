Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\\venv\\Scripts\\python.exe"

if (-not (Test-Path $python)) {
    throw "Expected release environment at '$python'. Create the venv and install the release dependencies first."
}

& $python (Join-Path $PSScriptRoot "check_release.py")
if ($LASTEXITCODE -ne 0) {
    throw "Release check failed with exit code $LASTEXITCODE."
}

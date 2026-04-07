Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\\venv\\Scripts\\python.exe"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$tempRoot = Join-Path $repoRoot ".release-tmp"

if (-not (Test-Path $python)) {
    throw "Expected release environment at '$python'. Create the venv and install the release dependencies first."
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE."
    }
}

Set-Location $repoRoot

$artifactPaths = @(
    "build",
    "dist",
    "dash_mantine_datatable.egg-info",
    ".release-tmp"
)

foreach ($path in $artifactPaths) {
    if (Test-Path $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}

New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
$env:TMP = $tempRoot
$env:TEMP = $tempRoot

Invoke-NativeCommand -FilePath "npm" -ArgumentList @("run", "build") -Label "npm run build"
Invoke-NativeCommand -FilePath $python -ArgumentList @("-m", "pytest") -Label "python -m pytest"
Invoke-NativeCommand -FilePath $python -ArgumentList @("-m", "build") -Label "python -m build"

$distArtifacts = Get-ChildItem -LiteralPath "dist" | ForEach-Object { $_.FullName }
Invoke-NativeCommand -FilePath $python -ArgumentList (@("-m", "twine", "check") + $distArtifacts) -Label "python -m twine check"
Invoke-NativeCommand -FilePath $python -ArgumentList @(
    "-c",
    "import pathlib, tarfile, zipfile; required = {'README.md', 'LICENSE', 'dash_mantine_datatable/metadata.json', 'dash_mantine_datatable/package-info.json', 'dash_mantine_datatable/dash_mantine_datatable.min.js'}; dist = pathlib.Path('dist'); sdist = next(dist.glob('*.tar.gz')); wheel = next(dist.glob('*.whl')); package_root = sdist.name[:-7] + '/'; sdist_names = set(tarfile.open(sdist).getnames()); wheel_names = set(zipfile.ZipFile(wheel).namelist()); missing_sdist = sorted(package_root + name for name in required if package_root + name not in sdist_names); missing_wheel = sorted(name for name in required if name not in wheel_names and not name.startswith(('README.md', 'LICENSE'))); license_text = tarfile.open(sdist).extractfile(package_root + 'LICENSE').read().decode('utf-8').strip(); assert not missing_sdist, f'Missing from sdist: {missing_sdist}'; assert not missing_wheel, f'Missing from wheel: {missing_wheel}'; assert license_text, 'LICENSE is empty in sdist'; print(f'Release artifacts verified: {sdist.name}, {wheel.name}');"
) -Label "artifact inspection"

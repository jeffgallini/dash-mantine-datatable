# Contributing

## Local setup

```powershell
npm install --legacy-peer-deps
python -m pip install -r requirements.txt -r tests/requirements.txt
```

## Common tasks

```powershell
npm run build:js
npm run build:backends
python -m pytest
python usage.py
```

## Branch workflow

- Create feature branches from `staging`.
- Open contributor pull requests into `staging`.
- When `staging` is ready to ship, open a release pull request from `staging`
  into `main`.

## Release preparation

Before opening the `staging -> main` release PR:

- Add release notes under `## Unreleased` in `CHANGELOG.md`.
- Decide the next version and put it in the PR title as
  `vX.Y.Z Release - Summary`.
- Run the release check locally if you want a preflight build/test/package
  pass.

```powershell
.\scripts\check-release.ps1
```

```bash
python scripts/check_release.py
```

## Automated publishing

Release pull requests into `main` must come from `staging` and must be titled
`vX.Y.Z Release`, optionally followed by ` - Summary`.

The `Release PR Guard` workflow checks that:

- the PR is `staging -> main`
- the title format is valid
- the requested version is newer than the current package version

After a valid release PR is merged, `.github/workflows/publish-release.yml`
will:

- write the requested release version into the package metadata files
- convert `CHANGELOG.md` into the final versioned release notes
- commit those release metadata updates back to `main`
- rebuild, test, publish to PyPI, and create or update the GitHub release

## One-time maintainer setup

- Create the `staging` branch on GitHub.
- Protect `main` and require the `Release PR Guard` check.
- Add a `PYPI_API_TOKEN` secret to the `pypi` environment.


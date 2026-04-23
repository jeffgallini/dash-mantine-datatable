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

- Bump the version in `package.json`, `package-lock.json`,
  `dash_mantine_datatable/package-info.json`, and `Project.toml`.
- Add a matching `CHANGELOG.md` section whose heading starts with
  `## X.Y.Z - YYYY-MM-DD`.
- Run the release check locally.

```powershell
.\scripts\check-release.ps1
```

```bash
python scripts/check_release.py
```

## Automated publishing

Release pull requests into `main` must be titled `vX.Y.Z Release` and may add
extra descriptive text after that prefix. The `Release PR Guard` workflow
rejects any PR to `main` that is not `staging -> main`, does not use the
required title format, or has mismatched version/changelog metadata.

After a valid release PR is merged, `.github/workflows/publish-release.yml`
will rebuild the package, run the tests, publish `dist/*` to PyPI, and create
or update a GitHub release tagged `vX.Y.Z` using the matching
`CHANGELOG.md` section as the release notes.

## One-time maintainer setup

- Create the `staging` branch on GitHub.
- Protect `main` and require the `Release PR Guard` check.
- Add a `PYPI_API_TOKEN` secret to the `pypi` environment.


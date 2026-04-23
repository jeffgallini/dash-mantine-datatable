# Changelog

## Unreleased

- Added GitHub Actions to validate `staging -> main` release pull requests and
  publish releases to PyPI and GitHub after merge.
- Made the release pull request title the source of truth for the next package
  version, with automated version stamping and changelog promotion during the
  publish workflow.
- Documented the staging-based release flow and the local release preflight
  steps for contributors and maintainers.

## 0.1.0 - 2026-04-07

- Initial public release of `dash-mantine-datatable` for Dash applications.
- Added the generated Python, R, and Julia package metadata for the first
  publishable component package.
- Included the bundled JavaScript assets, package metadata, and release
  documentation needed for TestPyPI and PyPI publishing.

# Changelog

## Unreleased

## 1.0.0 - 2026-09-03

### Added

- Great Docs site with user guide, recipes, and API reference, published to GitHub Pages.
- Recipe generator (`scripts/generate_recipes.py`) that keeps docs examples aligned with `usage.py`.
- Documentation media capture helper for README and recipe screenshots.
- Restored GitHub Actions for docs deployment, release PR validation, and PyPI publishing.

### Changed

- README refreshed with docs link, badges, feature overview, and example media.
- GitHub Pages docs workflow now builds the Quarto Great Docs site instead of pdoc-only output.

### Fixed

- Dash template rendering for grouped hierarchy cells and expansion chevrons.
- Filter popover dismissal for MultiSelect, Select, DateInput, and Autocomplete controls.
- Array-valued cell display formatting for filter and presentation columns.
- Table min-height row stretch behavior in fixed-height layouts.
- Inline editor and filter `setProps` synchronization for Dash Mantine controls.

## 0.1.0 - 2026-04-07

- Initial public release of `dash-mantine-datatable` for Dash applications.
- Added the generated Python, R, and Julia package metadata for the first
  publishable component package.
- Included the bundled JavaScript assets, package metadata, and release
  documentation needed for TestPyPI and PyPI publishing.

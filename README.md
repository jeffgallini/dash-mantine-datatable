# dash-mantine-datatable

`dash-mantine-datatable` is a Dash wrapper around Mantine DataTable with a
Dash-friendly API, Mantine style props, and chainable Python helpers for
columns, grouping, rows, selection, pagination, sorting, and search.

## Install

```bash
pip install dash-mantine-datatable
```

## Quick Start

```python
from dash import Dash
import dash_mantine_components as dmc
import dash_mantine_datatable as dmdt

app = Dash()

app.layout = dmc.MantineProvider(
    dmdt.DataTable(
        id="employees",
        data=[
            {"id": 1, "name": "Avery Stone", "team": "Platform", "status": "On Track"},
            {"id": 2, "name": "Mina Patel", "team": "Growth", "status": "Planning"},
        ],
        columns=[
            {"accessor": "name", "sortable": True},
            {"accessor": "team", "sortable": True},
            {"accessor": "status", "presentation": "badge"},
        ],
    ).update_layout(radius="lg", withTableBorder=True, striped=True)
)

if __name__ == "__main__":
    app.run(debug=True)
```

## Highlights

- Mantine-flavored Dash props such as `radius`, `bg`, `classNames`, `styles`, `bd`, and `bdrs`
- Chainable helpers including `update_layout()`, `update_table_properties()`, `update_columns()`, `group_columns()`, `update_rows()`, `update_selection()`, `update_pagination()`, `update_sorting()`, and `update_search()`
- Dash-safe component templates for column filters, empty states, custom loaders, row expansion content, and sort icons
- Support for grouped headers, nested rows, row dragging, server-side pagination, and selector-based row styling rules
- Multi-language Dash component assets for Python, R, and Julia generated from the same source tree

## Helper Example

```python
table = (
    dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "salary": 128000, "status": "On Track"}],
        columns=[
            dmdt.Column("name"),
            dmdt.Column("salary", textAlign="right", presentation="currency", currency="USD"),
            dmdt.Column("status", presentation="badge"),
        ],
    )
    .update_columns(selector="name", title="Employee")
    .update_rows(selector={"status": "On Track"}, className="row-ok")
    .update_selection(selectionTrigger="checkbox")
    .update_pagination(recordsPerPage=10)
)
```

## Local Development

```bash
npm install --legacy-peer-deps
python -m pip install -r requirements.txt -r tests/requirements.txt
npm run build
python -m pytest
python usage.py
```

## Publishing

```powershell
.\scripts\check-release.ps1
python -m twine upload --repository testpypi dist/*
```

Smoke-test the TestPyPI release in a fresh virtual environment before uploading
the same artifact set to PyPI. The release check rebuilds the JavaScript bundle,
runs the test suite, builds the sdist and wheel, and verifies that the release
artifacts include the bundled JS assets, `metadata.json`, `package-info.json`,
`README.md`, and `LICENSE`.

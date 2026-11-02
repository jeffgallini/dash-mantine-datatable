from contextlib import suppress

import dash
import dash_mantine_components as dmc
import dash_mantine_datatable as dmdt
import pytest
from dash import Dash, Input, Output, html
from dash_mantine_datatable._mantine_support import (
    BUNDLE_V8,
    BUNDLE_V9,
    assert_dash_supports_dmc3,
    bundle_name_for_dmc_version,
    major_version,
)
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException


def _chrome_webdriver_ready():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    try:
        driver = webdriver.Chrome(options=options)
    except SessionNotCreatedException as exc:
        message = str(exc).splitlines()[0]
        return False, f"Skipping browser smoke test: {message}"
    except WebDriverException as exc:
        message = str(exc).splitlines()[0]
        return False, f"Skipping browser smoke test: {message}"

    with suppress(Exception):
        driver.quit()

    return True, ""


_WEBDRIVER_READY, _WEBDRIVER_REASON = _chrome_webdriver_ready()
pytestmark = pytest.mark.skipif(not _WEBDRIVER_READY, reason=_WEBDRIVER_REASON)


def _browser_app():
    """Small page for the browser smoke test.

    Importing usage.py builds the full docs site. On GitHub that layout is
    still downloading when the smoke test's wait expires, for both DMC 2 and
    DMC 3.
    """

    if major_version(getattr(dmc, "__version__", None)) >= 3:
        assert_dash_supports_dmc3(dash)

    records = [
        {
            "id": 1,
            "name": "Avery Stone",
            "team": "Platform",
            "bio": "Owns the deployment pipeline and release tooling.",
        },
        {
            "id": 2,
            "name": "Mina Patel",
            "team": "Growth",
            "bio": "Leads onboarding and activation UX work.",
        },
        {
            "id": 3,
            "name": "Jonah Kim",
            "team": "Platform",
            "bio": "Keeps the warehouse and metrics pipeline healthy.",
        },
    ]
    columns = [
        {"accessor": "name", "title": "Name"},
        {"accessor": "team", "title": "Team"},
    ]
    app = Dash(__name__)
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                dmdt.DataTable(
                    id="overview-table",
                    data=records,
                    columns=columns,
                    paginationMode="none",
                ),
                dmdt.DataTable(
                    id="selection-table",
                    data=records,
                    columns=columns,
                    selectionTrigger="checkbox",
                    selectedRecordIds=[1, 3],
                    paginationMode="none",
                ),
                dmc.Code(
                    id="selection-output",
                    block=True,
                    children="Selected record ids: [1, 3]",
                ),
                dmdt.DataTable(
                    id="expanding-rows-table",
                    data=records,
                    columns=columns,
                    paginationMode="none",
                ).update_rows(
                    expandedRecordIds=[1],
                    rowExpansion=dmdt.RowExpansionConfig(
                        dmc.Text("{bio}"),
                        allowMultiple=True,
                    ),
                ),
                dmdt.DataTable(
                    id="column-filtering-table",
                    data=records,
                    columns=columns,
                    filterMode="client",
                    paginationMode="none",
                ).update_columns(
                    selector="name",
                    filter=dmc.TextInput(
                        id="column-name-filter",
                        placeholder="Search employees...",
                        value="",
                    ),
                ),
            ]
        )
    )

    @app.callback(
        Output("selection-output", "children"),
        Input("selection-table", "selectedRecordIds"),
    )
    def show_selected_rows(selected_ids):
        return f"Selected record ids: {selected_ids or []}"

    return app


def test_render_component(dash_duo):
    dash_duo.start_server(_browser_app())
    dash_duo.wait_timeout = 30

    dash_duo.wait_for_text_to_equal(
        '#selection-output', 'Selected record ids: [1, 3]'
    )

    overview_table = dash_duo.find_element('#overview-table')
    assert overview_table is not None

    sources = dash_duo.driver.execute_script(
        "return Array.from(document.querySelectorAll('script[src]')).map(node => node.src);"
    )
    active = bundle_name_for_dmc_version(getattr(dmc, "__version__", None))
    inactive = BUNDLE_V9 if active == BUNDLE_V8 else BUNDLE_V8
    assert any(active in source for source in sources)
    assert all(inactive not in source for source in sources)

    dash_duo.wait_for_contains_text(
        "#expanding-rows-table",
        "Owns the deployment pipeline and release tooling.",
    )

    filter_icon = dash_duo.find_element(
        "#column-filtering-table .mantine-datatable-header-cell-filter-action-icon"
    )
    dash_duo.driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        filter_icon,
    )
    filter_icon.click()
    dash_duo.wait_for_element("#column-name-filter")

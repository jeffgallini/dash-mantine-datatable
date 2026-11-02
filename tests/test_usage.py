from contextlib import suppress

import dash_mantine_components as dmc
import pytest
from dash.testing.application_runners import import_app
from dash_mantine_datatable._mantine_support import (
    BUNDLE_V8,
    BUNDLE_V9,
    bundle_name_for_dmc_version,
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


def test_render_component(dash_duo):
    app = import_app('usage')
    dash_duo.start_server(app)

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

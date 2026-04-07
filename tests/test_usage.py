from contextlib import suppress

import pytest
from dash.testing.application_runners import import_app
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

from dash_mantine_datatable._mantine_support import (
    BUNDLE_V8,
    BUNDLE_V9,
    REACT_19,
    assert_dash_supports_dmc3,
    bundle_name_for_dmc_version,
    js_dist_for_dmc_version,
    major_version,
)


def test_bundle_follows_dash_mantine_components_major():
    assert bundle_name_for_dmc_version("2.6.0") == BUNDLE_V8
    assert bundle_name_for_dmc_version("2.99.0") == BUNDLE_V8
    assert bundle_name_for_dmc_version("3.0.0") == BUNDLE_V9
    assert bundle_name_for_dmc_version(None) == BUNDLE_V8


def test_only_the_matching_bundle_is_loaded():
    dist = js_dist_for_dmc_version("3.0.0", "dash_mantine_datatable")
    loaded = [
        item["relative_package_path"]
        for item in dist
        if not item.get("dynamic")
    ]

    assert loaded == [BUNDLE_V9]
    assert any(item["relative_package_path"] == BUNDLE_V8 and item.get("dynamic") for item in dist)


def test_dmc3_requires_dash_45_and_react_19():
    class OldDash:
        __version__ = "4.4.0"

    try:
        assert_dash_supports_dmc3(OldDash)
    except ImportError as exc:
        assert "4.5" in str(exc)
    else:
        raise AssertionError("Dash 4.4 should be rejected for dash-mantine-components 3.")

    class CurrentDash:
        __version__ = "4.5.0"

        class _dash_renderer:
            selected = None

            @classmethod
            def _set_react_version(cls, version):
                cls.selected = version

    assert_dash_supports_dmc3(CurrentDash)
    assert CurrentDash._dash_renderer.selected == REACT_19
    assert major_version("19.2.4") == 19

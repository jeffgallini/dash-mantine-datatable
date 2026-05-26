def test_column_filtering_demo_uses_internal_client_filters():
    import usage

    table = usage.make_column_filtering_demo_table()

    assert table.filterMode == "client"
    assert len(table.data) == len(usage.EMPLOYEES)
    assert [column.get("accessor") for column in table.columns if "filter" in column] == [
        "name",
        "team",
        "startDate",
        "deliveryScore",
        "status",
    ]
    assert not any("filtering" in column for column in table.columns)
    assert not any(
        "column-filtering-table.data" in str(output)
        for output in usage.app.callback_map
    )

import dash_mantine_components as dmc
import dash_mantine_datatable as dmdt
from dash import html


def test_update_layout_and_table_properties():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery"}],
        columns=[
            {"accessor": "name", "titleStyle": {"color": "blue"}},
            {"accessor": "salary"},
        ],
    )

    updated = (
        table.update_layout(
            style={"border": "1px solid red"},
            tableProps={"stickyHeader": True},
            storeColumnsKey="employees-columns",
            dir="rtl",
        )
        .update_columns(
            {"accessor": "salary", "title": "Salary", "width": 120},
        )
        .update_columns(
            selector="name",
            title="Full name",
            cellsStyle={"fontStyle": "italic"},
            titleStyle={"fontWeight": 700},
            footer="Primary column",
        )
        .update_layout(
            style={"padding": "1rem"},
            tableProps={"layout": "fixed"},
        )
        .update_table_properties(
            withRowBorders=False,
            horizontalSpacing="lg",
            verticalSpacing="sm",
            fontSize="md",
            borderRadius="xl",
            verticalAlign="top",
        )
    )

    props = updated.to_plotly_json()["props"]

    assert updated is table
    assert props["style"] == {"border": "1px solid red", "padding": "1rem"}
    assert props["tableProps"] == {"stickyHeader": True, "layout": "fixed"}
    assert props["storeColumnsKey"] == "employees-columns"
    assert props["direction"] == "rtl"
    assert props["columns"][0]["title"] == "Full name"
    assert props["columns"][0]["cellsStyle"] == {"fontStyle": "italic"}
    assert props["columns"][0]["titleStyle"] == {
        "color": "blue",
        "fontWeight": 700,
    }
    assert props["columns"][0]["footer"] == "Primary column"
    assert props["columns"][1]["title"] == "Salary"
    assert props["columns"][1]["width"] == 120
    assert props["withRowBorders"] is False
    assert props["horizontalSpacing"] == "lg"
    assert props["verticalSpacing"] == "sm"
    assert props["fz"] == "md"
    assert props["borderRadius"] == "xl"
    assert props["verticalAlign"] == "top"


def test_update_layout_supports_direction_prop():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery"}],
        columns=[{"accessor": "name"}],
    ).update_layout(direction="rtl")

    props = table.to_plotly_json()["props"]

    assert props["direction"] == "rtl"


def test_constructor_and_update_layout_support_grouping_aliases():
    table = dmdt.DataTable(
        data=[{"id": 1, "team": "Platform", "location": "Berlin"}],
        columns=[{"accessor": "team"}, {"accessor": "location"}],
        group_by=["team"],
        child_rows_accessor="childrenData",
        group_aggregations={"location": "count"},
    ).update_layout(
        group_by=["team", "location"],
        child_rows_accessor="nestedRows",
        group_aggregations={"location": {"fn": "count", "accessor": "id"}},
    )

    props = table.to_plotly_json()["props"]

    assert props["groupBy"] == ["team", "location"]
    assert props["childRowsAccessor"] == "nestedRows"
    assert props["groupAggregations"] == {
        "location": {"fn": "count", "accessor": "id"}
    }


def test_update_columns_overwrite_replaces_selected_columns():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "salary": 128000, "location": "Berlin"}],
        columns=[
            {"accessor": "name", "width": 180, "cellsStyle": {"fontWeight": 600}},
            {"accessor": "salary", "textAlign": "right", "width": 140},
            {"accessor": "location", "hidden": False},
        ],
    )

    updated = (
        table.update_columns(
            selector=["salary", "location"],
            hidden=True,
        ).update_columns(
            {"accessor": "salary", "title": "Annual salary"},
            overwrite=True,
        )
    )

    props = updated.to_plotly_json()["props"]

    assert props["columns"][0] == {
        "accessor": "name",
        "width": 180,
        "cellsStyle": {"fontWeight": 600},
    }
    assert props["columns"][1] == {
        "accessor": "salary",
        "title": "Annual salary",
    }
    assert props["columns"][2] == {
        "accessor": "location",
        "hidden": True,
    }


def test_update_columns_supports_column_customization_flags():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "team": "Platform", "location": "Berlin"}],
        columns=[
            {"accessor": "name", "title": "Employee"},
            {"accessor": "team"},
            {"accessor": "location"},
        ],
    ).update_columns(
        selector=["name", "team", "location"],
        draggable=True,
        toggleable=True,
    ).update_columns(
        selector=["name", "team"],
        resizable=True,
    ).update_columns(
        selector="location",
        defaultToggle=False,
    )

    props = table.to_plotly_json()["props"]

    assert props["columns"][0]["draggable"] is True
    assert props["columns"][0]["toggleable"] is True
    assert props["columns"][0]["resizable"] is True
    assert props["columns"][1]["draggable"] is True
    assert props["columns"][1]["toggleable"] is True
    assert props["columns"][1]["resizable"] is True
    assert props["columns"][2]["draggable"] is True
    assert props["columns"][2]["toggleable"] is True
    assert props["columns"][2]["defaultToggle"] is False


def test_update_columns_supports_dmc_filter_components():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "team": "Platform"}],
        columns=[
            {"accessor": "name"},
            {"accessor": "team"},
        ],
    ).update_columns(
        selector="name",
        filter=dmc.TextInput(
            id="name-filter",
            label="Employee",
            value="Avery",
        ),
        filtering=True,
        filterPopoverProps={"width": 280},
    ).update_columns(
        selector="team",
        filter=dmc.MultiSelect(
            id="team-filter",
            data=["Platform", "Growth"],
            value=["Platform"],
            comboboxProps={"withinPortal": False},
        ),
    ).update_layout(
        defaultColumnProps=dmdt.Column(
            filter=dmc.TextInput(
                id="default-filter",
                label="Default filter",
            )
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["columns"][0]["filtering"] is True
    assert props["columns"][0]["filterPopoverProps"] == {"width": 280}
    assert props["columns"][0]["filter"].to_plotly_json()["props"]["id"] == "name-filter"
    assert props["columns"][1]["filter"].to_plotly_json()["props"]["id"] == "team-filter"
    assert (
        props["defaultColumnProps"]["filter"].to_plotly_json()["props"]["id"]
        == "default-filter"
    )
    assert "columns[].filter" in dmdt.DataTable._children_props
    assert "defaultColumnProps.filter" in dmdt.DataTable._children_props


def test_group_columns_builds_groups_from_existing_columns():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "role": "Engineer", "salary": 128000}],
        columns=[
            {"accessor": "name", "title": "Employee"},
            {"accessor": "role"},
            {"accessor": "salary", "textAlign": "right"},
        ],
    )

    updated = table.group_columns(
        {
            "id": "profile",
            "title": "Profile",
            "style": {"fontStyle": "italic"},
            "columns": ["name", "role"],
        },
        {
            "id": "compensation",
            "columns": [
                {"accessor": "salary", "title": "Annual salary", "width": 140}
            ],
        },
    )

    props = updated.to_plotly_json()["props"]

    assert updated is table
    assert props["groups"][0]["title"] == "Profile"
    assert props["groups"][0]["style"] == {"fontStyle": "italic"}
    assert props["groups"][0]["columns"][0] == {
        "accessor": "name",
        "title": "Employee",
    }
    assert props["groups"][1]["columns"][0] == {
        "accessor": "salary",
        "textAlign": "right",
        "title": "Annual salary",
        "width": 140,
    }


def test_group_columns_updates_selected_groups():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "salary": 128000, "status": "On Track"}],
        columns=[
            {"accessor": "name"},
            {"accessor": "salary"},
            {"accessor": "status"},
        ],
        groups=[
            {
                "id": "overview",
                "title": "Overview",
                "columns": ["name", "status"],
            },
            {
                "id": "compensation",
                "columns": ["salary"],
            },
        ],
    )

    updated = (
        table.group_columns(
            selector=["overview", "results"],
            style={"color": "blue"},
        ).group_columns(
            selector="compensation",
            title="Compensation",
            columns=[{"accessor": "salary", "textAlign": "right"}],
        )
    )

    props = updated.to_plotly_json()["props"]

    assert props["groups"][0]["style"] == {"color": "blue"}
    assert props["groups"][1]["title"] == "Compensation"
    assert props["groups"][1]["columns"][0] == {
        "accessor": "salary",
        "textAlign": "right",
    }


def test_group_columns_supports_nested_groups():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "salary": 128000}],
        columns=[{"accessor": "name"}, {"accessor": "salary"}],
    ).group_columns(
        dmdt.ColumnGroup(
            "outer",
            groups=[
                dmdt.ColumnGroup("identity", columns=["name"]),
                dmdt.ColumnGroup("comp", columns=["salary"]),
            ],
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["groups"][0]["id"] == "outer"
    assert props["groups"][0]["groups"][0]["id"] == "identity"
    assert props["groups"][0]["groups"][0]["columns"] == [{"accessor": "name"}]
    assert props["groups"][0]["groups"][1]["columns"] == [{"accessor": "salary"}]


def test_column_helper_and_default_column_render_are_dash_safe():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "status": "On Track"}],
        columns=[
            dmdt.Column("name"),
            dmdt.Column("status"),
        ],
    ).update_layout(
        defaultColumnProps=dmdt.Column(textAlign="right", ellipsis=True),
        defaultColumnRender=html.Span("{name}", id={"type": "cell", "id": "{id}"}),
    )

    props = table.to_plotly_json()["props"]

    assert props["columns"][0] == {"accessor": "name"}
    assert props["defaultColumnProps"] == {"textAlign": "right", "ellipsis": True}
    assert (
        props["defaultColumnRender"].to_plotly_json()["props"]["children"] == "{name}"
    )
    assert (
        props["defaultColumnRender"].to_plotly_json()["props"]["id"]
        == {"type": "cell", "id": "{id}"}
    )
    assert "columns[].render" in dmdt.DataTable._children_props
    assert "defaultColumnRender" in dmdt.DataTable._children_props


def test_empty_state_supports_top_level_dash_components():
    table = dmdt.DataTable(
        data=[],
        columns=[{"accessor": "name"}],
        paginationMode="none",
        emptyState=html.Div("Nothing here", id="empty-shell"),
    )

    props = table.to_plotly_json()["props"]

    assert props["emptyState"].to_plotly_json()["props"]["children"] == "Nothing here"
    assert props["emptyState"].to_plotly_json()["props"]["id"] == "empty-shell"
    assert "emptyState" in dmdt.DataTable._children_props
    assert "emptyState" in dmdt.DataTable._base_nodes


def test_custom_loader_no_records_icon_and_sort_icons_are_dash_safe():
    table = dmdt.DataTable(
        data=[],
        columns=[{"accessor": "name"}],
        customLoader=html.Div("Loading", id="loader-shell"),
        noRecordsIcon=html.Div("Empty", id="empty-icon-shell"),
        sortIcons={
            "sorted": html.Span("Sorted", id="sorted-icon"),
            "unsorted": html.Span("Unsorted", id="unsorted-icon"),
        },
    )

    props = table.to_plotly_json()["props"]

    assert props["customLoader"].to_plotly_json()["props"]["id"] == "loader-shell"
    assert props["noRecordsIcon"].to_plotly_json()["props"]["id"] == "empty-icon-shell"
    assert props["sortIcons"]["sorted"].to_plotly_json()["props"]["id"] == "sorted-icon"
    assert (
        props["sortIcons"]["unsorted"].to_plotly_json()["props"]["id"]
        == "unsorted-icon"
    )
    assert "customLoader" in dmdt.DataTable._children_props
    assert "customLoader" in dmdt.DataTable._base_nodes
    assert "noRecordsIcon" in dmdt.DataTable._children_props
    assert "noRecordsIcon" in dmdt.DataTable._base_nodes
    assert "sortIcons.sorted" in dmdt.DataTable._children_props
    assert "sortIcons.unsorted" in dmdt.DataTable._children_props


def test_update_rows_supports_conditional_rules_and_composite_ids():
    table = (
        dmdt.DataTable(
            data=[
                {"bookTitle": "The Fellowship of the Ring", "character": "Frodo"},
                {"bookTitle": "The Two Towers", "character": "Samwise"},
            ],
            columns=[
                {"accessor": "character"},
                {"accessor": "bookTitle"},
            ],
            paginationMode="none",
        )
        .update_rows(
            idAccessor=("bookTitle", "character"),
            color="dimmed",
        )
        .update_rows(
            selector={"bookTitle": "The Fellowship of the Ring"},
            backgroundColor={"light": "#f0f7f1", "dark": "#232b25"},
            className="ring-bearer",
        )
        .update_rows(
            selector={"character": "Samwise"},
            style={"fontStyle": "italic", "fontWeight": 700},
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["idAccessor"] == {
        "accessors": ["bookTitle", "character"],
    }
    assert props["rowColor"] == "dimmed"
    assert props["rowBackgroundColor"] == [
        {
            "selector": {"bookTitle": "The Fellowship of the Ring"},
            "value": {"light": "#f0f7f1", "dark": "#232b25"},
        }
    ]
    assert props["rowClassName"] == [
        {
            "selector": {"bookTitle": "The Fellowship of the Ring"},
            "value": "ring-bearer",
        }
    ]
    assert "rowAttributes" not in props
    assert props["rowStyle"] == [
        {
            "selector": {"character": "Samwise"},
            "value": {"fontStyle": "italic", "fontWeight": 700},
        }
    ]


def test_update_rows_appends_rules_and_rejects_duplicate_aliases():
    table = dmdt.DataTable(
        data=[{"id": 1, "status": "On Track"}],
        columns=[{"accessor": "status"}],
    ).update_rows(
        selector={"status": "On Track"},
        className="row-ok",
    )

    updated = table.update_rows(
        selector={"status": "Needs Review"},
        className="row-review",
    )
    props = updated.to_plotly_json()["props"]

    assert props["rowClassName"] == [
        {"selector": {"status": "On Track"}, "value": "row-ok"},
        {"selector": {"status": "Needs Review"}, "value": "row-review"},
    ]

    try:
        table.update_rows(color="blue", rowColor="red")
    except TypeError as exc:
        assert "Pass either rowColor or color" in str(exc)
    else:
        raise AssertionError("Expected update_rows to reject duplicate aliases")


def test_update_rows_supports_row_attributes_rules():
    table = (
        dmdt.DataTable(
            data=[{"id": 1, "status": "On Track"}, {"id": 2, "status": "Review"}],
            columns=[{"accessor": "status"}],
        )
        .update_rows(attributes={"data-kind": "employee"})
        .update_rows(
            selector={"status": "Review"},
            rowAttributes={"data-status": "review", "title": "Needs review"},
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["rowAttributes"] == [
        {"value": {"data-kind": "employee"}},
        {
            "selector": {"status": "Review"},
            "value": {"data-status": "review", "title": "Needs review"},
        },
    ]


def test_update_rows_supports_row_dragging():
    table = dmdt.DataTable(
        data=[
            {"id": 1, "name": "Avery"},
            {"id": 2, "name": "Mina"},
        ],
        columns=[{"accessor": "name"}],
        paginationMode="none",
    )

    updated = table.update_rows(draggable=True)
    props = updated.to_plotly_json()["props"]

    assert updated is table
    assert props["rowDragging"] is True

    try:
        table.update_rows(selector={"id": 1}, draggable=True)
    except TypeError as exc:
        assert "rowDragging is a table-level setting" in str(exc)
    else:
        raise AssertionError("Expected selector + draggable to be rejected")


def test_update_rows_supports_expansion_content_and_state():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery"}],
        columns=[{"accessor": "name"}],
        paginationMode="none",
    ).update_rows(
        expandedRecordIds=[1],
        rowExpansion={
            "allowMultiple": True,
            "content": html.Div(
                "Details for {name}",
                id={"type": "expansion-shell", "id": "{id}"},
            ),
        },
    )

    props = table.to_plotly_json()["props"]

    assert props["expandedRecordIds"] == [1]
    assert props["rowExpansion"]["allowMultiple"] is True
    assert (
        props["rowExpansion"]["content"].to_plotly_json()["props"]["children"]
        == "Details for {name}"
    )

    try:
        table.update_rows(
            selector={"id": 1},
            rowExpansion={"content": html.Div("Nope")},
        )
    except TypeError as exc:
        assert "rowExpansion is a table-level setting" in str(exc)
    else:
        raise AssertionError("Expected selector + rowExpansion to be rejected")


def test_add_interactivity_applies_row_and_cell_click_affordances():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery", "status": "On Track"}],
        columns=[
            {"accessor": "name"},
            {"accessor": "status"},
        ],
    ).add_interactivity(
        rowClick=True,
        cellClick=True,
        cellSelector="name",
    )

    props = table.to_plotly_json()["props"]

    assert props["highlightOnHover"] is True
    assert props["textSelectionDisabled"] is True
    assert props["rowStyle"] == {"cursor": "pointer"}
    assert props["columns"][0]["cellsStyle"] == {"cursor": "pointer"}
    assert "cellsStyle" not in props["columns"][1]


def test_add_interactivity_preserves_existing_rules_and_explicit_settings():
    table = (
        dmdt.DataTable(
            data=[
                {"id": 1, "name": "Avery", "status": "On Track"},
                {"id": 2, "name": "Mina", "status": "Needs Review"},
            ],
            columns=[
                {"accessor": "name", "cellsStyle": {"fontWeight": 600}},
                {"accessor": "status"},
            ],
            highlightOnHover=False,
        )
        .update_rows(
            selector={"status": "Needs Review"},
            style={"fontStyle": "italic"},
        )
        .add_interactivity(
            rowClick=True,
            cellClick=True,
            cellSelector="name",
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["highlightOnHover"] is False
    assert props["textSelectionDisabled"] is True
    assert props["rowStyle"] == [
        {"value": {"cursor": "pointer"}},
        {
            "selector": {"status": "Needs Review"},
            "value": {"fontStyle": "italic"},
        },
    ]
    assert props["columns"][0]["cellsStyle"] == {
        "fontWeight": 600,
        "cursor": "pointer",
    }


def test_update_selection_pagination_sorting_and_search_helpers():
    table = (
        dmdt.DataTable(
            data=[{"id": 1, "name": "Avery", "status": "On Track"}],
            columns=[
                dmdt.Column(
                    "name",
                    cellAttributes={"data-column": "name"},
                ),
                {"accessor": "status"},
            ],
        )
        .update_selection(
            selectionTrigger="checkbox",
            selectionColumnClassName="selection-col",
            selectionColumnStyle={"width": 52},
            selectionCheckboxProps={"radius": "xl"},
            allRecordsSelectionCheckboxProps={"aria-label": "Select all"},
            selectableRowRules=[
                {"selector": {"status": "On Track"}, "value": True},
            ],
            disabledSelectionRowRules=[
                {"selector": {"id": 2}, "value": True},
            ],
            selectionCheckboxRules=[
                {"selector": {"status": "On Track"}, "value": {"color": "green"}},
            ],
        )
        .update_pagination(
            paginationMode="server",
            page=3,
            recordsPerPage=25,
            totalRecords=120,
            paginationSize="md",
            paginationActiveTextColor="white",
            paginationActiveBackgroundColor="blue",
            loadingText="Loading records...",
        )
        .update_sorting(
            sortMode="server",
            sortStatus={"columnAccessor": "name", "direction": "asc"},
            sortIcons={
                "sorted": html.Span("S", id="sort-s"),
                "unsorted": html.Span("U", id="sort-u"),
            },
        )
        .update_search(
            searchMode="server",
            searchQuery="Avery",
            searchableAccessors=["name"],
        )
    )

    props = table.to_plotly_json()["props"]

    assert props["selectionTrigger"] == "checkbox"
    assert props["selectionColumnClassName"] == "selection-col"
    assert props["selectionColumnStyle"] == {"width": 52}
    assert props["selectionCheckboxProps"] == {"radius": "xl"}
    assert props["allRecordsSelectionCheckboxProps"] == {
        "aria-label": "Select all"
    }
    assert props["selectableRowRules"] == [
        {"selector": {"status": "On Track"}, "value": True}
    ]
    assert props["disabledSelectionRowRules"] == [
        {"selector": {"id": 2}, "value": True}
    ]
    assert props["selectionCheckboxRules"] == [
        {"selector": {"status": "On Track"}, "value": {"color": "green"}}
    ]
    assert props["paginationMode"] == "server"
    assert props["page"] == 3
    assert props["recordsPerPage"] == 25
    assert props["totalRecords"] == 120
    assert props["paginationSize"] == "md"
    assert props["paginationActiveTextColor"] == "white"
    assert props["paginationActiveBackgroundColor"] == "blue"
    assert props["loadingText"] == "Loading records..."
    assert props["sortMode"] == "server"
    assert props["sortStatus"] == {"columnAccessor": "name", "direction": "asc"}
    assert props["searchMode"] == "server"
    assert props["searchQuery"] == "Avery"
    assert props["searchableAccessors"] == ["name"]
    assert props["columns"][0]["cellAttributes"] == {"data-column": "name"}


def test_clear_selection_and_expansion_reset_state():
    table = (
        dmdt.DataTable(
            data=[{"id": 1, "name": "Avery"}],
            columns=[{"accessor": "name"}],
        )
        .update_selection(selectedRecordIds=[1], selectedRecords=[{"id": 1}])
        .update_rows(expandedRecordIds=[1])
        .clear_selection()
        .clear_expansion()
    )

    props = table.to_plotly_json()["props"]

    assert props["selectedRecordIds"] == []
    assert props["selectedRecords"] == []
    assert props["expandedRecordIds"] == []


def test_helper_config_classes_build_expected_mappings():
    group = dmdt.ColumnGroup("details", columns=["name"], title="Details")
    selection = dmdt.SelectionConfig(
        selectionTrigger="checkbox",
        selectionCheckboxProps={"size": "sm"},
    )
    pagination = dmdt.PaginationConfig(page=2, recordsPerPage=20, totalRecords=99)
    expansion = dmdt.RowExpansionConfig(
        html.Div("Details", id="expansion"),
        allowMultiple=True,
    )

    assert group == {"id": "details", "columns": ["name"], "title": "Details"}
    assert selection == {
        "selectionTrigger": "checkbox",
        "selectionCheckboxProps": {"size": "sm"},
    }
    assert pagination == {"page": 2, "recordsPerPage": 20, "totalRecords": 99}
    assert expansion["allowMultiple"] is True
    assert expansion["content"].to_plotly_json()["props"]["id"] == "expansion"


def test_update_layout_supports_additional_mantine_style_props():
    table = dmdt.DataTable(
        data=[{"id": 1, "name": "Avery"}],
        columns=[{"accessor": "name"}],
    ).update_layout(
        bd="1px solid red",
        bdrs="xl",
        td="underline",
        bgsz="cover",
        bgp="center",
        bgr="no-repeat",
        bga="fixed",
        pos="relative",
        top=1,
        left="2rem",
        bottom=0,
        right="auto",
        inset="unset",
    )

    props = table.to_plotly_json()["props"]

    assert props["bd"] == "1px solid red"
    assert props["bdrs"] == "xl"
    assert props["td"] == "underline"
    assert props["bgsz"] == "cover"
    assert props["bgp"] == "center"
    assert props["bgr"] == "no-repeat"
    assert props["bga"] == "fixed"
    assert props["pos"] == "relative"
    assert props["top"] == 1
    assert props["left"] == "2rem"
    assert props["bottom"] == 0
    assert props["right"] == "auto"
    assert props["inset"] == "unset"

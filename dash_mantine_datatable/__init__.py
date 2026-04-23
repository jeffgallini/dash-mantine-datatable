"""Dash wrapper for Mantine DataTable with Python-friendly helpers.

Description
-----------
This package exposes a `DataTable` component for Dash plus a small set of
helper factories that make common table configuration more discoverable from
Python. The usual entry point is `DataTable(...)`, while `Column(...)`,
`ColumnGroup(...)`, `SelectionConfig(...)`, `PaginationConfig(...)`, and
`RowExpansionConfig(...)` help you build the nested dictionaries that the
component expects.

Notes
-----
The public API is intentionally chainable. Most configuration helpers return
the current `DataTable` instance so you can start with a minimal table and add
columns, row rules, grouping, pagination, and selection step by step.

Examples
--------
>>> import dash_mantine_datatable as dmdt
>>> table = dmdt.DataTable(
...     data=[{"id": 1, "name": "Avery", "salary": 128000}],
...     columns=[
...         dmdt.Column("name", title="Employee"),
...         dmdt.Column("salary", presentation="currency", currency="USD"),
...     ],
...     radius="lg",
... )
>>> table.update_selection(selectionTrigger="checkbox")
DataTable(...)
"""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path
from typing import Any

import dash as _dash

from .DataTable import DataTable as _GeneratedDataTable

_PACKAGE_INFO_PATH = Path(__file__).with_name("package-info.json")
package = json.loads(_PACKAGE_INFO_PATH.read_text(encoding="utf-8"))
package_name = package["name"].replace(" ", "_").replace("-", "_")
__version__ = package["version"]

if not hasattr(_dash, "__plotly_dash") and not hasattr(_dash, "development"):
    raise ImportError(
        "Dash could not be imported. Make sure there is no local module named "
        "'dash.py' shadowing the real Dash package."
    )

_js_dist = [
    {
        "relative_package_path": "dash_mantine_datatable.min.js",
        "namespace": package_name,
    },
    {
        "relative_package_path": "dash_mantine_datatable.min.js.map",
        "namespace": package_name,
        "dynamic": True,
    },
]
_css_dist: list[dict[str, Any]] = []

_PROP_ALIASES = {
    "child_rows_accessor": "childRowsAccessor",
    "custom_loader": "customLoader",
    "default_column_render": "defaultColumnRender",
    "dir": "direction",
    "disabled_selection_row_rules": "disabledSelectionRowRules",
    "fontSize": "fz",
    "group_aggregations": "groupAggregations",
    "group_by": "groupBy",
    "loading_text": "loadingText",
    "no_records_icon": "noRecordsIcon",
    "pagination_active_background_color": "paginationActiveBackgroundColor",
    "pagination_active_text_color": "paginationActiveTextColor",
    "pagination_size": "paginationSize",
    "records": "data",
    "selection_checkbox_props": "selectionCheckboxProps",
    "selection_checkbox_rules": "selectionCheckboxRules",
    "selection_column_class_name": "selectionColumnClassName",
    "selection_column_style": "selectionColumnStyle",
    "selectable_row_rules": "selectableRowRules",
    "sort_icons": "sortIcons",
}
_EXTRA_BASE_NODES = (
    "customLoader",
    "defaultColumnRender",
    "emptyState",
    "noRecordsIcon",
)
_EXTRA_CHILDREN_PROPS = (
    "columns[].render",
    "columns[].editor",
    "columns[].filter",
    "columns[].footer",
    "customLoader",
    "defaultColumnProps.render",
    "defaultColumnProps.editor",
    "defaultColumnProps.filter",
    "defaultColumnProps.footer",
    "defaultColumnRender",
    "emptyState",
    "noRecordsIcon",
    "sortIcons.sorted",
    "sortIcons.unsorted",
)
_MERGED_MAPPING_PROPS = {"style", "styles", "classNames", "tableProps", "scrollAreaProps"}
_COLUMN_MERGE_PROPS = {
    "cellAttributes",
    "cellsStyle",
    "filterPopoverProps",
    "footerStyle",
    "headerStyle",
    "style",
    "titleStyle",
}
_ROW_PROP_ALIASES = {
    "attributes": "rowAttributes",
    "backgroundColor": "rowBackgroundColor",
    "className": "rowClassName",
    "color": "rowColor",
    "style": "rowStyle",
}


def _compact_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in mapping.items() if value is not None}


def _merge_mapping(existing: Any, incoming: Any) -> Any:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = deepcopy(existing)
        for key, value in incoming.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = _merge_mapping(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
    return deepcopy(incoming)


def _normalize_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in kwargs.items():
        canonical = _PROP_ALIASES.get(key, key)
        if canonical in normalized and canonical != key:
            raise TypeError(f"Received both '{canonical}' and alias '{key}'.")
        normalized[canonical] = value
    return normalized


def _normalize_column(column: Any) -> dict[str, Any]:
    if isinstance(column, str):
        return {"accessor": column}
    if isinstance(column, dict):
        return deepcopy(column)
    raise TypeError("Columns must be dictionaries or accessor strings.")


def _resolve_column_reference(reference: Any, existing_columns: list[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(reference, str):
        for column in existing_columns:
            if column.get("accessor") == reference:
                return deepcopy(column)
        return {"accessor": reference}

    column = _normalize_column(reference)
    accessor = column.get("accessor")
    if accessor is None:
        return column

    for existing in existing_columns:
        if existing.get("accessor") == accessor:
            return _merge_mapping(existing, column)
    return column


def _resolve_group(group: Any, existing_columns: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(group, dict):
        raise TypeError("Column groups must be dictionaries.")

    resolved = deepcopy(group)
    if "columns" in resolved and resolved["columns"] is not None:
        resolved["columns"] = [
            _resolve_column_reference(column, existing_columns)
            for column in resolved["columns"]
        ]
    if "groups" in resolved and resolved["groups"] is not None:
        resolved["groups"] = [
            _resolve_group(child_group, existing_columns)
            for child_group in resolved["groups"]
        ]
    return resolved


def _normalize_selector(selector: Any) -> list[Any] | None:
    if selector is None:
        return None
    if isinstance(selector, (list, tuple, set)):
        return list(selector)
    return [selector]


def _column_indexes(columns: list[dict[str, Any]], selector: Any) -> list[int]:
    selectors = _normalize_selector(selector)
    if selectors is None:
        return list(range(len(columns)))

    indexes: list[int] = []
    selector_set = set(selectors)
    for index, column in enumerate(columns):
        if column.get("accessor") in selector_set:
            indexes.append(index)
    return indexes


def _group_indexes(groups: list[dict[str, Any]], selector: Any) -> list[int]:
    selectors = _normalize_selector(selector)
    if selectors is None:
        return list(range(len(groups)))

    indexes: list[int] = []
    selector_set = set(selectors)
    for index, group in enumerate(groups):
        if group.get("id") in selector_set:
            indexes.append(index)
    return indexes


def _with_rule(prop_name: str, current: Any, value: Any, selector: Any) -> Any:
    rule = {"value": deepcopy(value)}
    if selector is not None:
        rule["selector"] = deepcopy(selector)

    if current is None:
        if selector is None and prop_name in {"rowColor", "rowBackgroundColor", "rowClassName", "rowStyle"}:
            return deepcopy(value)
        return [rule]

    if isinstance(current, list):
        if selector is None:
            return [rule, *deepcopy(current)]
        return [*deepcopy(current), rule]

    if selector is None:
        if prop_name == "rowStyle" and isinstance(current, dict) and isinstance(value, dict):
            return _merge_mapping(current, value)
        if prop_name in {"rowColor", "rowBackgroundColor", "rowClassName", "rowStyle"}:
            return deepcopy(value)

    base_rule = {"value": deepcopy(current)}
    if selector is None:
        return [rule, base_rule]
    return [base_rule, rule]


def Column(accessor: str | None = None, /, **kwargs: Any) -> dict[str, Any]:
    """
    Description
    -----------
    Build a column-definition dictionary for `DataTable(columns=[...])`.
    This helper is the quickest way to create readable column configs from
    Python without manually repeating `{"accessor": ...}` for every column.

    Parameters
    ----------
    accessor : str | None, optional
        Description: Record key rendered by the column. This becomes the
        column identifier used by helpers such as
        `table.update_columns(selector="salary", ...)`.
        Example: `Column("salary")`.
    title : str, optional
        Description: Header label shown above the column. If omitted, the
        frontend falls back to the accessor or its built-in title formatting.
        Example: `title="Annual Salary"`.
    presentation : str, optional
        Description: Built-in display mode used to format cell values.
        Expected inputs: `'text'`, `'number'`, `'currency'`, `'date'`,
        `'datetime'`, `'badge'`, `'link'`, `'code'`, `'json'`, `'progress'`.
        Example: `presentation="currency"`.
    sortable : bool, optional
        Description: Enables sorting for the column.
        Example: `sortable=True`.
    editable : bool, optional
        Description: Enables double-click editing for the column. Pair this
        with `editor` when you want a custom Dash input component.
        Example: `editable=True`.
    editor : Any, optional
        Description: Dash component used as the in-place editor for editable
        cells.
        Example: `editor=dmc.NumberInput(min=0, thousandSeparator=",")`.
    render : Any, optional
        Description: Dash component or renderer payload used for custom cell
        content.
        Example: `render=dmc.Text("View", c="blue")`.
    filter : Any, optional
        Description: Dash component rendered in the column filter popover.
        Example: `filter=dmc.TextInput(placeholder="Filter names")`.
    textAlign : str, optional
        Description: Horizontal alignment for cell content.
        Expected inputs: values accepted by Mantine/DataTable such as
        `'left'`, `'center'`, `'right'`.
        Example: `textAlign="right"`.
    width : int | float | str, optional
        Description: Column width. You can pass a numeric pixel value or a CSS
        width string.
        Example: `width=140`.
    cellsStyle : dict, optional
        Description: Inline style mapping applied to body cells.
        Example: `cellsStyle={"fontVariantNumeric": "tabular-nums"}`.
    titleStyle : dict, optional
        Description: Inline style mapping applied to the header cell.
        Example: `titleStyle={"textTransform": "uppercase"}`.
    draggable : bool, optional
        Description: Allows the column to participate in column dragging.
        Example: `draggable=True`.
    toggleable : bool, optional
        Description: Allows the column to be shown or hidden by column
        customization controls.
        Example: `toggleable=True`.
    resizable : bool, optional
        Description: Allows the column width to be resized by the user.
        Example: `resizable=True`.
    defaultToggle : bool, optional
        Description: Initial visibility state used when column toggling is
        enabled.
        Example: `defaultToggle=False`.

    Returns
    -------
    dict
        A Dash-safe column configuration dictionary.

    Notes
    -----
    The helper does not validate every possible column key. It simply builds a
    plain dictionary, which makes it safe to use with existing Mantine
    DataTable column options and this package's Dash-specific additions.

    Examples
    --------
    >>> Column("salary", title="Salary", presentation="currency", currency="USD")
    {'accessor': 'salary', 'title': 'Salary', 'presentation': 'currency', 'currency': 'USD'}
    >>> Column("status", presentation="badge", badgeColorAccessor="statusColor")
    {'accessor': 'status', 'presentation': 'badge', 'badgeColorAccessor': 'statusColor'}
    """
    column = {}
    if accessor is not None:
        column["accessor"] = accessor
    column.update(kwargs)
    return column


def ColumnGroup(
    group_id: str | None = None,
    /,
    *,
    columns: list[Any] | None = None,
    groups: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Description
    -----------
    Build a grouped-header definition for `DataTable(groups=[...])`. Use this
    when you want multiple header rows, such as a "Compensation" group above
    salary and bonus columns.

    Parameters
    ----------
    group_id : str | None, optional
        Description: Stable identifier for the group. This is the id you use
        later with `table.group_columns(selector="compensation", ...)`.
        Example: `group_id="compensation"`.
    columns : list[Any] | None, optional
        Description: Column references attached directly to this group. Each
        item may be an accessor string like `"salary"` or a full column
        dictionary.
        Example: `columns=["salary", "bonus"]`.
    groups : list[dict[str, Any]] | None, optional
        Description: Nested child groups for multi-row grouped headers.
        Example: `groups=[ColumnGroup("cash", columns=["salary", "bonus"])]`.
    title : str, optional
        Description: Visible header label for the group.
        Example: `title="Compensation"`.
    style : dict, optional
        Description: Inline style mapping applied to the group header cell.
        Example: `style={"textAlign": "center"}`.
    headerStyle : dict, optional
        Description: Header-specific style mapping forwarded to the frontend.
        Example: `headerStyle={"backgroundColor": "var(--mantine-color-gray-0)"}`.
    textAlign : str, optional
        Description: Alignment hint for grouped-header content.
        Expected inputs: values accepted by Mantine/DataTable such as
        `'left'`, `'center'`, `'right'`.
        Example: `textAlign="center"`.

    Returns
    -------
    dict
        A grouped-header configuration dictionary.

    Notes
    -----
    Group dictionaries are plain Python objects, so they can be freely mixed
    with `Column(...)` output and raw dictionaries in the same `groups` list.

    Examples
    --------
    >>> ColumnGroup("profile", title="Profile", columns=["name", "team"])
    {'id': 'profile', 'columns': ['name', 'team'], 'title': 'Profile'}
    """
    group = {}
    if group_id is not None:
        group["id"] = group_id
    if columns is not None:
        group["columns"] = list(columns)
    if groups is not None:
        group["groups"] = deepcopy(groups)
    group.update(kwargs)
    return group


def SelectionConfig(**kwargs: Any) -> dict[str, Any]:
    """
    Description
    -----------
    Build a compact selection configuration dictionary that you can unpack into
    `DataTable(...)` or pass to `table.update_selection(...)`.

    Parameters
    ----------
    selectionTrigger : str, optional
        Description: Enables row selection and decides how it is triggered.
        Expected inputs: `'cell'`, `'checkbox'`.
        Example: `selectionTrigger="checkbox"`.
    selectedRecordIds : list[Any], optional
        Description: Controlled list of selected row ids.
        Example: `selectedRecordIds=[1, 4, 8]`.
    selectedRecords : list[dict], optional
        Description: Controlled list of selected record payloads.
        Example: `selectedRecords=[{"id": 1, "name": "Avery"}]`.
    selectableRowRules : bool | dict | list, optional
        Description: Rule definition that marks which rows are selectable.
        Example: `selectableRowRules=[{"selector": {"status": "Active"}, "value": True}]`.
    disabledSelectionRowRules : bool | dict | list, optional
        Description: Rule definition that disables row selection for matching
        rows.
        Example: `disabledSelectionRowRules=[{"selector": {"archived": True}, "value": True}]`.
    selectionCheckboxRules : dict | list, optional
        Description: Conditional checkbox props for the selection column.
        Example: `selectionCheckboxRules=[{"selector": {"locked": True}, "value": {"disabled": True}}]`.
    selectionCheckboxProps : dict, optional
        Description: Shared props for each row-selection checkbox.
        Example: `selectionCheckboxProps={"size": "sm"}`.
    allRecordsSelectionCheckboxProps : dict, optional
        Description: Props for the "select all" checkbox in the header.
        Example: `allRecordsSelectionCheckboxProps={"aria-label": "Select all rows"}`.
    selectionColumnClassName : str, optional
        Description: CSS class applied to the selection column.
        Example: `selectionColumnClassName="table-selection-col"`.
    selectionColumnStyle : dict, optional
        Description: Inline style mapping applied to the selection column.
        Example: `selectionColumnStyle={"width": 44}`.

    Returns
    -------
    dict
        A dictionary with `None` values removed.

    Notes
    -----
    This helper is a convenience for building clean config objects. It does
    not mutate a table and it drops keys whose value is `None`.

    Examples
    --------
    >>> SelectionConfig(selectionTrigger="checkbox", selectedRecordIds=[1, 2])
    {'selectionTrigger': 'checkbox', 'selectedRecordIds': [1, 2]}
    """
    return _compact_mapping(deepcopy(kwargs))


def PaginationConfig(**kwargs: Any) -> dict[str, Any]:
    """
    Description
    -----------
    Build a compact pagination configuration dictionary for client-side or
    server-side paging.

    Parameters
    ----------
    page : int | float, optional
        Description: Current page number in controlled pagination mode.
        Example: `page=1`.
    pageSize : int | float, optional
        Description: Number of rows shown per page when using the `pageSize`
        prop.
        Example: `pageSize=25`.
    recordsPerPage : int | float, optional
        Description: Preferred page-size prop matching Mantine DataTable's API.
        Example: `recordsPerPage=25`.
    totalRecords : int | float, optional
        Description: Total number of records available, typically required for
        server-side pagination.
        Example: `totalRecords=248`.
    recordsPerPageOptions : list[int | float], optional
        Description: Page-size choices shown in the footer control.
        Example: `recordsPerPageOptions=[10, 25, 50, 100]`.
    pageSizeOptions : list[int | float], optional
        Description: Alternative page-size options prop.
        Example: `pageSizeOptions=[10, 25, 50]`.
    recordsPerPageLabel : str, optional
        Description: Label shown next to the page-size selector.
        Example: `recordsPerPageLabel="Rows"`.
    paginationSize : str | int | float, optional
        Description: Visual size of the pagination controls.
        Expected inputs: Mantine size tokens such as `'xs'`, `'sm'`, `'md'`,
        `'lg'`, `'xl'`, or a numeric size when supported.
        Example: `paginationSize="sm"`.
    paginationActiveTextColor : str | dict, optional
        Description: Text color for the active page button.
        Example: `paginationActiveTextColor="white"`.
    paginationActiveBackgroundColor : str | dict, optional
        Description: Background color for the active page button.
        Example: `paginationActiveBackgroundColor="blue.6"`.
    paginationWithEdges : bool, optional
        Description: Shows first/last page controls when `True`.
        Example: `paginationWithEdges=True`.
    paginationWithControls : bool, optional
        Description: Shows previous/next controls when `True`.
        Example: `paginationWithControls=True`.

    Returns
    -------
    dict
        A dictionary with `None` values removed.

    Notes
    -----
    For most apps you will set either `recordsPerPage` or `pageSize`, not
    both. This helper simply forwards whatever keys you provide.

    Examples
    --------
    >>> PaginationConfig(page=2, recordsPerPage=25, totalRecords=240)
    {'page': 2, 'recordsPerPage': 25, 'totalRecords': 240}
    """
    return _compact_mapping(deepcopy(kwargs))


def RowExpansionConfig(content: Any = None, /, **kwargs: Any) -> dict[str, Any]:
    """
    Description
    -----------
    Build a row-expansion configuration dictionary for detail panels shown
    beneath a record.

    Parameters
    ----------
    content : Any, optional
        Description: Dash component or payload rendered when a row is expanded.
        Example: `content=dmc.Text("Employee details")`.
    allowMultiple : bool, optional
        Description: Allows multiple rows to stay expanded at the same time.
        Example: `allowMultiple=True`.
    trigger : str, optional
        Description: Chooses how expansion is toggled.
        Expected inputs: frontend-supported trigger values such as `'click'`
        when available.
        Example: `trigger="click"`.

    Returns
    -------
    dict
        A dictionary with `None` values removed.

    Notes
    -----
    This helper is especially useful when you want to keep expansion config in
    one place and reuse it across multiple table instances.

    Examples
    --------
    >>> RowExpansionConfig(content="More details", allowMultiple=True)
    {'allowMultiple': True, 'content': 'More details'}
    """
    config = deepcopy(kwargs)
    if content is not None:
        config["content"] = content
    return _compact_mapping(config)


class DataTable(_GeneratedDataTable):
    """
    Description
    -----------
    Declarative Dash table component with chainable Python-side configuration
    helpers. `DataTable` wraps Mantine DataTable in a Dash-friendly API that
    works well with `dash-mantine-components`, while also adding helpers for
    columns, grouped headers, row rules, selection, pagination, sorting, and
    search.

    If you are new to the package, the usual pattern is:

    1. Pass `data` and `columns` when you construct the table.
    2. Set `idAccessor` if your row id field is not named `id`.
    3. Choose client-side or server-side behavior with
       `paginationMode`, `sortMode`, and `searchMode`.
    4. Use chainable helpers like `update_columns()` and `update_rows()` to
       refine behavior after the base table is created.

    Parameters
    ----------
    id : str | dict, optional
        Description: Dash component id used in callbacks.
        Example: `id="employees-table"`.
    data : list[dict], optional
        Description: Table records. This is the preferred Dash-facing alias
        for row data.
        Example: `data=[{"id": 1, "name": "Avery"}]`.
    records : list[dict], optional
        Description: Alias for `data` kept for Mantine DataTable familiarity.
        If both are supplied, use one source of truth.
        Example: `records=[{"id": 1, "name": "Avery"}]`.
    columns : list[dict], optional
        Description: Column definitions. Each column typically has an
        `accessor`, and may also include formatting, sorting, filtering, or
        editing behavior.
        Example: `columns=[Column("name"), Column("salary", presentation="currency")]`.
    groups : list[dict], optional
        Description: Grouped-header definitions for multi-row column headers.
        Example: `groups=[ColumnGroup("profile", title="Profile", columns=["name", "team"])]`.
    idAccessor : str | dict | list[str], optional
        Description: Record identifier accessor used for selection, expansion,
        row rules, and drag operations. Use this when your row key is not the
        default `id`.
        Example: `idAccessor="employeeId"`.
    groupBy : str | list[str], optional
        Description: Accessor or accessors used for inline row grouping.
        Example: `groupBy="team"`.
    childRowsAccessor : str, optional
        Description: Accessor containing nested child rows when your data is
        already hierarchical.
        Example: `childRowsAccessor="children"`.
    groupAggregations : dict, optional
        Description: Aggregation mapping for grouped parent rows.
        Expected inputs: built-in aggregations such as `'sum'`, `'mean'`,
        `'median'`, `'min'`, `'max'`, `'count'`, or a custom client-side
        function string.
        Example: `groupAggregations={"salary": "sum"}`.
    paginationMode : str, optional
        Description: Chooses where pagination is handled.
        Expected inputs: `'client'`, `'server'`, `'none'`.
        Example: `paginationMode="server"`.
    sortMode : str, optional
        Description: Chooses where sorting is handled.
        Expected inputs: `'client'`, `'server'`.
        Example: `sortMode="client"`.
    searchMode : str, optional
        Description: Chooses where search filtering is handled.
        Expected inputs: `'client'`, `'server'`.
        Example: `searchMode="client"`.
    searchQuery : str, optional
        Description: Controlled search text.
        Example: `searchQuery="platform"`.
    searchableAccessors : list[str], optional
        Description: Limits client-side search to specific record fields.
        Example: `searchableAccessors=["name", "team", "role"]`.
    page : int | float, optional
        Description: Current page in controlled pagination mode.
        Example: `page=1`.
    recordsPerPage : int | float, optional
        Description: Number of rows shown per page.
        Example: `recordsPerPage=25`.
    totalRecords : int | float, optional
        Description: Total record count, usually required in server-side
        pagination mode.
        Example: `totalRecords=248`.
    selectionTrigger : str, optional
        Description: Enables selection and decides how it is triggered.
        Expected inputs: `'cell'`, `'checkbox'`.
        Example: `selectionTrigger="checkbox"`.
    selectedRecordIds : list[Any], optional
        Description: Controlled ids for selected rows.
        Example: `selectedRecordIds=[1, 3]`.
    rowExpansion : dict, optional
        Description: Configuration for per-row detail panels.
        Example: `rowExpansion=RowExpansionConfig(content=dmc.Text("Details"))`.
    rowDragging : bool | dict, optional
        Description: Enables drag-and-drop row reordering.
        Example: `rowDragging=True`.
    locale : str, optional
        Description: Locale used for number and date formatting.
        Example: `locale="en-US"`.
    direction : str, optional
        Description: Layout direction for LTR or RTL UIs.
        Expected inputs: `'ltr'`, `'rtl'`.
        Example: `direction="rtl"`.
    radius : str | int | float, optional
        Description: Border radius for the table container.
        Expected inputs: Mantine size tokens such as `'xs'`, `'sm'`, `'md'`,
        `'lg'`, `'xl'`, or a numeric/CSS value.
        Example: `radius="lg"`.
    striped : bool, optional
        Description: Alternates row backgrounds for easier scanning.
        Example: `striped=True`.
    highlightOnHover : bool, optional
        Description: Highlights the active row on hover.
        Example: `highlightOnHover=True`.
    withTableBorder : bool, optional
        Description: Draws an outer table border.
        Example: `withTableBorder=True`.
    withColumnBorders : bool, optional
        Description: Draws vertical borders between columns.
        Example: `withColumnBorders=False`.
    withRowBorders : bool, optional
        Description: Draws borders between body rows.
        Example: `withRowBorders=True`.
    height : str | int | float, optional
        Description: Fixed table height, often used with sticky headers or
        scrollable layouts.
        Example: `height=420`.
    minHeight : str | int | float, optional
        Description: Minimum table height.
        Example: `minHeight=240`.
    maxHeight : str | int | float, optional
        Description: Maximum table height before scrolling.
        Example: `maxHeight=560`.
    horizontalSpacing : str | int | float, optional
        Description: Horizontal cell padding.
        Expected inputs: Mantine spacing tokens such as `'xs'`, `'sm'`, `'md'`,
        `'lg'`, `'xl'`, or numeric values.
        Example: `horizontalSpacing="sm"`.
    verticalSpacing : str | int | float, optional
        Description: Vertical cell padding.
        Expected inputs: Mantine spacing tokens such as `'xs'`, `'sm'`, `'md'`,
        `'lg'`, `'xl'`, or numeric values.
        Example: `verticalSpacing="xs"`.
    verticalAlign : str, optional
        Description: Vertical alignment for cell content.
        Expected inputs: `'top'`, `'center'`, `'bottom'`.
        Example: `verticalAlign="center"`.
    bg : str | dict, optional
        Description: Mantine background color prop for the table wrapper.
        Example: `bg="white"`.
    c : str | dict, optional
        Description: Mantine text color prop for the table wrapper.
        Example: `c="dark.8"`.
    emptyState : str | dict, optional
        Description: Content shown when there are no rows to display.
        Example: `emptyState=dmc.Text("No matching employees")`.
    customLoader : Any, optional
        Description: Custom loader shown while `fetching=True`.
        Example: `customLoader=dmc.Loader(color="blue")`.
    noRecordsIcon : Any, optional
        Description: Icon or component shown beside the empty-state text.
        Example: `noRecordsIcon=dmc.ThemeIcon("!")`.
    storeColumnsKey : str, optional
        Description: Local-storage key used to persist draggable, toggleable,
        or resizable column state in the browser.
        Example: `storeColumnsKey="employees-columns-v1"`.

    Attributes
    ----------
    data : list of dict
        Records rendered by the table. `records` is normalized into this
        property during initialization.
    columns : list of dict
        Column configuration currently attached to the table.
    groups : list of dict or None
        Column-group configuration for grouped headers.
    groupBy : str or list of str or None
        Active row-grouping accessor or accessors.
    idAccessor : str or dict or list of str
        Record identity accessor used by selection, expansion, and row rules.
    selectedRecordIds : list
        Selected record identifiers.
    selectedRecords : list
        Selected record payloads mirrored from the front end.
    expandedRecordIds : list
        Expanded row identifiers for `rowExpansion` or grouped child rows.
    sortStatus : dict or None
        Current sort descriptor used by client-side or server-side sorting.
    searchQuery : str or None
        Current table search query.
    pagination : dict or None
        Pagination event payload reported by the component.
    lastSortChange : dict or None
        Latest sort interaction payload emitted by the component.
    lastSelectionChange : dict or None
        Latest selection interaction payload emitted by the component.
    lastExpansionChange : dict or None
        Latest expansion interaction payload emitted by the component.
    lastRowDragChange : dict or None
        Latest row-drag interaction payload emitted by the component.

    Notes
    -----
    The complete constructor keyword surface comes from the generated
    `DataTable.py` component. This wrapper keeps those canonical keywords and
    adds a small set of Python-friendly aliases.

    Python-friendly aliases are accepted for a few common props, including
    `records -> data`, `group_by -> groupBy`, `group_aggregations ->
    groupAggregations`, `child_rows_accessor -> childRowsAccessor`, and
    `dir -> direction`.

    Mapping-style properties such as `style`, `styles`, `classNames`,
    `tableProps`, and `scrollAreaProps` are merged when updated through the
    fluent helpers instead of being blindly replaced.

    Examples
    --------
    >>> table = DataTable(
    ...     id="employees",
    ...     data=[{"id": 1, "name": "Avery", "team": "Platform", "salary": 128000}],
    ...     columns=[
    ...         Column("name", title="Employee", sortable=True),
    ...         Column("team", sortable=True),
    ...         Column("salary", presentation="currency", currency="USD", textAlign="right"),
    ...     ],
    ...     idAccessor="id",
    ...     paginationMode="client",
    ...     radius="lg",
    ... )
    >>> table.update_columns(selector="name", title="Employee")
    DataTable(...)
    >>> table.update_selection(selectionTrigger="checkbox")
    DataTable(...)
    >>> table.update_rows(selector={"team": "Platform"}, className="team-platform")
    DataTable(...)
    """

    _base_nodes = tuple(
        sorted(set(getattr(_GeneratedDataTable, "_base_nodes", ())) | set(_EXTRA_BASE_NODES))
    )
    _children_props = tuple(
        sorted(
            set(getattr(_GeneratedDataTable, "_children_props", ()))
            | set(_EXTRA_CHILDREN_PROPS)
        )
    )
    _js_dist = _js_dist
    _css_dist = _css_dist

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Description
        -----------
        Initialize a `DataTable` and normalize the small set of Python-side
        aliases accepted by this wrapper.

        Parameters
        ----------
        *args : Any
            Description: Positional arguments forwarded to the generated Dash
            component. Most users will not need positional arguments.
            Example: `DataTable([...])` is uncommon; keyword arguments are
            preferred.
        **kwargs : Any
            Description: Component properties accepted by `DataTable`. Common
            aliases include `records`, `group_by`, `group_aggregations`,
            `child_rows_accessor`, and `dir`.
            Example: `DataTable(records=data, group_by="team", dir="rtl")`.

        Notes
        -----
        Alias normalization happens before the generated component constructor
        runs, so the stored properties always use the canonical Dash names
        such as `data`, `groupBy`, and `direction`.

        Examples
        --------
        >>> DataTable(records=[{"id": 1, "name": "Avery"}], columns=[Column("name")])
        DataTable(...)
        """
        normalized = _normalize_kwargs(kwargs)
        super().__init__(*args, **normalized)

    def _update_props(self, **kwargs: Any) -> "DataTable":
        """
        Update component properties in place.

        Parameters
        ----------
        **kwargs
            Properties to update. Known aliases are normalized before the
            update is applied.

        Returns
        -------
        DataTable
            The current instance, enabling method chaining.

        Notes
        -----
        Dictionary-like properties listed in `_MERGED_MAPPING_PROPS` are
        merged recursively with existing values.
        """
        normalized = _normalize_kwargs(kwargs)
        for key, value in normalized.items():
            current = getattr(self, key, None)
            if key in _MERGED_MAPPING_PROPS and current is not None:
                setattr(self, key, _merge_mapping(current, value))
            else:
                setattr(self, key, deepcopy(value))
        return self

    def update_layout(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update high-level layout and presentation properties in place. Use
        this when you want to tweak the table shell, sizing, color, spacing,
        or loading presentation after the table has already been created.

        Parameters
        ----------
        radius : str | int | float, optional
            Description: Border radius for the table container.
            Expected inputs: Mantine size tokens such as `'xs'`, `'sm'`,
            `'md'`, `'lg'`, `'xl'`, or a numeric/CSS value.
            Example: `radius="lg"`.
        direction : str, optional
            Description: Layout direction.
            Expected inputs: `'ltr'`, `'rtl'`.
            Example: `direction="rtl"`.
        height : str | int | float, optional
            Description: Fixed table height.
            Example: `height=420`.
        minHeight : str | int | float, optional
            Description: Minimum height for the table shell.
            Example: `minHeight=240`.
        maxHeight : str | int | float, optional
            Description: Maximum height before scroll behavior appears.
            Example: `maxHeight=560`.
        bg : str | dict, optional
            Description: Mantine background color prop.
            Example: `bg="gray.0"`.
        style : dict, optional
            Description: Inline styles applied to the table wrapper.
            Example: `style={"boxShadow": "var(--mantine-shadow-sm)"}`.
        className : str, optional
            Description: CSS class applied to the table wrapper.
            Example: `className="employees-table"`.
        tableProps : dict, optional
            Description: Props forwarded to the underlying Mantine table
            element.
            Example: `tableProps={"style": {"tableLayout": "fixed"}}`.
        scrollAreaProps : dict, optional
            Description: Props forwarded to the table scroll area.
            Example: `scrollAreaProps={"type": "never"}`.
        withTableBorder : bool, optional
            Description: Toggles the outer border.
            Example: `withTableBorder=True`.
        withColumnBorders : bool, optional
            Description: Toggles borders between columns.
            Example: `withColumnBorders=False`.
        pinFirstColumn : bool, optional
            Description: Pins the first visible column during horizontal
            scrolling.
            Example: `pinFirstColumn=True`.
        pinLastColumn : bool, optional
            Description: Pins the last visible column during horizontal
            scrolling.
            Example: `pinLastColumn=True`.
        textSelectionDisabled : bool, optional
            Description: Disables text selection, which helps interactive rows
            and cells feel more intentional.
            Example: `textSelectionDisabled=True`.
        striped : bool, optional
            Description: Alternates row backgrounds.
            Example: `striped=True`.
        loadingText : str, optional
            Description: Message shown while the table is fetching data.
            Example: `loadingText="Loading employees..."`.
        loaderType : str, optional
            Description: Loader variant forwarded to the Mantine loader.
            Example: `loaderType="dots"`.
        loaderColor : str, optional
            Description: Loader color token.
            Example: `loaderColor="blue"`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        Mapping props like `style`, `styles`, `classNames`, `tableProps`, and
        `scrollAreaProps` are merged with existing values instead of being
        replaced wholesale. Layout helpers also accept other canonical
        `DataTable` constructor keywords when that keeps a fluent chain more
        readable.

        Examples
        --------
        >>> table.update_layout(radius="lg", withTableBorder=True, striped=True)
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def update_table_properties(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update table behavior and styling properties using a more
        table-focused method name. This is useful when you want fluent chains
        to read like "layout", "columns", "rows", "selection", and so on.

        Parameters
        ----------
        withRowBorders : bool, optional
            Description: Toggles borders between body rows.
            Example: `withRowBorders=True`.
        withTableBorder : bool, optional
            Description: Toggles the outer border.
            Example: `withTableBorder=True`.
        withColumnBorders : bool, optional
            Description: Toggles borders between columns.
            Example: `withColumnBorders=False`.
        horizontalSpacing : str | int | float, optional
            Description: Horizontal cell padding.
            Expected inputs: Mantine spacing tokens such as `'xs'`, `'sm'`,
            `'md'`, `'lg'`, `'xl'`, or numeric values.
            Example: `horizontalSpacing="sm"`.
        verticalSpacing : str | int | float, optional
            Description: Vertical cell padding.
            Expected inputs: Mantine spacing tokens such as `'xs'`, `'sm'`,
            `'md'`, `'lg'`, `'xl'`, or numeric values.
            Example: `verticalSpacing="xs"`.
        verticalAlign : str, optional
            Description: Vertical alignment for cell content.
            Expected inputs: `'top'`, `'center'`, `'bottom'`.
            Example: `verticalAlign="center"`.
        striped : bool, optional
            Description: Alternates row backgrounds.
            Example: `striped=True`.
        highlightOnHover : bool, optional
            Description: Highlights the current row on hover.
            Example: `highlightOnHover=True`.
        stickyHeader : bool, optional
            Description: Keeps the header visible when the table scrolls.
            Example: `stickyHeader=True`.
        stickyHeaderOffset : str | int | float, optional
            Description: Offset used when sticky headers need to clear a fixed
            app header.
            Example: `stickyHeaderOffset=56`.
        noHeader : bool, optional
            Description: Hides the header row.
            Example: `noHeader=True`.
        textSelectionDisabled : bool, optional
            Description: Disables text selection inside the table.
            Example: `textSelectionDisabled=True`.
        defaultColumnProps : dict, optional
            Description: Shared defaults applied to every column unless a
            column overrides them.
            Example: `defaultColumnProps={"sortable": True}`.
        paginationSize : str | int | float, optional
            Description: Visual size of pagination controls.
            Expected inputs: Mantine size tokens such as `'xs'`, `'sm'`,
            `'md'`, `'lg'`, `'xl'`, or a numeric size when supported.
            Example: `paginationSize="sm"`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        This is functionally an alias of `update_layout()`. The separate name
        exists for readability in fluent chains, especially when you are
        grouping table shell props separately from column or row updates.

        Examples
        --------
        >>> table.update_table_properties(stickyHeader=True, verticalSpacing="xs")
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def update_columns(
        self,
        *columns: Any,
        selector: Any = None,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> "DataTable":
        """
        Description
        -----------
        Add new columns or update existing ones. This is the main helper for
        progressively shaping a table after the base `columns=[...]` list has
        been created.

        Parameters
        ----------
        *columns : Any
            Description: Column definitions to add or update. Each item may be
            an accessor string like `"salary"` or a full column dictionary.
            Example: `table.update_columns(Column("salary", sortable=True))`.
        selector : Any, optional
            Description: Accessor or collection of accessors identifying which
            existing columns should be updated.
            Example: `selector="salary"`.
        overwrite : bool, optional
            Description: Replaces matching columns instead of merging into the
            existing definition when `True`.
            Example: `overwrite=True`.
        title : str, optional
            Description: Replacement header label for the targeted columns.
            Example: `title="Annual Salary"`.
        presentation : str, optional
            Description: Built-in display mode for the targeted columns.
            Expected inputs: `'text'`, `'number'`, `'currency'`, `'date'`,
            `'datetime'`, `'badge'`, `'link'`, `'code'`, `'json'`, `'progress'`.
            Example: `presentation="currency"`.
        sortable : bool, optional
            Description: Enables sorting on the targeted columns.
            Example: `sortable=True`.
        textAlign : str, optional
            Description: Horizontal content alignment.
            Expected inputs: values accepted by Mantine/DataTable such as
            `'left'`, `'center'`, `'right'`.
            Example: `textAlign="right"`.
        width : str | int | float, optional
            Description: Column width.
            Example: `width=140`.
        editable : bool, optional
            Description: Enables double-click editing for the targeted columns.
            Example: `editable=True`.
        editor : Any, optional
            Description: In-place Dash editor component for editable columns.
            Example: `editor=dmc.NumberInput(min=0)`.
        render : Any, optional
            Description: Custom Dash content for cell rendering.
            Example: `render=dmc.Badge("Open")`.
        filter : Any, optional
            Description: Filter control rendered in the column's filter UI.
            Example: `filter=dmc.TextInput(placeholder="Search")`.
        cellsStyle : dict, optional
            Description: Cell-level inline style mapping.
            Example: `cellsStyle={"fontVariantNumeric": "tabular-nums"}`.
        titleStyle : dict, optional
            Description: Header-cell inline style mapping.
            Example: `titleStyle={"textTransform": "uppercase"}`.
        ellipsis : bool, optional
            Description: Truncates long cell content with ellipsis behavior.
            Example: `ellipsis=True`.
        draggable : bool, optional
            Description: Allows the targeted columns to be reordered.
            Example: `draggable=True`.
        toggleable : bool, optional
            Description: Allows the targeted columns to be shown or hidden.
            Example: `toggleable=True`.
        resizable : bool, optional
            Description: Allows the targeted columns to be resized.
            Example: `resizable=True`.
        defaultToggle : bool, optional
            Description: Initial visibility state for toggleable columns.
            Example: `defaultToggle=False`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        Nested mapping properties such as `style`, `titleStyle`, and
        `cellsStyle` are merged recursively for matching columns. If no match
        is found and the update includes an `accessor`, the column is
        appended. For the broader column-key surface, `update_columns()`
        accepts the same column fields documented by `Column(...)`.

        Examples
        --------
        >>> table.update_columns(selector="salary", title="Annual salary", width=140)
        DataTable(...)
        >>> table.update_columns({"accessor": "location", "hidden": True})
        DataTable(...)
        """
        current_columns = [
            _normalize_column(column) for column in (getattr(self, "columns", None) or [])
        ]

        updates: list[tuple[Any, dict[str, Any]]] = []
        for column in columns:
            normalized_column = _normalize_column(column)
            updates.append((selector or normalized_column.get("accessor"), normalized_column))

        if kwargs:
            updates.append((selector, deepcopy(kwargs)))

        for target_selector, update in updates:
            target_indexes = _column_indexes(current_columns, target_selector)
            if not target_indexes and target_selector is None and update.get("accessor"):
                target_indexes = _column_indexes(current_columns, update["accessor"])

            if not target_indexes:
                if update.get("accessor"):
                    current_columns.append(update)
                continue

            for index in target_indexes:
                existing = current_columns[index]
                if overwrite:
                    replacement = deepcopy(update)
                    if "accessor" not in replacement and "accessor" in existing:
                        replacement["accessor"] = existing["accessor"]
                    current_columns[index] = replacement
                    continue

                merged = deepcopy(existing)
                for key, value in update.items():
                    if key in _COLUMN_MERGE_PROPS and key in merged:
                        merged[key] = _merge_mapping(merged[key], value)
                    else:
                        merged[key] = deepcopy(value)
                current_columns[index] = merged

        self.columns = current_columns
        return self

    def group_columns(
        self,
        *groups: dict[str, Any],
        selector: Any = None,
        **kwargs: Any,
    ) -> "DataTable":
        """
        Description
        -----------
        Create or update grouped column headers. Use this when you want header
        rows that organize columns into sections like "Profile",
        "Compensation", or "Quarterly Metrics".

        Parameters
        ----------
        *groups : dict[str, Any]
            Description: Group definitions to append or apply to existing
            groups.
            Example: `table.group_columns(ColumnGroup("profile", columns=["name", "team"]))`.
        selector : Any, optional
            Description: Group id or collection of ids used to target existing
            groups for updates.
            Example: `selector="profile"`.
        title : str, optional
            Description: Visible label for the targeted group.
            Example: `title="Profile"`.
        columns : list[Any], optional
            Description: Column references or column dictionaries attached to
            the targeted group.
            Example: `columns=["name", "team"]`.
        groups : list[dict[str, Any]], optional
            Description: Nested child groups for multi-row grouped headers.
            Example: `groups=[ColumnGroup("cash", columns=["salary", "bonus"])]`.
        style : dict, optional
            Description: Inline style mapping for the group header.
            Example: `style={"textAlign": "center"}`.
        headerStyle : dict, optional
            Description: Header-specific style mapping for the group.
            Example: `headerStyle={"backgroundColor": "var(--mantine-color-gray-0)"}`.
        textAlign : str, optional
            Description: Alignment hint for header content.
            Expected inputs: values accepted by Mantine/DataTable such as
            `'left'`, `'center'`, `'right'`.
            Example: `textAlign="center"`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        When `columns` or nested `groups` are provided, this helper resolves
        accessor strings against the current column definitions so grouped
        headers stay in sync with the table's columns. The accepted group keys
        match the fields documented by `ColumnGroup(...)`.

        Examples
        --------
        >>> table.group_columns({"id": "profile", "columns": ["name", "team"]})
        DataTable(...)
        """
        existing_columns = [
            _normalize_column(column) for column in (getattr(self, "columns", None) or [])
        ]
        current_groups = [
            deepcopy(group) for group in (getattr(self, "groups", None) or [])
        ]

        if groups:
            resolved_groups = [_resolve_group(group, existing_columns) for group in groups]
            if selector is None:
                current_groups.extend(resolved_groups)
            else:
                target_indexes = _group_indexes(current_groups, selector)
                for index, group in zip(target_indexes, resolved_groups):
                    current_groups[index] = group

        if kwargs:
            update = deepcopy(kwargs)
            if "columns" in update and update["columns"] is not None:
                update["columns"] = [
                    _resolve_column_reference(column, existing_columns)
                    for column in update["columns"]
                ]
            if "groups" in update and update["groups"] is not None:
                update["groups"] = [
                    _resolve_group(group, existing_columns)
                    for group in update["groups"]
                ]

            for index in _group_indexes(current_groups, selector):
                current_groups[index] = _merge_mapping(current_groups[index], update)

        self.groups = current_groups
        return self

    def update_rows(self, selector: Any = None, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update row-level styling, metadata, expansion, or drag behavior. This
        is the main helper for conditional row rules such as "highlight all
        overdue rows" or "make platform rows clickable".

        Parameters
        ----------
        selector : Any, optional
            Description: Selector used for conditional rules. In practice this
            is usually a mapping of row fields to match.
            Example: `selector={"status": "Needs Review"}`.
        rowColor : str | dict | list, optional
            Description: Row text color or row-color rule.
            Example: `rowColor="red.8"`.
        color : str | dict | list, optional
            Description: Alias for `rowColor`.
            Example: `color="blue.8"`.
        rowBackgroundColor : str | dict | list, optional
            Description: Row background color or conditional background rule.
            Example: `rowBackgroundColor="yellow.0"`.
        backgroundColor : str | dict | list, optional
            Description: Alias for `rowBackgroundColor`.
            Example: `backgroundColor="green.0"`.
        rowClassName : str | dict | list, optional
            Description: CSS class name or conditional class rule for rows.
            Example: `rowClassName="row-warning"`.
        className : str | dict | list, optional
            Description: Alias for `rowClassName`.
            Example: `className="row-clickable"`.
        rowStyle : dict | list, optional
            Description: Inline style mapping or conditional row-style rule.
            Example: `rowStyle={"cursor": "pointer"}`.
        style : dict | list, optional
            Description: Alias for `rowStyle`.
            Example: `style={"fontWeight": 600}`.
        rowAttributes : dict | list, optional
            Description: Extra DOM attributes or conditional attribute rules.
            Example: `rowAttributes={"data-kind": "employee"}`.
        attributes : dict | list, optional
            Description: Alias for `rowAttributes`.
            Example: `attributes={"data-team": "platform"}`.
        rowDragging : bool | dict, optional
            Description: Enables table-level drag-and-drop row reordering.
            Example: `rowDragging=True`.
        draggable : bool | dict, optional
            Description: Alias for `rowDragging`.
            Example: `draggable=True`.
        idAccessor : str | dict | list[str], optional
            Description: Record identifier accessor used by selection and
            expansion.
            Example: `idAccessor="employeeId"`.
        expandedRecordIds : list[Any], optional
            Description: Controlled list of expanded row ids.
            Example: `expandedRecordIds=[1, 2]`.
        rowExpansion : dict, optional
            Description: Row-expansion configuration.
            Example: `rowExpansion=RowExpansionConfig(content="Details")`.
        rowBorderColor : str | dict, optional
            Description: Row border color override applied at the table level.
            Example: `rowBorderColor="gray.3"`.

        Returns
        -------
        DataTable
            The current instance.

        Raises
        ------
        TypeError
            If both a canonical row property and its alias are supplied, or if
            table-level properties such as `rowDragging` / `rowExpansion` are
            combined with a selector.

        Notes
        -----
        Conditional row props are stored as Dash-safe rule objects of the form
        `{"selector": ..., "value": ...}`. Unconditional updates overwrite
        static row props unless the property supports rule accumulation.

        Examples
        --------
        >>> table.update_rows(selector={"status": "Needs Review"}, backgroundColor="orange.0")
        DataTable(...)
        >>> table.update_rows(style={"cursor": "pointer"})
        DataTable(...)
        """
        for alias, canonical in _ROW_PROP_ALIASES.items():
            if alias in kwargs and canonical in kwargs:
                raise TypeError(f"Pass either {canonical} or {alias}, not both.")

        if "draggable" in kwargs:
            if selector is not None:
                raise TypeError("rowDragging is a table-level setting and does not accept a selector.")
            self.rowDragging = kwargs.pop("draggable")

        if "rowExpansion" in kwargs and selector is not None:
            raise TypeError("rowExpansion is a table-level setting and does not accept a selector.")

        if "idAccessor" in kwargs:
            id_accessor = kwargs.pop("idAccessor")
            if isinstance(id_accessor, (list, tuple)):
                self.idAccessor = {"accessors": list(id_accessor)}
            else:
                self.idAccessor = id_accessor

        normalized = deepcopy(kwargs)
        for alias, canonical in _ROW_PROP_ALIASES.items():
            if alias in normalized:
                normalized[canonical] = normalized.pop(alias)

        for key, value in normalized.items():
            if key in {"expandedRecordIds", "rowDragging", "rowExpansion"}:
                setattr(self, key, deepcopy(value))
                continue

            if key in {"rowAttributes", "rowBackgroundColor", "rowClassName", "rowColor", "rowStyle"}:
                current = getattr(self, key, None)
                setattr(self, key, _with_rule(key, current, value, selector))
                continue

            setattr(self, key, deepcopy(value))
        return self

    def add_interactivity(
        self,
        *,
        rowClick: bool = False,
        rowDoubleClick: bool = False,
        rowContextMenu: bool = False,
        cellClick: bool = False,
        cellDoubleClick: bool = False,
        cellContextMenu: bool = False,
        cellSelector: Any = None,
    ) -> "DataTable":
        """
        Description
        -----------
        Apply the visual cues that make a table feel interactive. This helper
        sets pointer cursors, enables hover highlighting when appropriate, and
        disables text selection so click targets feel intentional.

        Parameters
        ----------
        rowClick : bool, optional
            Description: Applies interactive row styling for single-click row
            handlers.
            Example: `rowClick=True`.
        rowDoubleClick : bool, optional
            Description: Applies interactive row styling for double-click row
            handlers.
            Example: `rowDoubleClick=True`.
        rowContextMenu : bool, optional
            Description: Applies interactive row styling for context-menu row
            handlers.
            Example: `rowContextMenu=True`.
        cellClick : bool, optional
            Description: Applies interactive styling to cells for click
            handlers.
            Example: `cellClick=True`.
        cellDoubleClick : bool, optional
            Description: Applies interactive styling to cells for double-click
            handlers.
            Example: `cellDoubleClick=True`.
        cellContextMenu : bool, optional
            Description: Applies interactive styling to cells for context-menu
            handlers.
            Example: `cellContextMenu=True`.
        cellSelector : Any, optional
            Description: Accessor or collection of accessors limiting which
            columns receive interactive cell styling.
            Example: `cellSelector=["name", "status"]`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        This helper configures presentation only. It does not register Dash
        callbacks by itself; you still need Dash callbacks that listen to the
        event payload props such as `rowClick` or `cellClick`.

        Examples
        --------
        >>> table.add_interactivity(rowClick=True, cellClick=True, cellSelector=["name"])
        DataTable(...)
        """
        if rowClick or rowDoubleClick or rowContextMenu:
            if getattr(self, "highlightOnHover", None) is None:
                self.highlightOnHover = True
            self.textSelectionDisabled = True
            self.update_rows(style={"cursor": "pointer"})

        if cellClick or cellDoubleClick or cellContextMenu:
            self.textSelectionDisabled = True
            selector = cellSelector
            columns = getattr(self, "columns", None)
            if selector is None and columns:
                selector = [column.get("accessor") for column in columns]
            self.update_columns(selector=selector, cellsStyle={"cursor": "pointer"})

        return self

    def update_selection(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update selection-related properties in place.

        Parameters
        ----------
        selectionTrigger : str, optional
            Description: Enables selection and decides how it is triggered.
            Expected inputs: `'cell'`, `'checkbox'`.
            Example: `selectionTrigger="checkbox"`.
        selectedRecordIds : list[Any], optional
            Description: Controlled ids for selected rows.
            Example: `selectedRecordIds=[1, 3]`.
        selectedRecords : list[dict], optional
            Description: Controlled record payloads for selected rows.
            Example: `selectedRecords=[{"id": 1, "name": "Avery"}]`.
        selectableRowRules : bool | dict | list, optional
            Description: Conditional rules that mark rows as selectable.
            Example: `selectableRowRules=[{"selector": {"active": True}, "value": True}]`.
        disabledSelectionRowRules : bool | dict | list, optional
            Description: Conditional rules that disable selection for matching
            rows.
            Example: `disabledSelectionRowRules=[{"selector": {"locked": True}, "value": True}]`.
        selectionCheckboxRules : dict | list, optional
            Description: Conditional props for row-selection checkboxes.
            Example: `selectionCheckboxRules=[{"selector": {"locked": True}, "value": {"disabled": True}}]`.
        selectionCheckboxProps : dict, optional
            Description: Shared props for row-selection checkboxes.
            Example: `selectionCheckboxProps={"size": "sm"}`.
        allRecordsSelectionCheckboxProps : dict, optional
            Description: Props for the header "select all" checkbox.
            Example: `allRecordsSelectionCheckboxProps={"aria-label": "Select all employees"}`.
        selectionColumnClassName : str, optional
            Description: CSS class for the selection column.
            Example: `selectionColumnClassName="table-selection-col"`.
        selectionColumnStyle : dict, optional
            Description: Inline styles for the selection column.
            Example: `selectionColumnStyle={"width": 44}`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        This is a convenience wrapper around the component props; it does not
        add extra selection logic beyond alias normalization and in-place
        updates.

        Examples
        --------
        >>> table.update_selection(selectionTrigger="checkbox", selectedRecordIds=[1])
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def update_pagination(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update pagination-related properties in place.

        Parameters
        ----------
        page : int | float, optional
            Description: Current page number.
            Example: `page=2`.
        pageSize : int | float, optional
            Description: Number of rows shown per page when using `pageSize`.
            Example: `pageSize=25`.
        recordsPerPage : int | float, optional
            Description: Number of rows shown per page when using
            `recordsPerPage`.
            Example: `recordsPerPage=25`.
        totalRecords : int | float, optional
            Description: Total number of available records.
            Example: `totalRecords=240`.
        recordsPerPageOptions : list[int | float], optional
            Description: Footer choices for rows per page.
            Example: `recordsPerPageOptions=[10, 25, 50, 100]`.
        pageSizeOptions : list[int | float], optional
            Description: Alternative prop for page-size choices.
            Example: `pageSizeOptions=[10, 25, 50]`.
        recordsPerPageLabel : str, optional
            Description: Label for the page-size control.
            Example: `recordsPerPageLabel="Rows"`.
        paginationSize : str | int | float, optional
            Description: Visual size of the pagination controls.
            Expected inputs: Mantine size tokens such as `'xs'`, `'sm'`,
            `'md'`, `'lg'`, `'xl'`, or a numeric size when supported.
            Example: `paginationSize="sm"`.
        paginationActiveTextColor : str | dict, optional
            Description: Text color for the active page button.
            Example: `paginationActiveTextColor="white"`.
        paginationActiveBackgroundColor : str | dict, optional
            Description: Background color for the active page button.
            Example: `paginationActiveBackgroundColor="blue.6"`.
        paginationWithEdges : bool, optional
            Description: Shows first/last page controls.
            Example: `paginationWithEdges=True`.
        paginationWithControls : bool, optional
            Description: Shows previous/next page controls.
            Example: `paginationWithControls=True`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        This helper is useful for both initial setup and controlled callback
        updates when the current page, size, or total count changes.

        Examples
        --------
        >>> table.update_pagination(page=2, totalRecords=240, recordsPerPage=25)
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def update_sorting(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update sorting-related properties in place.

        Parameters
        ----------
        sortStatus : dict, optional
            Description: Controlled sort descriptor, usually containing the
            active accessor and direction.
            Example: `sortStatus={"columnAccessor": "salary", "direction": "desc"}`.
        sortMode : str, optional
            Description: Chooses where sorting is handled.
            Expected inputs: `'client'`, `'server'`.
            Example: `sortMode="server"`.
        sortIcons : dict, optional
            Description: Custom icons or components for sorted/unsorted states.
            Example: `sortIcons={"sorted": dmc.Text("v"), "unsorted": dmc.Text("-")}`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        In server mode, this helper typically pairs with a Dash callback that
        reacts to `sortStatus` or `lastSortChange` and returns freshly sorted
        data.

        Examples
        --------
        >>> table.update_sorting(sortMode="server", sortStatus={"columnAccessor": "name", "direction": "asc"})
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def update_search(self, **kwargs: Any) -> "DataTable":
        """
        Description
        -----------
        Update search-related properties in place.

        Parameters
        ----------
        searchQuery : str, optional
            Description: Controlled search text.
            Example: `searchQuery="platform"`.
        searchMode : str, optional
            Description: Chooses where search filtering is handled.
            Expected inputs: `'client'`, `'server'`.
            Example: `searchMode="client"`.
        searchableAccessors : list[str], optional
            Description: Limits client-side search to specific record fields.
            Example: `searchableAccessors=["name", "team", "role"]`.

        Returns
        -------
        DataTable
            The current instance.

        Notes
        -----
        In server mode, this helper usually pairs with a Dash callback that
        fetches filtered rows from your backend.

        Examples
        --------
        >>> table.update_search(searchMode="client", searchQuery="platform")
        DataTable(...)
        """
        return self._update_props(**kwargs)

    def clear_selection(self) -> "DataTable":
        """
        Description
        -----------
        Clear all selected rows by resetting both selection payload props.

        Parameters
        ----------
        None.

        Returns
        -------
        DataTable
            The current instance with `selectedRecordIds` and
            `selectedRecords` reset to empty lists.

        Notes
        -----
        This is useful in callbacks after bulk actions, page changes, or
        filter changes when you want selection state to be explicitly cleared.

        Examples
        --------
        >>> table.clear_selection()
        DataTable(...)
        """
        self.selectedRecordIds = []
        self.selectedRecords = []
        return self

    def clear_expansion(self) -> "DataTable":
        """
        Description
        -----------
        Collapse all expanded rows by resetting `expandedRecordIds`.

        Parameters
        ----------
        None.

        Returns
        -------
        DataTable
            The current instance with `expandedRecordIds` reset to an empty
            list.

        Notes
        -----
        This is helpful after replacing the underlying dataset or when you
        want grouped/expanded state to restart from a clean slate.

        Examples
        --------
        >>> table.clear_expansion()
        DataTable(...)
        """
        self.expandedRecordIds = []
        return self


def _doc_parameter(
    name: str,
    *,
    kind=inspect.Parameter.KEYWORD_ONLY,
    default: Any = inspect.Signature.empty,
) -> inspect.Parameter:
    kwargs: dict[str, Any] = {"name": name, "kind": kind}
    if default is not inspect.Signature.empty:
        kwargs["default"] = default
    return inspect.Parameter(**kwargs)


def _set_doc_signature(target: Any, parameters: list[inspect.Parameter]) -> None:
    target.__signature__ = inspect.Signature(parameters)


_generated_datatable_init_parameters = [
    parameter
    for parameter in inspect.signature(_GeneratedDataTable.__init__).parameters.values()
    if parameter.kind != inspect.Parameter.VAR_KEYWORD
]

DataTable.__signature__ = inspect.Signature(_generated_datatable_init_parameters[1:])
DataTable.__init__.__signature__ = inspect.Signature(_generated_datatable_init_parameters)

Column.__signature__ = inspect.Signature(
    [
        _doc_parameter(
            "accessor",
            kind=inspect.Parameter.POSITIONAL_ONLY,
            default=None,
        ),
        _doc_parameter("title", default=None),
        _doc_parameter("presentation", default=None),
        _doc_parameter("sortable", default=None),
        _doc_parameter("editable", default=None),
        _doc_parameter("editor", default=None),
        _doc_parameter("render", default=None),
        _doc_parameter("filter", default=None),
        _doc_parameter("textAlign", default=None),
        _doc_parameter("width", default=None),
        _doc_parameter("cellsStyle", default=None),
        _doc_parameter("titleStyle", default=None),
        _doc_parameter("draggable", default=None),
        _doc_parameter("toggleable", default=None),
        _doc_parameter("resizable", default=None),
        _doc_parameter("defaultToggle", default=None),
    ]
)

ColumnGroup.__signature__ = inspect.Signature(
    [
        _doc_parameter(
            "group_id",
            kind=inspect.Parameter.POSITIONAL_ONLY,
            default=None,
        ),
        _doc_parameter("columns", default=None),
        _doc_parameter("groups", default=None),
        _doc_parameter("title", default=None),
        _doc_parameter("style", default=None),
        _doc_parameter("headerStyle", default=None),
        _doc_parameter("textAlign", default=None),
    ]
)

SelectionConfig.__signature__ = inspect.Signature(
    [
        _doc_parameter("selectionTrigger", default=None),
        _doc_parameter("selectedRecordIds", default=None),
        _doc_parameter("selectedRecords", default=None),
        _doc_parameter("selectableRowRules", default=None),
        _doc_parameter("disabledSelectionRowRules", default=None),
        _doc_parameter("selectionCheckboxRules", default=None),
        _doc_parameter("selectionCheckboxProps", default=None),
        _doc_parameter("allRecordsSelectionCheckboxProps", default=None),
        _doc_parameter("selectionColumnClassName", default=None),
        _doc_parameter("selectionColumnStyle", default=None),
    ]
)

PaginationConfig.__signature__ = inspect.Signature(
    [
        _doc_parameter("page", default=None),
        _doc_parameter("pageSize", default=None),
        _doc_parameter("recordsPerPage", default=None),
        _doc_parameter("totalRecords", default=None),
        _doc_parameter("recordsPerPageOptions", default=None),
        _doc_parameter("pageSizeOptions", default=None),
        _doc_parameter("recordsPerPageLabel", default=None),
        _doc_parameter("paginationSize", default=None),
        _doc_parameter("paginationActiveTextColor", default=None),
        _doc_parameter("paginationActiveBackgroundColor", default=None),
        _doc_parameter("paginationWithEdges", default=None),
        _doc_parameter("paginationWithControls", default=None),
    ]
)

RowExpansionConfig.__signature__ = inspect.Signature(
    [
        _doc_parameter(
            "content",
            kind=inspect.Parameter.POSITIONAL_ONLY,
            default=None,
        ),
        _doc_parameter("allowMultiple", default=None),
        _doc_parameter("trigger", default=None),
    ]
)

_set_doc_signature(
    DataTable.update_layout,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("radius", default=None),
        _doc_parameter("direction", default=None),
        _doc_parameter("height", default=None),
        _doc_parameter("minHeight", default=None),
        _doc_parameter("maxHeight", default=None),
        _doc_parameter("bg", default=None),
        _doc_parameter("style", default=None),
        _doc_parameter("className", default=None),
        _doc_parameter("tableProps", default=None),
        _doc_parameter("scrollAreaProps", default=None),
        _doc_parameter("withTableBorder", default=None),
        _doc_parameter("withColumnBorders", default=None),
        _doc_parameter("striped", default=None),
        _doc_parameter("pinFirstColumn", default=None),
        _doc_parameter("pinLastColumn", default=None),
        _doc_parameter("textSelectionDisabled", default=None),
        _doc_parameter("loadingText", default=None),
        _doc_parameter("loaderType", default=None),
        _doc_parameter("loaderColor", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_table_properties,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("withRowBorders", default=None),
        _doc_parameter("withTableBorder", default=None),
        _doc_parameter("withColumnBorders", default=None),
        _doc_parameter("horizontalSpacing", default=None),
        _doc_parameter("verticalSpacing", default=None),
        _doc_parameter("verticalAlign", default=None),
        _doc_parameter("striped", default=None),
        _doc_parameter("highlightOnHover", default=None),
        _doc_parameter("stickyHeader", default=None),
        _doc_parameter("stickyHeaderOffset", default=None),
        _doc_parameter("noHeader", default=None),
        _doc_parameter("textSelectionDisabled", default=None),
        _doc_parameter("defaultColumnProps", default=None),
        _doc_parameter("paginationSize", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_columns,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("columns", kind=inspect.Parameter.VAR_POSITIONAL),
        _doc_parameter("selector", default=None),
        _doc_parameter("overwrite", default=False),
        _doc_parameter("title", default=None),
        _doc_parameter("presentation", default=None),
        _doc_parameter("sortable", default=None),
        _doc_parameter("textAlign", default=None),
        _doc_parameter("width", default=None),
        _doc_parameter("editable", default=None),
        _doc_parameter("editor", default=None),
        _doc_parameter("render", default=None),
        _doc_parameter("filter", default=None),
        _doc_parameter("cellsStyle", default=None),
        _doc_parameter("titleStyle", default=None),
        _doc_parameter("ellipsis", default=None),
        _doc_parameter("draggable", default=None),
        _doc_parameter("toggleable", default=None),
        _doc_parameter("resizable", default=None),
        _doc_parameter("defaultToggle", default=None),
    ],
)

_set_doc_signature(
    DataTable.group_columns,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("group_defs", kind=inspect.Parameter.VAR_POSITIONAL),
        _doc_parameter("selector", default=None),
        _doc_parameter("title", default=None),
        _doc_parameter("columns", default=None),
        _doc_parameter("groups", default=None),
        _doc_parameter("style", default=None),
        _doc_parameter("headerStyle", default=None),
        _doc_parameter("textAlign", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_rows,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("selector", default=None),
        _doc_parameter("rowColor", default=None),
        _doc_parameter("color", default=None),
        _doc_parameter("rowBackgroundColor", default=None),
        _doc_parameter("backgroundColor", default=None),
        _doc_parameter("rowClassName", default=None),
        _doc_parameter("className", default=None),
        _doc_parameter("rowStyle", default=None),
        _doc_parameter("style", default=None),
        _doc_parameter("rowAttributes", default=None),
        _doc_parameter("attributes", default=None),
        _doc_parameter("rowDragging", default=None),
        _doc_parameter("draggable", default=None),
        _doc_parameter("idAccessor", default=None),
        _doc_parameter("expandedRecordIds", default=None),
        _doc_parameter("rowExpansion", default=None),
        _doc_parameter("rowBorderColor", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_selection,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("selectionTrigger", default=None),
        _doc_parameter("selectedRecordIds", default=None),
        _doc_parameter("selectedRecords", default=None),
        _doc_parameter("selectableRowRules", default=None),
        _doc_parameter("disabledSelectionRowRules", default=None),
        _doc_parameter("selectionCheckboxRules", default=None),
        _doc_parameter("selectionCheckboxProps", default=None),
        _doc_parameter("allRecordsSelectionCheckboxProps", default=None),
        _doc_parameter("selectionColumnClassName", default=None),
        _doc_parameter("selectionColumnStyle", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_pagination,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("page", default=None),
        _doc_parameter("pageSize", default=None),
        _doc_parameter("recordsPerPage", default=None),
        _doc_parameter("totalRecords", default=None),
        _doc_parameter("recordsPerPageOptions", default=None),
        _doc_parameter("pageSizeOptions", default=None),
        _doc_parameter("recordsPerPageLabel", default=None),
        _doc_parameter("paginationSize", default=None),
        _doc_parameter("paginationActiveTextColor", default=None),
        _doc_parameter("paginationActiveBackgroundColor", default=None),
        _doc_parameter("paginationWithEdges", default=None),
        _doc_parameter("paginationWithControls", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_sorting,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("sortStatus", default=None),
        _doc_parameter("sortMode", default=None),
        _doc_parameter("sortIcons", default=None),
    ],
)

_set_doc_signature(
    DataTable.update_search,
    [
        _doc_parameter("self", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD),
        _doc_parameter("searchQuery", default=None),
        _doc_parameter("searchMode", default=None),
        _doc_parameter("searchableAccessors", default=None),
    ],
)


__all__ = [
    "Column",
    "ColumnGroup",
    "DataTable",
    "PaginationConfig",
    "RowExpansionConfig",
    "SelectionConfig",
]

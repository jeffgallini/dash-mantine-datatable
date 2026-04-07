from __future__ import annotations

from copy import deepcopy
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
    return _compact_mapping(deepcopy(kwargs))


def PaginationConfig(**kwargs: Any) -> dict[str, Any]:
    return _compact_mapping(deepcopy(kwargs))


def RowExpansionConfig(content: Any = None, /, **kwargs: Any) -> dict[str, Any]:
    config = deepcopy(kwargs)
    if content is not None:
        config["content"] = content
    return _compact_mapping(config)


class DataTable(_GeneratedDataTable):
    """Dash Mantine DataTable wrapper with chainable Python-side helpers."""

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
        normalized = _normalize_kwargs(kwargs)
        super().__init__(*args, **normalized)

    def _update_props(self, **kwargs: Any) -> "DataTable":
        normalized = _normalize_kwargs(kwargs)
        for key, value in normalized.items():
            current = getattr(self, key, None)
            if key in _MERGED_MAPPING_PROPS and current is not None:
                setattr(self, key, _merge_mapping(current, value))
            else:
                setattr(self, key, deepcopy(value))
        return self

    def update_layout(self, **kwargs: Any) -> "DataTable":
        return self._update_props(**kwargs)

    def update_table_properties(self, **kwargs: Any) -> "DataTable":
        return self._update_props(**kwargs)

    def update_columns(
        self,
        *columns: Any,
        selector: Any = None,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> "DataTable":
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
        return self._update_props(**kwargs)

    def update_pagination(self, **kwargs: Any) -> "DataTable":
        return self._update_props(**kwargs)

    def update_sorting(self, **kwargs: Any) -> "DataTable":
        return self._update_props(**kwargs)

    def update_search(self, **kwargs: Any) -> "DataTable":
        return self._update_props(**kwargs)

    def clear_selection(self) -> "DataTable":
        self.selectedRecordIds = []
        self.selectedRecords = []
        return self

    def clear_expansion(self) -> "DataTable":
        self.expandedRecordIds = []
        return self


__all__ = [
    "Column",
    "ColumnGroup",
    "DataTable",
    "PaginationConfig",
    "RowExpansionConfig",
    "SelectionConfig",
]

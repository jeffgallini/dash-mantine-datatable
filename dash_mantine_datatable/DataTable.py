# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class DataTable(Component):
    """A DataTable component.


Keyword arguments:

- id (string | dict; optional):
    The ID used to identify this component in Dash callbacks.

- allRecordsSelectionCheckboxProps (dict; optional)

- backgroundColor (string | dict; optional)

- bd (string | number; optional)

- bdrs (string | number; optional)

- bg (string | dict; optional)

- bga (string; optional)

- bgp (string; optional)

- bgr (string; optional)

- bgsz (string; optional)

- bodyRef (boolean | number | string | dict | list; optional)

- borderColor (string | dict; optional)

- borderRadius (string | number; optional)

- bottom (string | number; optional)

- c (string | dict; optional)

- cellClick (dict; optional)

- cellContextMenu (dict; optional)

- cellDoubleClick (dict; optional)

- childRowsAccessor (string; default undefined):
    Nested child-record accessor for already hierarchical data. When
    set, rows with this accessor render inline child rows using the
    same indentation and expand/collapse affordance as `groupBy`.

- className (string; optional)

- classNames (dict; optional)

- columns (list of dicts; optional):
    Column definitions. Each column may also define a Dash-friendly
    `presentation` such as `text`, `number`, `currency`, `date`,
    `datetime`, `badge`, `link`, `code`, `json` or `progress`. Set
    `editable=True` to enable double-click editing, and pass a Dash
    input component to `editor` when you want a custom in-place
    editor.

- customLoader (boolean | number | string | dict | list; optional)

- data (list of dicts; optional):
    Table records. `data` is the preferred Dash-facing alias.

- defaultColumnProps (dict; optional)

- defaultColumnRender (boolean | number | string | dict | list; optional)

- direction (a value equal to: 'ltr', 'rtl'; default 'ltr'):
    Layout direction. Set to `rtl` to render the table in a
    right-to-left Mantine direction context.

- disabledSelectionRowRules (boolean | dict | list; optional)

- display (string; optional)

- emptyState (string | dict; optional)

- expandedRecordIds (list; optional)

- fetching (boolean; optional)

- ff (string; optional)

- flex (string | number; optional)

- fs (string; optional)

- fw (string | number; optional)

- fz (string | number; optional)

- groupAggregations (dict; default undefined):
    Per-column aggregation mapping for parent rows. Values may be one
    of the built-in aggregations (`sum`, `mean`, `median`, `min`,
    `max`, `count`) or a custom client-side function / function source
    string.

- groupBy (string | list of strings; default undefined):
    Row grouping accessor or accessors. Grouped rows render inline
    nested parents inside a single table, while leaf rows can still
    use `rowExpansion` for detail panels.

- groups (list of dicts; default undefined):
    Optional column groups matching Mantine DataTable grouped headers.

- h (string | number; optional)

- height (string | number; optional)

- hiddenFrom (string; optional)

- highlightOnHover (boolean; default True)

- highlightOnHoverColor (string | dict; optional)

- horizontalSpacing (string | number; optional)

- idAccessor (string | dict | list of strings; default 'id'):
    Record identifier accessor. Defaults to `id`.

- inset (string | number; optional)

- lastExpansionChange (dict; optional)

- lastRowDragChange (dict; optional)

- lastSelectionChange (dict; optional)

- lastSortChange (dict; optional)

- left (string | number; optional)

- lh (string | number; optional)

- loaderBackgroundBlur (number; optional)

- loaderColor (string; optional)

- loaderSize (string | number; optional)

- loaderType (string; optional)

- loadingText (string; optional)

- locale (string; default 'en-US'):
    Locale used for number and date formatting.

- lts (string | number; optional)

- m (string | number; optional)

- mah (string | number; optional)

- maw (string | number; optional)

- maxHeight (string | number; optional)

- mb (string | number; optional)

- me (string | number; optional)

- mih (string | number; optional)

- minHeight (string | number; optional)

- miw (string | number; optional)

- ml (string | number; optional)

- mr (string | number; optional)

- ms (string | number; optional)

- mt (string | number; optional)

- mx (string | number; optional)

- my (string | number; optional)

- noHeader (boolean; optional)

- noRecordsIcon (boolean | number | string | dict | list; optional)

- noRecordsText (string; default 'No records found')

- opacity (string | number; optional)

- p (string | number; optional)

- page (number; optional)

- pageSize (number; default 10)

- pageSizeOptions (list of numbers; default [10, 25, 50])

- pagination (dict; optional)

- paginationActiveBackgroundColor (string | dict; optional)

- paginationActiveTextColor (string | dict; optional)

- paginationMode (a value equal to: 'client', 'server', 'none'; default 'client')

- paginationSize (string | number; default 'sm')

- paginationWithControls (boolean; optional)

- paginationWithEdges (boolean; optional)

- pb (string | number; optional)

- pe (string | number; optional)

- pinFirstColumn (boolean; optional)

- pinLastColumn (boolean; optional)

- pl (string | number; optional)

- pos (string; optional)

- pr (string | number; optional)

- ps (string | number; optional)

- pt (string | number; optional)

- px (string | number; optional)

- py (string | number; optional)

- radius (string | number; optional)

- records (list of dicts; optional):
    Optional alias for `data`, matching the original Mantine DataTable
    API.

- recordsPerPage (number; default 10)

- recordsPerPageLabel (string; default 'Rows per page')

- recordsPerPageOptions (list of numbers; default undefined)

- right (string | number; optional)

- rowAttributes (dict | list; optional)

- rowBackgroundColor (string | dict | list; optional):
    Row background color. Accepts a static color or Dash-safe rule
    objects.

- rowBorderColor (string | dict; optional)

- rowClassName (string | dict | list; optional):
    Row class names. Accepts a static className or Dash-safe rule
    objects.

- rowClick (dict; optional)

- rowColor (string | dict | list; optional):
    Row text color. Accepts a static Mantine color or Dash-safe rule
    objects.

- rowContextMenu (dict; optional)

- rowDoubleClick (dict; optional)

- rowDragging (boolean | dict; optional):
    Enables Dash-native row reordering. Pass `True` or a configuration
    object. The reordered list is written back to both `data` and
    `records`, and the latest drag payload is exposed through
    `lastRowDragChange`.

- rowExpansion (dict; optional)

- rowStyle (dict | list; optional):
    Row inline styles. Accepts a static style object or Dash-safe rule
    objects.

- scrollAreaProps (dict; optional)

- scrollEdge (dict; optional)

- scrollPosition (dict; optional)

- searchMode (a value equal to: 'client', 'server'; default 'client')

- searchQuery (string; optional)

- searchableAccessors (list of strings; optional)

- selectableRowRules (boolean | dict | list; optional)

- selectedRecordIds (list; optional)

- selectedRecords (list; optional)

- selectionCheckboxProps (dict; optional)

- selectionCheckboxRules (dict | list; optional)

- selectionColumnClassName (string; optional)

- selectionColumnStyle (dict; optional)

- selectionTrigger (a value equal to: 'cell', 'checkbox'; default undefined)

- shadow (string; optional)

- sortIcons (dict; optional)

- sortMode (a value equal to: 'client', 'server'; default 'client')

- sortStatus (dict; optional)

- stickyHeader (boolean; optional)

- stickyHeaderOffset (string | number; optional)

- storeColumnsKey (string; optional):
    Local-storage key used by Mantine DataTable to persist draggable /
    toggleable / resizable column state.

- striped (boolean; default False)

- stripedColor (string | dict; optional)

- styles (dict; optional)

- ta (string; optional)

- tableClassName (string; optional)

- tableProps (dict; optional)

- tableRef (boolean | number | string | dict | list; optional)

- td (string; optional)

- textSelectionDisabled (boolean; default False)

- top (string | number; optional)

- totalRecords (number; optional)

- tt (string; optional)

- verticalAlign (a value equal to: 'top', 'center', 'bottom'; optional)

- verticalSpacing (string | number; optional)

- visibleFrom (string; optional)

- w (string | number; optional)

- withColumnBorders (boolean; default False)

- withRowBorders (boolean; default True)

- withTableBorder (boolean; default True)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_datatable'
    _type = 'DataTable'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        data: typing.Optional[typing.Sequence[dict]] = None,
        records: typing.Optional[typing.Sequence[dict]] = None,
        columns: typing.Optional[typing.Sequence[dict]] = None,
        groups: typing.Optional[typing.Sequence[dict]] = None,
        groupBy: typing.Optional[typing.Union[str, typing.Sequence[str]]] = None,
        childRowsAccessor: typing.Optional[str] = None,
        groupAggregations: typing.Optional[dict] = None,
        idAccessor: typing.Optional[typing.Union[str, dict, typing.Sequence[str]]] = None,
        locale: typing.Optional[str] = None,
        direction: typing.Optional[Literal["ltr", "rtl"]] = None,
        paginationMode: typing.Optional[Literal["client", "server", "none"]] = None,
        sortMode: typing.Optional[Literal["client", "server"]] = None,
        searchMode: typing.Optional[Literal["client", "server"]] = None,
        searchQuery: typing.Optional[str] = None,
        searchableAccessors: typing.Optional[typing.Sequence[str]] = None,
        page: typing.Optional[NumberType] = None,
        recordsPerPage: typing.Optional[NumberType] = None,
        pageSize: typing.Optional[NumberType] = None,
        totalRecords: typing.Optional[NumberType] = None,
        sortStatus: typing.Optional[dict] = None,
        selectedRecordIds: typing.Optional[typing.Sequence] = None,
        selectedRecords: typing.Optional[typing.Sequence] = None,
        expandedRecordIds: typing.Optional[typing.Sequence] = None,
        selectionTrigger: typing.Optional[Literal["cell", "checkbox"]] = None,
        selectionColumnClassName: typing.Optional[str] = None,
        selectionColumnStyle: typing.Optional[dict] = None,
        selectionCheckboxProps: typing.Optional[dict] = None,
        allRecordsSelectionCheckboxProps: typing.Optional[dict] = None,
        selectableRowRules: typing.Optional[typing.Union[bool, dict, typing.Sequence]] = None,
        disabledSelectionRowRules: typing.Optional[typing.Union[bool, dict, typing.Sequence]] = None,
        selectionCheckboxRules: typing.Optional[typing.Union[dict, typing.Sequence]] = None,
        rowDragging: typing.Optional[typing.Union[bool, dict]] = None,
        rowColor: typing.Optional[typing.Union[str, dict, typing.Sequence]] = None,
        rowBackgroundColor: typing.Optional[typing.Union[str, dict, typing.Sequence]] = None,
        rowClassName: typing.Optional[typing.Union[str, dict, typing.Sequence]] = None,
        rowAttributes: typing.Optional[typing.Union[dict, typing.Sequence]] = None,
        rowStyle: typing.Optional[typing.Union[dict, typing.Sequence]] = None,
        rowExpansion: typing.Optional[dict] = None,
        rowClick: typing.Optional[dict] = None,
        rowDoubleClick: typing.Optional[dict] = None,
        rowContextMenu: typing.Optional[dict] = None,
        cellClick: typing.Optional[dict] = None,
        cellDoubleClick: typing.Optional[dict] = None,
        cellContextMenu: typing.Optional[dict] = None,
        pagination: typing.Optional[dict] = None,
        scrollPosition: typing.Optional[dict] = None,
        scrollEdge: typing.Optional[dict] = None,
        lastRowDragChange: typing.Optional[dict] = None,
        lastSortChange: typing.Optional[dict] = None,
        lastSelectionChange: typing.Optional[dict] = None,
        lastExpansionChange: typing.Optional[dict] = None,
        emptyState: typing.Optional[typing.Union[str, dict]] = None,
        noRecordsIcon: typing.Optional[typing.Any] = None,
        noRecordsText: typing.Optional[str] = None,
        recordsPerPageOptions: typing.Optional[typing.Sequence[NumberType]] = None,
        pageSizeOptions: typing.Optional[typing.Sequence[NumberType]] = None,
        recordsPerPageLabel: typing.Optional[str] = None,
        paginationSize: typing.Optional[typing.Union[str, NumberType]] = None,
        paginationActiveTextColor: typing.Optional[typing.Union[str, dict]] = None,
        paginationActiveBackgroundColor: typing.Optional[typing.Union[str, dict]] = None,
        loadingText: typing.Optional[str] = None,
        tableProps: typing.Optional[dict] = None,
        scrollAreaProps: typing.Optional[dict] = None,
        className: typing.Optional[str] = None,
        tableClassName: typing.Optional[str] = None,
        classNames: typing.Optional[dict] = None,
        style: typing.Optional[typing.Any] = None,
        styles: typing.Optional[dict] = None,
        radius: typing.Optional[typing.Union[str, NumberType]] = None,
        height: typing.Optional[typing.Union[str, NumberType]] = None,
        minHeight: typing.Optional[typing.Union[str, NumberType]] = None,
        maxHeight: typing.Optional[typing.Union[str, NumberType]] = None,
        shadow: typing.Optional[str] = None,
        bg: typing.Optional[typing.Union[str, dict]] = None,
        c: typing.Optional[typing.Union[str, dict]] = None,
        backgroundColor: typing.Optional[typing.Union[str, dict]] = None,
        borderColor: typing.Optional[typing.Union[str, dict]] = None,
        rowBorderColor: typing.Optional[typing.Union[str, dict]] = None,
        stripedColor: typing.Optional[typing.Union[str, dict]] = None,
        highlightOnHoverColor: typing.Optional[typing.Union[str, dict]] = None,
        withRowBorders: typing.Optional[bool] = None,
        withTableBorder: typing.Optional[bool] = None,
        withColumnBorders: typing.Optional[bool] = None,
        horizontalSpacing: typing.Optional[typing.Union[str, NumberType]] = None,
        verticalSpacing: typing.Optional[typing.Union[str, NumberType]] = None,
        borderRadius: typing.Optional[typing.Union[str, NumberType]] = None,
        striped: typing.Optional[bool] = None,
        highlightOnHover: typing.Optional[bool] = None,
        textSelectionDisabled: typing.Optional[bool] = None,
        fetching: typing.Optional[bool] = None,
        loaderBackgroundBlur: typing.Optional[NumberType] = None,
        loaderSize: typing.Optional[typing.Union[str, NumberType]] = None,
        loaderType: typing.Optional[str] = None,
        loaderColor: typing.Optional[str] = None,
        customLoader: typing.Optional[typing.Any] = None,
        noHeader: typing.Optional[bool] = None,
        pinFirstColumn: typing.Optional[bool] = None,
        pinLastColumn: typing.Optional[bool] = None,
        stickyHeader: typing.Optional[bool] = None,
        stickyHeaderOffset: typing.Optional[typing.Union[str, NumberType]] = None,
        verticalAlign: typing.Optional[Literal["top", "center", "bottom"]] = None,
        paginationWithEdges: typing.Optional[bool] = None,
        paginationWithControls: typing.Optional[bool] = None,
        storeColumnsKey: typing.Optional[str] = None,
        defaultColumnProps: typing.Optional[dict] = None,
        defaultColumnRender: typing.Optional[typing.Any] = None,
        sortIcons: typing.Optional[dict] = None,
        bodyRef: typing.Optional[typing.Any] = None,
        tableRef: typing.Optional[typing.Any] = None,
        m: typing.Optional[typing.Union[str, NumberType]] = None,
        mx: typing.Optional[typing.Union[str, NumberType]] = None,
        my: typing.Optional[typing.Union[str, NumberType]] = None,
        mt: typing.Optional[typing.Union[str, NumberType]] = None,
        mb: typing.Optional[typing.Union[str, NumberType]] = None,
        ms: typing.Optional[typing.Union[str, NumberType]] = None,
        me: typing.Optional[typing.Union[str, NumberType]] = None,
        ml: typing.Optional[typing.Union[str, NumberType]] = None,
        mr: typing.Optional[typing.Union[str, NumberType]] = None,
        p: typing.Optional[typing.Union[str, NumberType]] = None,
        px: typing.Optional[typing.Union[str, NumberType]] = None,
        py: typing.Optional[typing.Union[str, NumberType]] = None,
        pt: typing.Optional[typing.Union[str, NumberType]] = None,
        pb: typing.Optional[typing.Union[str, NumberType]] = None,
        ps: typing.Optional[typing.Union[str, NumberType]] = None,
        pe: typing.Optional[typing.Union[str, NumberType]] = None,
        pl: typing.Optional[typing.Union[str, NumberType]] = None,
        pr: typing.Optional[typing.Union[str, NumberType]] = None,
        w: typing.Optional[typing.Union[str, NumberType]] = None,
        miw: typing.Optional[typing.Union[str, NumberType]] = None,
        maw: typing.Optional[typing.Union[str, NumberType]] = None,
        h: typing.Optional[typing.Union[str, NumberType]] = None,
        mih: typing.Optional[typing.Union[str, NumberType]] = None,
        mah: typing.Optional[typing.Union[str, NumberType]] = None,
        opacity: typing.Optional[typing.Union[str, NumberType]] = None,
        ff: typing.Optional[str] = None,
        fz: typing.Optional[typing.Union[str, NumberType]] = None,
        fw: typing.Optional[typing.Union[str, NumberType]] = None,
        lts: typing.Optional[typing.Union[str, NumberType]] = None,
        ta: typing.Optional[str] = None,
        lh: typing.Optional[typing.Union[str, NumberType]] = None,
        fs: typing.Optional[str] = None,
        tt: typing.Optional[str] = None,
        display: typing.Optional[str] = None,
        flex: typing.Optional[typing.Union[str, NumberType]] = None,
        bd: typing.Optional[typing.Union[str, NumberType]] = None,
        bdrs: typing.Optional[typing.Union[str, NumberType]] = None,
        td: typing.Optional[str] = None,
        bgsz: typing.Optional[str] = None,
        bgp: typing.Optional[str] = None,
        bgr: typing.Optional[str] = None,
        bga: typing.Optional[str] = None,
        pos: typing.Optional[str] = None,
        top: typing.Optional[typing.Union[str, NumberType]] = None,
        left: typing.Optional[typing.Union[str, NumberType]] = None,
        bottom: typing.Optional[typing.Union[str, NumberType]] = None,
        right: typing.Optional[typing.Union[str, NumberType]] = None,
        inset: typing.Optional[typing.Union[str, NumberType]] = None,
        hiddenFrom: typing.Optional[str] = None,
        visibleFrom: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'allRecordsSelectionCheckboxProps', 'backgroundColor', 'bd', 'bdrs', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bodyRef', 'borderColor', 'borderRadius', 'bottom', 'c', 'cellClick', 'cellContextMenu', 'cellDoubleClick', 'childRowsAccessor', 'className', 'classNames', 'columns', 'customLoader', 'data', 'defaultColumnProps', 'defaultColumnRender', 'direction', 'disabledSelectionRowRules', 'display', 'emptyState', 'expandedRecordIds', 'fetching', 'ff', 'flex', 'fs', 'fw', 'fz', 'groupAggregations', 'groupBy', 'groups', 'h', 'height', 'hiddenFrom', 'highlightOnHover', 'highlightOnHoverColor', 'horizontalSpacing', 'idAccessor', 'inset', 'lastExpansionChange', 'lastRowDragChange', 'lastSelectionChange', 'lastSortChange', 'left', 'lh', 'loaderBackgroundBlur', 'loaderColor', 'loaderSize', 'loaderType', 'loadingText', 'locale', 'lts', 'm', 'mah', 'maw', 'maxHeight', 'mb', 'me', 'mih', 'minHeight', 'miw', 'ml', 'mr', 'ms', 'mt', 'mx', 'my', 'noHeader', 'noRecordsIcon', 'noRecordsText', 'opacity', 'p', 'page', 'pageSize', 'pageSizeOptions', 'pagination', 'paginationActiveBackgroundColor', 'paginationActiveTextColor', 'paginationMode', 'paginationSize', 'paginationWithControls', 'paginationWithEdges', 'pb', 'pe', 'pinFirstColumn', 'pinLastColumn', 'pl', 'pos', 'pr', 'ps', 'pt', 'px', 'py', 'radius', 'records', 'recordsPerPage', 'recordsPerPageLabel', 'recordsPerPageOptions', 'right', 'rowAttributes', 'rowBackgroundColor', 'rowBorderColor', 'rowClassName', 'rowClick', 'rowColor', 'rowContextMenu', 'rowDoubleClick', 'rowDragging', 'rowExpansion', 'rowStyle', 'scrollAreaProps', 'scrollEdge', 'scrollPosition', 'searchMode', 'searchQuery', 'searchableAccessors', 'selectableRowRules', 'selectedRecordIds', 'selectedRecords', 'selectionCheckboxProps', 'selectionCheckboxRules', 'selectionColumnClassName', 'selectionColumnStyle', 'selectionTrigger', 'shadow', 'sortIcons', 'sortMode', 'sortStatus', 'stickyHeader', 'stickyHeaderOffset', 'storeColumnsKey', 'striped', 'stripedColor', 'style', 'styles', 'ta', 'tableClassName', 'tableProps', 'tableRef', 'td', 'textSelectionDisabled', 'top', 'totalRecords', 'tt', 'verticalAlign', 'verticalSpacing', 'visibleFrom', 'w', 'withColumnBorders', 'withRowBorders', 'withTableBorder']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allRecordsSelectionCheckboxProps', 'backgroundColor', 'bd', 'bdrs', 'bg', 'bga', 'bgp', 'bgr', 'bgsz', 'bodyRef', 'borderColor', 'borderRadius', 'bottom', 'c', 'cellClick', 'cellContextMenu', 'cellDoubleClick', 'childRowsAccessor', 'className', 'classNames', 'columns', 'customLoader', 'data', 'defaultColumnProps', 'defaultColumnRender', 'direction', 'disabledSelectionRowRules', 'display', 'emptyState', 'expandedRecordIds', 'fetching', 'ff', 'flex', 'fs', 'fw', 'fz', 'groupAggregations', 'groupBy', 'groups', 'h', 'height', 'hiddenFrom', 'highlightOnHover', 'highlightOnHoverColor', 'horizontalSpacing', 'idAccessor', 'inset', 'lastExpansionChange', 'lastRowDragChange', 'lastSelectionChange', 'lastSortChange', 'left', 'lh', 'loaderBackgroundBlur', 'loaderColor', 'loaderSize', 'loaderType', 'loadingText', 'locale', 'lts', 'm', 'mah', 'maw', 'maxHeight', 'mb', 'me', 'mih', 'minHeight', 'miw', 'ml', 'mr', 'ms', 'mt', 'mx', 'my', 'noHeader', 'noRecordsIcon', 'noRecordsText', 'opacity', 'p', 'page', 'pageSize', 'pageSizeOptions', 'pagination', 'paginationActiveBackgroundColor', 'paginationActiveTextColor', 'paginationMode', 'paginationSize', 'paginationWithControls', 'paginationWithEdges', 'pb', 'pe', 'pinFirstColumn', 'pinLastColumn', 'pl', 'pos', 'pr', 'ps', 'pt', 'px', 'py', 'radius', 'records', 'recordsPerPage', 'recordsPerPageLabel', 'recordsPerPageOptions', 'right', 'rowAttributes', 'rowBackgroundColor', 'rowBorderColor', 'rowClassName', 'rowClick', 'rowColor', 'rowContextMenu', 'rowDoubleClick', 'rowDragging', 'rowExpansion', 'rowStyle', 'scrollAreaProps', 'scrollEdge', 'scrollPosition', 'searchMode', 'searchQuery', 'searchableAccessors', 'selectableRowRules', 'selectedRecordIds', 'selectedRecords', 'selectionCheckboxProps', 'selectionCheckboxRules', 'selectionColumnClassName', 'selectionColumnStyle', 'selectionTrigger', 'shadow', 'sortIcons', 'sortMode', 'sortStatus', 'stickyHeader', 'stickyHeaderOffset', 'storeColumnsKey', 'striped', 'stripedColor', 'style', 'styles', 'ta', 'tableClassName', 'tableProps', 'tableRef', 'td', 'textSelectionDisabled', 'top', 'totalRecords', 'tt', 'verticalAlign', 'verticalSpacing', 'visibleFrom', 'w', 'withColumnBorders', 'withRowBorders', 'withTableBorder']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DataTable, self).__init__(**args)

setattr(DataTable, "__init__", _explicitize_args(DataTable.__init__))

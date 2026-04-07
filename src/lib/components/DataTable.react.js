import React, { useDeferredValue, useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import {
    Anchor,
    Badge,
    Box,
    Code,
    DirectionProvider,
    Group,
    Popover,
    Paper,
    Progress,
    Stack,
    Text,
    TextInput,
} from '@mantine/core';
import {
    DataTable as MantineDataTable,
    DataTableDraggableRow,
    useDataTableColumns,
} from 'mantine-datatable';

const EMPTY_ARRAY = [];
const EMPTY_OBJECT = {};
const GROUP_RECORD_PREFIX = '__group__';
const GROUP_INDENT_SIZE = 20;
const TEMPLATE_TOKEN_PATTERN = /\{([^}]+)\}/g;
const ROOT_STYLE_PROP_NAMES = [
    'm',
    'mx',
    'my',
    'mt',
    'mb',
    'ms',
    'me',
    'ml',
    'mr',
    'p',
    'px',
    'py',
    'pt',
    'pb',
    'ps',
    'pe',
    'pl',
    'pr',
    'w',
    'miw',
    'maw',
    'h',
    'mih',
    'mah',
    'bg',
    'opacity',
    'ff',
    'fz',
    'fw',
    'lts',
    'ta',
    'lh',
    'fs',
    'tt',
    'display',
    'flex',
    'bd',
    'bdrs',
    'td',
    'bgsz',
    'bgp',
    'bgr',
    'bga',
    'pos',
    'top',
    'left',
    'bottom',
    'right',
    'inset',
    'hiddenFrom',
    'visibleFrom',
];

const isNil = (value) => value === null || value === undefined;

const pickDefinedProps = (source, keys) =>
    keys.reduce((accumulator, key) => {
        if (!isNil(source[key])) {
            accumulator[key] = source[key];
        }

        return accumulator;
    }, {});

const hasAnyDefinedProp = (source, keys) => keys.some((key) => !isNil(source[key]));

const reorderByIndices = (records, sourceIndex, destinationIndex) => {
    if (
        !Array.isArray(records) ||
        sourceIndex === destinationIndex ||
        sourceIndex < 0 ||
        destinationIndex < 0
    ) {
        return records;
    }

    const nextRecords = [...records];
    const [movedRecord] = nextRecords.splice(sourceIndex, 1);
    nextRecords.splice(destinationIndex, 0, movedRecord);
    return nextRecords;
};

const isInteractiveDragTarget = (target) =>
    Boolean(
        target?.closest?.(
            'a, button, input, textarea, select, option, [role="button"], [contenteditable="true"]'
        )
    );

const isDryComponent = (value) =>
    Boolean(
        value &&
            typeof value === 'object' &&
            !Array.isArray(value) &&
            value.type &&
            value.namespace &&
            value.props
    );

const getAccessorValue = (record, accessor) => {
    if (!record || !accessor) {
        return undefined;
    }

    if (typeof accessor !== 'string') {
        return record[accessor];
    }

    return accessor.split('.').reduce((accumulator, key) => {
        if (accumulator === null || accumulator === undefined) {
            return undefined;
        }

        return accumulator[key];
    }, record);
};

const setAccessorValue = (record, accessor, value) => {
    if (!record || typeof accessor !== 'string' || !accessor.trim()) {
        return record;
    }

    const keys = accessor.split('.');
    const nextRecord = Array.isArray(record) ? [...record] : { ...record };
    let currentTarget = nextRecord;
    let currentSource = record;

    keys.forEach((key, index) => {
        if (index === keys.length - 1) {
            currentTarget[key] = value;
            return;
        }

        const sourceValue =
            currentSource &&
            typeof currentSource === 'object' &&
            Object.prototype.hasOwnProperty.call(currentSource, key)
                ? currentSource[key]
                : undefined;
        const nextValue = Array.isArray(sourceValue)
            ? [...sourceValue]
            : sourceValue && typeof sourceValue === 'object'
              ? { ...sourceValue }
              : {};

        currentTarget[key] = nextValue;
        currentTarget = nextValue;
        currentSource = sourceValue;
    });

    return nextRecord;
};

const findRecordInCollection = (
    records,
    recordId,
    idAccessor,
    childRowsAccessor
) => {
    if (!Array.isArray(records)) {
        return undefined;
    }

    for (const record of records) {
        if (getRecordId(record, idAccessor) === recordId) {
            return record;
        }

        if (childRowsAccessor) {
            const children = getAccessorValue(record, childRowsAccessor);
            if (Array.isArray(children)) {
                const nestedMatch = findRecordInCollection(
                    children,
                    recordId,
                    idAccessor,
                    childRowsAccessor
                );

                if (nestedMatch) {
                    return nestedMatch;
                }
            }
        }
    }

    return undefined;
};

const updateRecordValueInCollection = (
    records,
    recordId,
    idAccessor,
    accessor,
    value,
    childRowsAccessor
) => {
    if (!Array.isArray(records)) {
        return { records, didUpdate: false };
    }

    let didUpdate = false;
    const nextRecords = records.map((record) => {
        let nextRecord = record;

        if (getRecordId(record, idAccessor) === recordId) {
            nextRecord = setAccessorValue(record, accessor, value);
            didUpdate = true;
        }

        if (childRowsAccessor) {
            const childRows = getAccessorValue(nextRecord, childRowsAccessor);

            if (Array.isArray(childRows)) {
                const updatedChildren = updateRecordValueInCollection(
                    childRows,
                    recordId,
                    idAccessor,
                    accessor,
                    value,
                    childRowsAccessor
                );

                if (updatedChildren.didUpdate) {
                    nextRecord = setAccessorValue(
                        nextRecord,
                        childRowsAccessor,
                        updatedChildren.records
                    );
                    didUpdate = true;
                }
            }
        }

        return nextRecord;
    });

    return {
        records: didUpdate ? nextRecords : records,
        didUpdate,
    };
};

const areEditableValuesEqual = (left, right) => {
    if (left === right) {
        return true;
    }

    if (left instanceof Date || right instanceof Date) {
        return String(left) === String(right);
    }

    if (Array.isArray(left) && Array.isArray(right)) {
        return (
            left.length === right.length &&
            left.every((item, index) =>
                areEditableValuesEqual(item, right[index])
            )
        );
    }

    if (
        left &&
        right &&
        typeof left === 'object' &&
        typeof right === 'object'
    ) {
        try {
            return JSON.stringify(left) === JSON.stringify(right);
        } catch {
            return false;
        }
    }

    return false;
};

const getEditorTypeName = (node) => {
    if (isDryComponent(node)) {
        return typeof node.type === 'string' ? node.type : undefined;
    }

    if (!React.isValidElement(node)) {
        return undefined;
    }

    if (typeof node.type === 'string') {
        return node.type;
    }

    return node.type?.displayName || node.type?.name;
};

const resolveEditorValueProp = (column, editorDefinition) => {
    if (typeof column?.editorValueProp === 'string') {
        return column.editorValueProp;
    }

    const editorTypeName = getEditorTypeName(editorDefinition);

    if (editorTypeName === 'Checkbox' || editorTypeName === 'Switch') {
        return 'checked';
    }

    return 'value';
};

const extractEditorValue = (nextValue, valueProp) => {
    if (
        nextValue &&
        typeof nextValue === 'object' &&
        !Array.isArray(nextValue)
    ) {
        if (Object.prototype.hasOwnProperty.call(nextValue, valueProp)) {
            return nextValue[valueProp];
        }

        if (
            nextValue.currentTarget &&
            Object.prototype.hasOwnProperty.call(
                nextValue.currentTarget,
                valueProp
            )
        ) {
            return nextValue.currentTarget[valueProp];
        }

        if (
            nextValue.target &&
            Object.prototype.hasOwnProperty.call(nextValue.target, valueProp)
        ) {
            return nextValue.target[valueProp];
        }
    }

    return nextValue;
};

const normalizeEditableValue = (value, column, editorDefinition) => {
    if (value instanceof Date) {
        const editorTypeName = getEditorTypeName(editorDefinition);

        if (
            column?.presentation === 'date' ||
            column?.type === 'date' ||
            editorTypeName === 'DateInput'
        ) {
            return value.toISOString().slice(0, 10);
        }

        return value.toISOString();
    }

    if (Array.isArray(value)) {
        return value.map((item) =>
            normalizeEditableValue(item, column, editorDefinition)
        );
    }

    return value;
};

const isTextLikeEditor = (editorDefinition) =>
    ['TextInput', 'Textarea', 'NumberInput', 'PasswordInput'].includes(
        getEditorTypeName(editorDefinition)
    );

const mergeEditorNestedProps = (value, overrides) =>
    value && typeof value === 'object' && !Array.isArray(value)
        ? { ...value, ...overrides }
        : overrides;

const enhanceEditorNode = (
    editorNode,
    column,
    editorDefinition,
    value,
    handleValueChange,
    closeEditor
) => {
    if (!React.isValidElement(editorNode)) {
        return editorNode;
    }

    const valueProp = resolveEditorValueProp(column, editorDefinition);
    const existingProps = editorNode.props || EMPTY_OBJECT;
    const originalOnChange = existingProps.onChange;
    const originalOnKeyDown = existingProps.onKeyDown;
    const nextProps = {
        ...existingProps,
        [valueProp]: value,
        autoFocus: false,
        comboboxProps: mergeEditorNestedProps(existingProps.comboboxProps, {
            withinPortal: true,
            zIndex: 1100,
        }),
        popoverProps: mergeEditorNestedProps(existingProps.popoverProps, {
            withinPortal: true,
            zIndex: 1100,
        }),
        onChange: (nextValue, ...args) => {
            handleValueChange(extractEditorValue(nextValue, valueProp));

            if (typeof originalOnChange === 'function') {
                originalOnChange(nextValue, ...args);
            }
        },
        onKeyDown: (event) => {
            if (event?.key === 'Escape') {
                if (event.preventDefault) {
                    event.preventDefault();
                }
                closeEditor();
            } else if (event?.key === 'Enter' && isTextLikeEditor(editorDefinition)) {
                closeEditor();
            }

            if (typeof originalOnKeyDown === 'function') {
                originalOnKeyDown(event);
            }
        },
    };

    return React.cloneElement(editorNode, nextProps);
};

const EditableCellPopover = ({
    content,
    editor,
    editorDefinition,
    isEditing,
    closeEditor,
    handleValueChange,
    value,
}) => {
    const dropdownRef = useRef(null);

    useEffect(() => {
        if (!isEditing || !dropdownRef.current) {
            return undefined;
        }

        const frameId = window.requestAnimationFrame(() => {
            const focusTarget = dropdownRef.current?.querySelector(
                'input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [role="textbox"], [type="radio"]:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );

            if (!focusTarget || typeof focusTarget.focus !== 'function') {
                return;
            }

            try {
                focusTarget.focus({ preventScroll: true });
            } catch {
                focusTarget.focus();
            }
        });

        return () => window.cancelAnimationFrame(frameId);
    }, [isEditing]);

    return (
        <Popover
            closeOnClickOutside
            offset={6}
            onDismiss={closeEditor}
            opened={isEditing}
            position="bottom-start"
            portalProps={{ reuseTargetNode: true }}
            shadow="md"
            width="target"
            withinPortal
            zIndex={1000}
        >
            <Popover.Target>
                <Box
                    component="span"
                    className={clsx(
                        'dash-mantine-datatable-editable-cell',
                        isEditing && 'dash-mantine-datatable-editable-cell-active'
                    )}
                >
                    {content}
                </Box>
            </Popover.Target>
            <Popover.Dropdown
                className="dash-mantine-datatable-editable-dropdown"
                onClick={(event) => event.stopPropagation()}
                onDoubleClick={(event) => event.stopPropagation()}
                onMouseDown={(event) => event.stopPropagation()}
                p="xs"
            >
                <Box ref={dropdownRef}>
                    {enhanceEditorNode(
                        editor,
                        editorDefinition?.column,
                        editorDefinition?.editor,
                        value,
                        handleValueChange,
                        closeEditor
                    )}
                </Box>
            </Popover.Dropdown>
        </Popover>
    );
};

const normalizeGroupBy = (value) => {
    if (typeof value === 'string') {
        const normalizedAccessor = value.trim();
        return normalizedAccessor ? [normalizedAccessor] : EMPTY_ARRAY;
    }

    if (!Array.isArray(value)) {
        return EMPTY_ARRAY;
    }

    return value
        .map((accessor) =>
            typeof accessor === 'string' ? accessor.trim() : ''
        )
        .filter(Boolean);
};

const serializeGroupValue = (value) => {
    if (value instanceof Date) {
        return value.toISOString();
    }

    if (isNil(value)) {
        return '';
    }

    if (typeof value === 'object') {
        try {
            return JSON.stringify(value);
        } catch {
            return String(value);
        }
    }

    return String(value);
};

const buildGroupRecordId = (path) =>
    [GROUP_RECORD_PREFIX]
        .concat(
            path.map(
                ({ accessor, value }) =>
                    `${accessor}=${serializeGroupValue(value)}`
            )
        )
        .join('|');

const hasAccessorPath = (record, accessor) => {
    if (!record || typeof accessor !== 'string' || !accessor.trim()) {
        return false;
    }

    return accessor.split('.').every((key) => {
        if (
            record === null ||
            record === undefined ||
            typeof record !== 'object' ||
            !Object.prototype.hasOwnProperty.call(record, key)
        ) {
            return false;
        }

        record = record[key];
        return true;
    });
};

const normalizeChildRowsAccessor = (value) => {
    if (typeof value !== 'string') {
        return undefined;
    }

    const normalizedAccessor = value.trim();
    return normalizedAccessor || undefined;
};

const compareAggregationValues = (left, right) => {
    const normalizeComparableValue = (value) => {
        if (value instanceof Date) {
            return value.getTime();
        }

        if (typeof value === 'number') {
            return value;
        }

        if (typeof value === 'string') {
            const numericValue = Number(value);
            if (Number.isFinite(numericValue) && value.trim() !== '') {
                return numericValue;
            }

            return value;
        }

        return String(value);
    };

    const normalizedLeft = normalizeComparableValue(left);
    const normalizedRight = normalizeComparableValue(right);

    if (normalizedLeft < normalizedRight) {
        return -1;
    }

    if (normalizedLeft > normalizedRight) {
        return 1;
    }

    return 0;
};

const compileCustomAggregator = (value) => {
    if (typeof value === 'function') {
        return value;
    }

    if (typeof value !== 'string') {
        return null;
    }

    const source = value.trim();

    if (!source) {
        return null;
    }

    try {
        if (source.startsWith('lambda ')) {
            const lambdaMatch =
                /^lambda\s*\(([^)]*)\)\s*:\s*([\s\S]+)$/.exec(source) ||
                /^lambda\s+([^:]+)\s*:\s*([\s\S]+)$/.exec(source);

            if (lambdaMatch) {
                return Function(
                    `return (${lambdaMatch[1].trim()}) => (${lambdaMatch[2].trim()});`
                )();
            }
        }

        if (source.includes('=>') || source.startsWith('function')) {
            return Function(`return (${source});`)();
        }

        return Function(
            'values',
            'records',
            'groupRecord',
            'outputAccessor',
            source
        );
    } catch {
        return null;
    }
};

const BUILT_IN_GROUP_AGGREGATORS = {
    count: (_values, records) => records.length,
    sum: (values) => {
        const numericValues = values
            .map((value) => Number(value))
            .filter((value) => Number.isFinite(value));

        if (!numericValues.length) {
            return undefined;
        }

        return numericValues.reduce((sum, value) => sum + value, 0);
    },
    mean: (values) => {
        const numericValues = values
            .map((value) => Number(value))
            .filter((value) => Number.isFinite(value));

        if (!numericValues.length) {
            return undefined;
        }

        return (
            numericValues.reduce((sum, value) => sum + value, 0) /
            numericValues.length
        );
    },
    median: (values) => {
        const numericValues = values
            .map((value) => Number(value))
            .filter((value) => Number.isFinite(value))
            .sort((left, right) => left - right);

        if (!numericValues.length) {
            return undefined;
        }

        const middleIndex = Math.floor(numericValues.length / 2);

        return numericValues.length % 2 === 0
            ? (numericValues[middleIndex - 1] + numericValues[middleIndex]) / 2
            : numericValues[middleIndex];
    },
    min: (values) => {
        const comparableValues = values.filter((value) => !isNil(value));

        if (!comparableValues.length) {
            return undefined;
        }

        return comparableValues.reduce((currentMin, value) =>
            compareAggregationValues(value, currentMin) < 0 ? value : currentMin
        );
    },
    max: (values) => {
        const comparableValues = values.filter((value) => !isNil(value));

        if (!comparableValues.length) {
            return undefined;
        }

        return comparableValues.reduce((currentMax, value) =>
            compareAggregationValues(value, currentMax) > 0 ? value : currentMax
        );
    },
};

const normalizeGroupAggregations = (value) => {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
        return EMPTY_ARRAY;
    }

    return Object.entries(value).flatMap(([outputAccessor, definition]) => {
        if (isNil(definition)) {
            return EMPTY_ARRAY;
        }

        if (typeof definition === 'string' || typeof definition === 'function') {
            return [
                {
                    outputAccessor,
                    sourceAccessor: outputAccessor,
                    aggregator: definition,
                },
            ];
        }

        if (typeof definition !== 'object' || Array.isArray(definition)) {
            return EMPTY_ARRAY;
        }

        return [
            {
                outputAccessor,
                sourceAccessor:
                    typeof definition.accessor === 'string' &&
                    definition.accessor.trim()
                        ? definition.accessor.trim()
                        : outputAccessor,
                aggregator:
                    definition.fn ??
                    definition.aggregator ??
                    definition.operation ??
                    definition.lambda ??
                    definition.function ??
                    definition.value,
            },
        ];
    });
};

const applyGroupAggregations = (record, leafRecords, aggregationDefinitions) => {
    if (!Array.isArray(aggregationDefinitions) || !aggregationDefinitions.length) {
        return record;
    }

    return aggregationDefinitions.reduce((nextRecord, definition) => {
        const { outputAccessor, sourceAccessor, aggregator } = definition;
        const values = sourceAccessor
            ? leafRecords.map((leafRecord) => getAccessorValue(leafRecord, sourceAccessor))
            : EMPTY_ARRAY;
        const normalizedAggregator =
            typeof aggregator === 'string' &&
            Object.prototype.hasOwnProperty.call(
                BUILT_IN_GROUP_AGGREGATORS,
                aggregator.trim().toLowerCase()
            )
                ? BUILT_IN_GROUP_AGGREGATORS[aggregator.trim().toLowerCase()]
                : compileCustomAggregator(aggregator);

        if (typeof normalizedAggregator !== 'function') {
            return nextRecord;
        }

        const aggregatedValue = normalizedAggregator(
            values,
            leafRecords,
            nextRecord,
            outputAccessor
        );

        if (isNil(aggregatedValue)) {
            return nextRecord;
        }

        return {
            ...nextRecord,
            [outputAccessor]: aggregatedValue,
        };
    }, record);
};

const isInlineHierarchyParentRecord = (record) =>
    Boolean(record?.__group || record?.__hierarchyParent);

const buildGroupedRecords = (
    records,
    accessors,
    aggregationDefinitions,
    path = EMPTY_ARRAY
) => {
    if (
        !Array.isArray(records) ||
        !records.length ||
        !Array.isArray(accessors) ||
        !accessors.length
    ) {
        return EMPTY_ARRAY;
    }

    const [accessor, ...remainingAccessors] = accessors;
    const groupedEntries = [];
    const groupedRecordsByKey = new Map();

    records.forEach((record) => {
        const groupValue = getAccessorValue(record, accessor);
        const groupKey = `${accessor}:${serializeGroupValue(groupValue)}`;

        if (!groupedRecordsByKey.has(groupKey)) {
            const groupPath = [...path, { accessor, value: groupValue }];
            const groupRecord = {
                __group: true,
                __groupAccessor: accessor,
                __groupId: buildGroupRecordId(groupPath),
                __groupLevel: path.length,
                __groupPath: groupPath,
                __groupValue: groupValue,
                __hierarchyParent: true,
                __groupedRecords: EMPTY_ARRAY,
                __remainingGroupBy: remainingAccessors,
            };

            if (!isNil(groupValue)) {
                groupRecord[accessor] = groupValue;
            }

            const nextEntry = {
                record: groupRecord,
                records: [],
            };

            groupedRecordsByKey.set(groupKey, nextEntry);
            groupedEntries.push(nextEntry);
        }

        groupedRecordsByKey.get(groupKey).records.push(record);
    });

    return groupedEntries.map((entry) => {
        const childPath = entry.record.__groupPath;
        const childRecords = remainingAccessors.length
            ? buildGroupedRecords(
                  entry.records,
                  remainingAccessors,
                  aggregationDefinitions,
                  childPath
              )
            : entry.records.map((record) => ({
                  ...record,
                  __group: false,
                  __groupLevel: childPath.length,
                  __leafRecords: [record],
              }));
        const leafRecords = remainingAccessors.length
            ? childRecords.flatMap((record) => record.__leafRecords || EMPTY_ARRAY)
            : entry.records;

        return applyGroupAggregations(
            {
                ...entry.record,
                __children: childRecords,
                __groupedRecords: leafRecords,
                __leafRecords: leafRecords,
            },
            leafRecords,
            aggregationDefinitions
        );
    });
};

const collectGroupedRecordIds = (records) => {
    if (!Array.isArray(records)) {
        return EMPTY_ARRAY;
    }

    return records.flatMap((record) =>
        record?.__group
            ? [
                  record.__groupId,
                  ...collectGroupedRecordIds(record.__children),
              ]
            : EMPTY_ARRAY
    );
};

const buildChildRowsRecords = (
    records,
    childRowsAccessor,
    aggregationDefinitions,
    level = 0
) => {
    if (!Array.isArray(records)) {
        return EMPTY_ARRAY;
    }

    return records.map((record) => {
        const hasChildrenAccessor = hasAccessorPath(record, childRowsAccessor);
        const rawChildren = hasChildrenAccessor
            ? getAccessorValue(record, childRowsAccessor)
            : undefined;
        const childRecords = Array.isArray(rawChildren)
            ? buildChildRowsRecords(
                  rawChildren,
                  childRowsAccessor,
                  aggregationDefinitions,
                  level + 1
              )
            : EMPTY_ARRAY;
        const leafRecords = hasChildrenAccessor
            ? childRecords.flatMap((childRecord) => childRecord.__leafRecords || EMPTY_ARRAY)
            : [record];
        const nextRecord = {
            ...record,
            __children: childRecords,
            __group: false,
            __groupLevel: level,
            __groupedRecords: leafRecords,
            __hierarchyParent: hasChildrenAccessor,
            __leafRecords: leafRecords,
        };

        return hasChildrenAccessor
            ? applyGroupAggregations(
                  nextRecord,
                  leafRecords,
                  aggregationDefinitions
              )
            : nextRecord;
    });
};

const flattenGroupedRecords = (records, expandedRecordIds, idAccessor) => {
    if (!Array.isArray(records)) {
        return EMPTY_ARRAY;
    }

    return records.flatMap((record) => {
        if (!isInlineHierarchyParentRecord(record)) {
            return [record];
        }

        const recordId = getRecordId(record, idAccessor);
        const isExpanded = expandedRecordIds.includes(recordId);

        return isExpanded
            ? [
                  record,
                  ...flattenGroupedRecords(
                      record.__children,
                      expandedRecordIds,
                      idAccessor
                  ),
              ]
            : [record];
    });
};

const collectHierarchyRecords = (records) => {
    if (!Array.isArray(records)) {
        return EMPTY_ARRAY;
    }

    return records.flatMap((record) => [
        record,
        ...collectHierarchyRecords(record?.__children),
    ]);
};

const mergeExpandedRecordIds = (...lists) =>
    Array.from(
        new Set(
            lists.flatMap((list) => (Array.isArray(list) ? list : EMPTY_ARRAY))
        )
    );

const wrapGroupedCellContent = (
    content,
    record,
    expandedRecordIds,
    groupLevel = 0
) => {
    const isGroupRecord = Boolean(record?.__group);
    const isExpanded = isGroupRecord
        ? expandedRecordIds.includes(record.__groupId)
        : false;

    return (
        <Box
            component="span"
            className="dash-mantine-datatable-group-cell"
            style={{
                paddingInlineStart: `${Math.max(groupLevel, 0) * GROUP_INDENT_SIZE}px`,
            }}
        >
            <span
                aria-hidden="true"
                className={clsx(
                    'dash-mantine-datatable-group-chevron',
                    isGroupRecord
                        ? 'dash-mantine-datatable-group-chevron-visible'
                        : 'dash-mantine-datatable-group-chevron-spacer',
                    isExpanded &&
                        'dash-mantine-datatable-group-chevron-expanded'
                )}
            />
            <Box component="span" className="dash-mantine-datatable-group-cell-content">
                {content}
            </Box>
        </Box>
    );
};

const interpolateTemplate = (template, record) => {
    if (!template || typeof template !== 'string') {
        return template;
    }

    return template.replace(/\{([^}]+)\}/g, (_, accessor) => {
        const value = getAccessorValue(record, accessor.trim());
        return isNil(value) ? '' : String(value);
    });
};

const getTemplateValue = (context, accessor) => {
    const normalizedAccessor = accessor.trim();

    if (!normalizedAccessor) {
        return undefined;
    }

    if (normalizedAccessor === 'record' || normalizedAccessor === 'row') {
        return context.record;
    }

    if (normalizedAccessor === 'value') {
        return context.value;
    }

    if (normalizedAccessor === 'index') {
        return context.index;
    }

    if (normalizedAccessor === 'accessor') {
        return context.accessor;
    }

    if (normalizedAccessor === 'column') {
        return context.column;
    }

    if (normalizedAccessor === 'locale') {
        return context.locale;
    }

    if (normalizedAccessor.startsWith('record.')) {
        return getAccessorValue(context.record, normalizedAccessor.slice(7));
    }

    if (normalizedAccessor.startsWith('row.')) {
        return getAccessorValue(context.record, normalizedAccessor.slice(4));
    }

    if (normalizedAccessor.startsWith('column.')) {
        return getAccessorValue(context.column, normalizedAccessor.slice(7));
    }

    const directContextValue = getAccessorValue(context, normalizedAccessor);

    if (!isNil(directContextValue)) {
        return directContextValue;
    }

    return getAccessorValue(context.record, normalizedAccessor);
};

const interpolateTemplateValue = (value, context) => {
    if (typeof value !== 'string') {
        return value;
    }

    const matches = Array.from(value.matchAll(TEMPLATE_TOKEN_PATTERN));

    if (!matches.length) {
        return value;
    }

    if (matches.length === 1 && matches[0][0] === value) {
        return getTemplateValue(context, matches[0][1]);
    }

    return value.replace(TEMPLATE_TOKEN_PATTERN, (_, accessor) => {
        const resolvedValue = getTemplateValue(context, accessor);
        return isNil(resolvedValue) ? '' : String(resolvedValue);
    });
};

const interpolateDryComponentNode = (node, context) => {
    if (Array.isArray(node)) {
        return node.map((item) => interpolateDryComponentNode(item, context));
    }

    if (isDryComponent(node)) {
        return {
            ...node,
            props: interpolateDryComponentNode(node.props, context),
        };
    }

    if (node && typeof node === 'object') {
        return Object.entries(node).reduce((accumulator, [key, value]) => {
            accumulator[key] = interpolateDryComponentNode(value, context);
            return accumulator;
        }, {});
    }

    return interpolateTemplateValue(node, context);
};

const resolveDashComponentType = (node) => {
    const namespace = node?.namespace;
    const type = node?.type;

    if (!namespace || !type || typeof window === 'undefined') {
        return null;
    }

    if (namespace === 'dash_html_components' || namespace === 'dash.html') {
        return String(type).toLowerCase();
    }

    return window?.[namespace]?.[type] || null;
};

const normalizeTemplateAction = (value) => {
    if (typeof value !== 'string') {
        return undefined;
    }

    const normalized = value
        .replace(/-row$/, '')
        .replace(/[-_]+/g, ' ')
        .trim();

    return normalized || value;
};

const buildTemplateClickPayload = (context, componentProps) => {
    const payload = buildEventPayload(
        {
            record: context.record,
            index: context.index,
            column: context.column,
        },
        context.idAccessor
    );
    const templateId = componentProps?.id;

    payload.trigger = 'templateClick';
    payload.templateId = templateId;

    if (
        templateId &&
        typeof templateId === 'object' &&
        !Array.isArray(templateId) &&
        typeof templateId.type === 'string'
    ) {
        payload.actionType = templateId.type;
        payload.action = normalizeTemplateAction(templateId.type);
    }

    return payload;
};

const withTemplateClickHandler = (componentProps, context, renderOptions) => {
    if (
        isNil(componentProps?.id) ||
        isNil(componentProps?.n_clicks) ||
        typeof renderOptions?.updateProps !== 'function'
    ) {
        return componentProps;
    }

    const originalOnClick = componentProps.onClick;

    return {
        ...componentProps,
        onClick: (event) => {
            if (event?.stopPropagation) {
                event.stopPropagation();
            }

            renderOptions.updateProps({
                cellClick: buildTemplateClickPayload(context, componentProps),
            });

            if (typeof originalOnClick === 'function') {
                originalOnClick(event);
            }
        },
    };
};

const materializeDashComponent = (
    node,
    context,
    renderOptions = EMPTY_OBJECT,
    nodePath = EMPTY_ARRAY
) => {
    const componentType = resolveDashComponentType(node);

    if (!componentType) {
        return interpolateDryComponentNode(node, context);
    }

    const interpolatedProps = interpolateDryComponentNode(node.props || EMPTY_OBJECT, context);
    const nextProps = Object.entries(interpolatedProps).reduce(
        (accumulator, [key, value]) => {
            if (key === 'children') {
                return accumulator;
            }

            accumulator[key] = renderTemplateNode(value, context, renderOptions, [
                ...nodePath,
                key,
            ]);
            return accumulator;
        },
        {}
    );
    const resolvedProps = withTemplateClickHandler(
        nextProps,
        context,
        renderOptions
    );
    const renderedChildren = Object.prototype.hasOwnProperty.call(
        interpolatedProps,
        'children'
    )
        ? renderTemplateNode(interpolatedProps.children, context, renderOptions, [
              ...nodePath,
              'children',
          ])
        : undefined;

    if (Array.isArray(renderedChildren)) {
        return React.createElement(componentType, resolvedProps, ...renderedChildren);
    }

    if (!isNil(renderedChildren)) {
        return React.createElement(componentType, resolvedProps, renderedChildren);
    }

    return React.createElement(componentType, resolvedProps);
};

const renderTemplateNode = (
    node,
    context,
    renderOptions = EMPTY_OBJECT,
    nodePath = EMPTY_ARRAY
) => {
    if (React.isValidElement(node)) {
        const nextProps = Object.keys(node.props || {}).reduce(
            (accumulator, key) => {
                accumulator[key] = renderTemplateNode(
                    node.props[key],
                    context,
                    renderOptions,
                    [...nodePath, key]
                );
                return accumulator;
            },
            {}
        );

        return React.cloneElement(
            node,
            withTemplateClickHandler(nextProps, context, renderOptions)
        );
    }

    if (isDryComponent(node)) {
        return materializeDashComponent(node, context, renderOptions, nodePath);
    }

    if (Array.isArray(node)) {
        return node.map((item, index) =>
            renderTemplateNode(item, context, renderOptions, [...nodePath, index])
        );
    }

    if (node && typeof node === 'object') {
        return Object.entries(node).reduce((accumulator, [key, value]) => {
            accumulator[key] = renderTemplateNode(value, context, renderOptions, [
                ...nodePath,
                key,
            ]);
            return accumulator;
        }, {});
    }

    return interpolateTemplateValue(node, context);
};

const buildTemplateContext = (record, index, column, locale, options = EMPTY_OBJECT) => ({
    accessor: column?.accessor,
    column,
    idAccessor: options.idAccessor,
    index,
    locale,
    record,
    recordId: getRecordId(record, options.idAccessor),
    row: record,
    value: getAccessorValue(record, column?.accessor),
});

const resolveTemplateNode = (
    template,
    context,
    options = EMPTY_OBJECT
) => {
    if (typeof template === 'function') {
        return template(context.record, context.index);
    }

    return renderTemplateNode(template, context, options);
};

const resolveTemplateRender = (
    template,
    record,
    index,
    column,
    locale,
    options = EMPTY_OBJECT
) =>
    resolveTemplateNode(
        template,
        buildTemplateContext(record, index, column, locale, options)
    );

const resolveStaticTemplateNode = (template, column, locale, options = EMPTY_OBJECT) =>
    resolveTemplateNode(
        template,
        buildTemplateContext(undefined, undefined, column, locale, options)
    );

const toDate = (value) => {
    if (value instanceof Date) {
        return value;
    }

    const nextDate = new Date(value);
    return Number.isNaN(nextDate.getTime()) ? null : nextDate;
};

const formatPrimitiveValue = (value, column, locale) => {
    if (isNil(value)) {
        return column.emptyValue || '';
    }

    const presentation = column.presentation || column.type || 'text';
    const effectiveLocale = column.locale || locale;
    const intlOptions = column.formatOptions || EMPTY_OBJECT;

    if (
        presentation === 'number' ||
        presentation === 'currency' ||
        presentation === 'percent'
    ) {
        const numericValue = Number(value);

        if (Number.isNaN(numericValue)) {
            return String(value);
        }

        const options = { ...intlOptions };

        if (presentation === 'currency') {
            options.style = 'currency';
            options.currency = column.currency || options.currency || 'USD';
        } else if (presentation === 'percent') {
            options.style = 'percent';
        }

        if (!isNil(column.minimumFractionDigits)) {
            options.minimumFractionDigits = column.minimumFractionDigits;
        }

        if (!isNil(column.maximumFractionDigits)) {
            options.maximumFractionDigits = column.maximumFractionDigits;
        }

        return new Intl.NumberFormat(effectiveLocale, options).format(
            numericValue
        );
    }

    if (
        presentation === 'date' ||
        presentation === 'datetime' ||
        presentation === 'time'
    ) {
        const dateValue = toDate(value);

        if (!dateValue) {
            return String(value);
        }

        const options = { ...intlOptions };

        if (presentation === 'date') {
            options.dateStyle = options.dateStyle || 'medium';
        } else if (presentation === 'datetime') {
            options.dateStyle = options.dateStyle || 'medium';
            options.timeStyle = options.timeStyle || 'short';
        } else if (presentation === 'time') {
            options.timeStyle = options.timeStyle || 'short';
        }

        return new Intl.DateTimeFormat(effectiveLocale, options).format(
            dateValue
        );
    }

    if (presentation === 'boolean') {
        const trueLabel = column.trueLabel || 'Yes';
        const falseLabel = column.falseLabel || 'No';
        return value ? trueLabel : falseLabel;
    }

    if (typeof value === 'object') {
        return JSON.stringify(value);
    }

    return String(value);
};

const buildDisplayValue = (record, column, locale) => {
    if (column.template) {
        return interpolateTemplate(column.template, record);
    }

    const accessorValue = getAccessorValue(record, column.accessor);

    if (typeof column.valueAccessor === 'string') {
        return getAccessorValue(record, column.valueAccessor);
    }

    return formatPrimitiveValue(accessorValue, column, locale);
};

const renderFieldValue = (field, record, locale) => {
    const derivedField = {
        accessor: field.accessor,
        template: field.template,
        presentation: field.presentation,
        type: field.type,
        locale: field.locale,
        currency: field.currency,
        formatOptions: field.formatOptions,
        trueLabel: field.trueLabel,
        falseLabel: field.falseLabel,
        emptyValue: field.emptyValue,
        minimumFractionDigits: field.minimumFractionDigits,
        maximumFractionDigits: field.maximumFractionDigits,
    };

    const value = buildDisplayValue(record, derivedField, locale);

    if (field.type === 'code') {
        return <Code>{value}</Code>;
    }

    return (
        <Text c={field.color || 'dimmed'} fw={field.fw} size={field.size || 'sm'}>
            {value}
        </Text>
    );
};

const renderExpansionContent = (
    config,
    record,
    locale,
    options = EMPTY_OBJECT
) => {
    if (!config) {
        return null;
    }

    if (
        React.isValidElement(config) ||
        Array.isArray(config) ||
        isDryComponent(config)
    ) {
        return resolveTemplateNode(
            config,
            buildTemplateContext(
                record,
                undefined,
                { accessor: '__rowExpansion__' },
                locale,
                options
            ),
            options
        );
    }

    if (typeof config !== 'object') {
        return resolveTemplateNode(
            config,
            buildTemplateContext(
                record,
                undefined,
                { accessor: '__rowExpansion__' },
                locale,
                options
            ),
            options
        );
    }

    if (config.type === 'json') {
        const jsonValue = config.accessor
            ? getAccessorValue(record, config.accessor)
            : record;

        return (
            <Code block style={{ whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(jsonValue, null, 2)}
            </Code>
        );
    }

    if (config.type === 'text') {
        const textValue = config.template
            ? interpolateTemplate(config.template, record)
            : buildDisplayValue(record, config, locale);

        return <Text size="sm">{textValue}</Text>;
    }

    const fields = Array.isArray(config.fields) ? config.fields : EMPTY_ARRAY;

    return (
        <Paper p="sm" radius="sm" withBorder>
            <Stack gap="xs">
                {config.title ? (
                    <Text fw={700}>{interpolateTemplate(config.title, record)}</Text>
                ) : null}
                {fields.map((field) => (
                    <Group
                        align="flex-start"
                        gap="xs"
                        grow
                        key={field.accessor || field.label}
                        wrap="nowrap"
                    >
                        <Text c="dimmed" fw={600} size="sm" style={{ minWidth: 110 }}>
                            {field.label || field.accessor}
                        </Text>
                        <Box style={{ flex: 1 }}>
                            {renderFieldValue(field, record, locale)}
                        </Box>
                    </Group>
                ))}
            </Stack>
        </Paper>
    );
};

const toComparableValue = (value) => {
    if (typeof value === 'string') {
        return value.toLowerCase();
    }

    if (value instanceof Date) {
        return value.getTime();
    }

    return value;
};

const sortRecords = (records, sortStatus) => {
    if (!sortStatus || !sortStatus.columnAccessor) {
        return records;
    }

    const direction = sortStatus.direction === 'desc' ? -1 : 1;
    const accessor = sortStatus.sortKey || sortStatus.columnAccessor;
    const sorted = [...records];

    sorted.sort((left, right) => {
        const leftValue = toComparableValue(getAccessorValue(left, accessor));
        const rightValue = toComparableValue(getAccessorValue(right, accessor));

        if (isNil(leftValue) && isNil(rightValue)) {
            return 0;
        }

        if (isNil(leftValue)) {
            return 1;
        }

        if (isNil(rightValue)) {
            return -1;
        }

        if (leftValue > rightValue) {
            return direction;
        }

        if (leftValue < rightValue) {
            return -direction;
        }

        return 0;
    });

    return sorted;
};

const toSearchableText = (value) => {
    if (isNil(value)) {
        return '';
    }

    if (Array.isArray(value)) {
        return value.map(toSearchableText).join(' ');
    }

    if (typeof value === 'object') {
        return JSON.stringify(value);
    }

    return String(value);
};

const filterRecords = (records, query, accessors) => {
    if (!query) {
        return records;
    }

    const normalizedQuery = String(query).trim().toLowerCase();

    if (!normalizedQuery) {
        return records;
    }

    return records.filter((record) =>
        accessors.some((accessor) =>
            toSearchableText(getAccessorValue(record, accessor))
                .toLowerCase()
                .includes(normalizedQuery)
        )
    );
};

const isCompositeIdAccessor = (value) =>
    value && typeof value === 'object' && !Array.isArray(value);

const joinRecordIdParts = (values, separator = ':') =>
    values.map((value) => (isNil(value) ? '' : String(value))).join(separator);

const getRecordId = (record, idAccessor) => {
    if (!record) {
        return undefined;
    }

    if (Object.prototype.hasOwnProperty.call(record, '__groupId')) {
        return record.__groupId;
    }

    if (typeof idAccessor === 'function') {
        return idAccessor(record);
    }

    if (Array.isArray(idAccessor)) {
        return joinRecordIdParts(
            idAccessor.map((accessor) => getAccessorValue(record, accessor))
        );
    }

    if (isCompositeIdAccessor(idAccessor)) {
        if (typeof idAccessor.template === 'string') {
            return interpolateTemplate(idAccessor.template, record);
        }

        if (Array.isArray(idAccessor.accessors)) {
            return joinRecordIdParts(
                idAccessor.accessors.map((accessor) =>
                    getAccessorValue(record, accessor)
                ),
                idAccessor.separator
            );
        }

        if (typeof idAccessor.accessor === 'string') {
            return getAccessorValue(record, idAccessor.accessor);
        }
    }

    return getAccessorValue(record, idAccessor || 'id');
};

const isRowRule = (value) =>
    value &&
    typeof value === 'object' &&
    !Array.isArray(value) &&
    (Object.prototype.hasOwnProperty.call(value, 'selector') ||
        Object.prototype.hasOwnProperty.call(value, 'when'));

const matchesSelectorCondition = (actualValue, condition) => {
    if (!condition || typeof condition !== 'object' || Array.isArray(condition)) {
        return actualValue === condition;
    }

    if (
        isNil(actualValue) &&
        ['gt', 'gte', 'lt', 'lte', 'contains', 'startsWith', 'endsWith'].some(
            (key) => Object.prototype.hasOwnProperty.call(condition, key)
        )
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'eq') &&
        actualValue !== condition.eq
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'ne') &&
        actualValue === condition.ne
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'gt') &&
        !(actualValue > condition.gt)
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'gte') &&
        !(actualValue >= condition.gte)
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'lt') &&
        !(actualValue < condition.lt)
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'lte') &&
        !(actualValue <= condition.lte)
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'in') &&
        (!Array.isArray(condition.in) || !condition.in.includes(actualValue))
    ) {
        return false;
    }

    if (
        Object.prototype.hasOwnProperty.call(condition, 'notIn') &&
        Array.isArray(condition.notIn) &&
        condition.notIn.includes(actualValue)
    ) {
        return false;
    }

    if (Object.prototype.hasOwnProperty.call(condition, 'contains')) {
        const haystack = toSearchableText(actualValue);
        if (!haystack.includes(String(condition.contains))) {
            return false;
        }
    }

    if (Object.prototype.hasOwnProperty.call(condition, 'startsWith')) {
        const haystack = toSearchableText(actualValue);
        if (!haystack.startsWith(String(condition.startsWith))) {
            return false;
        }
    }

    if (Object.prototype.hasOwnProperty.call(condition, 'endsWith')) {
        const haystack = toSearchableText(actualValue);
        if (!haystack.endsWith(String(condition.endsWith))) {
            return false;
        }
    }

    return true;
};

const matchesRowSelector = (record, index, selector, idAccessor) => {
    if (isNil(selector)) {
        return true;
    }

    if (typeof selector === 'function') {
        return Boolean(selector(record, index));
    }

    if (Array.isArray(selector)) {
        return selector.some((childSelector) =>
            matchesRowSelector(record, index, childSelector, idAccessor)
        );
    }

    if (typeof selector === 'string' || typeof selector === 'number') {
        return getRecordId(record, idAccessor) === selector;
    }

    if (typeof selector === 'object') {
        return Object.entries(selector).every(([accessor, expectedValue]) => {
            let actualValue;

            if (accessor === 'index') {
                actualValue = index;
            } else if (accessor === 'id' || accessor === 'recordId') {
                actualValue = getRecordId(record, idAccessor);
            } else {
                actualValue = getAccessorValue(record, accessor);
            }

            if (Array.isArray(expectedValue)) {
                return expectedValue.includes(actualValue);
            }

            return matchesSelectorCondition(actualValue, expectedValue);
        });
    }

    return false;
};

const getRowRuleValue = (rule, fallbackKey) => {
    if (Object.prototype.hasOwnProperty.call(rule, 'value')) {
        return rule.value;
    }

    if (
        fallbackKey &&
        Object.prototype.hasOwnProperty.call(rule, fallbackKey)
    ) {
        return rule[fallbackKey];
    }

    return undefined;
};

const resolveRowRuleEntryValue = (
    entry,
    fallbackKey,
    record,
    index,
    idAccessor
) => {
    if (!isRowRule(entry)) {
        return entry;
    }

    const selector = Object.prototype.hasOwnProperty.call(entry, 'selector')
        ? entry.selector
        : entry.when;

    if (!matchesRowSelector(record, index, selector, idAccessor)) {
        return undefined;
    }

    return getRowRuleValue(entry, fallbackKey);
};

const buildRowValueResolver = (
    value,
    fallbackKey,
    idAccessor,
    { merge = false } = {}
) => {
    if (typeof value === 'function') {
        return value;
    }

    if (isNil(value)) {
        return undefined;
    }

    return (record, index) => {
        const entries = Array.isArray(value) ? value : [value];

        if (merge) {
            const mergedValue = entries.reduce((accumulator, entry) => {
                const resolvedValue = resolveRowRuleEntryValue(
                    entry,
                    fallbackKey,
                    record,
                    index,
                    idAccessor
                );

                if (
                    resolvedValue &&
                    typeof resolvedValue === 'object' &&
                    !Array.isArray(resolvedValue)
                ) {
                    return { ...accumulator, ...resolvedValue };
                }

                return accumulator;
            }, {});

            return Object.keys(mergedValue).length ? mergedValue : undefined;
        }

        let resolvedValue;
        entries.forEach((entry) => {
            const nextValue = resolveRowRuleEntryValue(
                entry,
                fallbackKey,
                record,
                index,
                idAccessor
            );

            if (!isNil(nextValue)) {
                resolvedValue = nextValue;
            }
        });

        return resolvedValue;
    };
};

const buildRowClassNameResolver = (value, idAccessor) => {
    if (typeof value === 'function' || typeof value === 'string') {
        return value;
    }

    if (isNil(value)) {
        return undefined;
    }

    return (record, index) => {
        const entries = Array.isArray(value) ? value : [value];
        const classNames = entries
            .map((entry) =>
                resolveRowRuleEntryValue(
                    entry,
                    'className',
                    record,
                    index,
                    idAccessor
                )
            )
            .filter(Boolean);

        return classNames.length ? clsx(classNames) : undefined;
    };
};

const buildRowStyleResolver = (value, idAccessor) => {
    if (typeof value === 'function') {
        return value;
    }

    if (isNil(value)) {
        return undefined;
    }

    return (record, index) => {
        const entries = Array.isArray(value) ? value : [value];
        const mergedStyle = entries.reduce((accumulator, entry) => {
            const nextStyle = resolveRowRuleEntryValue(
                entry,
                'style',
                record,
                index,
                idAccessor
            );

            if (
                nextStyle &&
                typeof nextStyle === 'object' &&
                !Array.isArray(nextStyle)
            ) {
                return { ...accumulator, ...nextStyle };
            }

            return accumulator;
        }, {});

        return Object.keys(mergedStyle).length ? mergedStyle : undefined;
    };
};

const buildRowBooleanResolver = (
    value,
    fallbackKey,
    idAccessor,
    defaultValue
) => {
    if (typeof value === 'function') {
        return (record, index) => {
            const resolvedValue = value(record, index);
            return isNil(resolvedValue) ? defaultValue : Boolean(resolvedValue);
        };
    }

    if (isNil(value)) {
        return undefined;
    }

    return (record, index) => {
        const entries = Array.isArray(value) ? value : [value];
        let resolvedValue = defaultValue;

        entries.forEach((entry) => {
            const nextValue = resolveRowRuleEntryValue(
                entry,
                fallbackKey,
                record,
                index,
                idAccessor
            );

            if (!isNil(nextValue)) {
                resolvedValue = Boolean(nextValue);
            }
        });

        return resolvedValue;
    };
};

const resolveMantineIdAccessor = (idAccessor) => {
    if (typeof idAccessor === 'function' || typeof idAccessor === 'string') {
        return idAccessor;
    }

    if (isNil(idAccessor)) {
        return 'id';
    }

    return (record) => getRecordId(record, idAccessor);
};

const buildEventPayload = (params, idAccessor) => {
    const recordId = getRecordId(params.record, idAccessor);
    const payload = {
        record: params.record,
        recordId,
        index: params.index,
        timestamp: Date.now(),
    };

    if (params.column) {
        payload.column = params.column;
        payload.columnAccessor = params.column.accessor;
        payload.columnIndex = params.columnIndex;
        payload.value = getAccessorValue(params.record, params.column.accessor);
    }

    return payload;
};

const flattenGroupColumns = (groupDefinitions) => {
    if (!Array.isArray(groupDefinitions)) {
        return EMPTY_ARRAY;
    }

    return groupDefinitions.flatMap((group) => [
        ...(Array.isArray(group?.columns) ? group.columns : EMPTY_ARRAY),
        ...flattenGroupColumns(group?.groups),
    ]);
};

const syncGroupsWithEffectiveColumns = (groupDefinitions, effectiveColumns) => {
    if (!Array.isArray(groupDefinitions)) {
        return undefined;
    }

    return groupDefinitions.map((group) => {
        const groupAccessors = new Set(
            Array.isArray(group?.columns)
                ? group.columns.map((column) => column?.accessor).filter(Boolean)
                : EMPTY_ARRAY
        );

        return {
            ...group,
            columns: (effectiveColumns || EMPTY_ARRAY).filter((column) =>
                groupAccessors.has(column?.accessor)
            ),
            groups: Array.isArray(group?.groups)
                ? syncGroupsWithEffectiveColumns(group.groups, effectiveColumns)
                : group?.groups,
        };
    });
};

const buildColumn = (
    column,
    locale,
    defaultColumnRender,
    renderOptions,
    editingOptions = EMPTY_OBJECT
) => ({
    accessor: column.accessor,
    title: column.title,
    textAlign: column.textAlign,
    sortable: column.sortable,
    sortKey: column.sortKey,
    draggable: column.draggable,
    toggleable: column.toggleable,
    resizable: column.resizable,
    defaultToggle: column.defaultToggle,
    filter:
        typeof column.filter === 'function'
            ? column.filter
            : isNil(column.filter)
              ? column.filter
              : resolveStaticTemplateNode(
                    column.filter,
                    column,
                    locale,
                    renderOptions
                ),
    filtering: column.filtering,
    filterPopoverProps: column.filterPopoverProps,
    filterPopoverDisableClickOutside:
        column.filterPopoverDisableClickOutside,
    width: column.width,
    hidden: column.hidden,
    hiddenContent: column.hiddenContent,
    visibleMediaQuery: column.visibleMediaQuery,
    titleClassName: column.titleClassName,
    titleStyle: column.titleStyle,
    cellsClassName: clsx(column.cellsClassName),
    cellsStyle:
        typeof column.cellsStyle === 'function'
            ? column.cellsStyle
            : column.cellsStyle
              ? () => column.cellsStyle
              : undefined,
    customCellAttributes: buildRowValueResolver(
        !isNil(column.cellAttributes)
            ? column.cellAttributes
            : column.customCellAttributes,
        'attributes',
        renderOptions.idAccessor,
        { merge: true }
    ),
    footer: isNil(column.footer)
        ? column.footer
        : resolveStaticTemplateNode(
              column.footer,
              column,
              locale,
              renderOptions
          ),
    footerClassName: column.footerClassName,
    footerStyle: column.footerStyle,
    ellipsis: column.ellipsis,
    noWrap: column.noWrap,
    render: (record, index) => {
        const rawValue = getAccessorValue(record, column.accessor);
        const formattedValue = buildDisplayValue(record, column, locale);
        const presentation = column.presentation || column.type || 'text';
        const customRender = column.render;
        let content;

        if (!isNil(customRender)) {
            content = resolveTemplateRender(
                customRender,
                record,
                index,
                column,
                locale,
                renderOptions
            );
        } else if (presentation === 'badge') {
            const badgeColor = column.badgeColorAccessor
                ? getAccessorValue(record, column.badgeColorAccessor)
                : column.badgeColor || 'gray';

            content = (
                <Badge
                    color={badgeColor}
                    radius={column.badgeRadius || 'sm'}
                    variant={column.badgeVariant || 'light'}
                >
                    {formattedValue}
                </Badge>
            );
        } else if (presentation === 'link') {
            const href = column.hrefAccessor
                ? getAccessorValue(record, column.hrefAccessor)
                : interpolateTemplate(column.hrefTemplate, record);

            content = (
                <Anchor href={href} target={column.target || '_blank'}>
                    {formattedValue}
                </Anchor>
            );
        } else if (presentation === 'code') {
            content = <Code>{formattedValue}</Code>;
        } else if (presentation === 'progress') {
            const progressValue = Number(rawValue || 0);
            content = (
                <Progress
                    color={column.progressColor || 'blue'}
                    radius={column.progressRadius || 'xl'}
                    value={Number.isNaN(progressValue) ? 0 : progressValue}
                />
            );
        } else if (presentation === 'json') {
            content = (
                <Code style={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(rawValue, null, 2)}
                </Code>
            );
        } else if (!isNil(defaultColumnRender)) {
            content = resolveTemplateRender(
                defaultColumnRender,
                record,
                index,
                column,
                locale,
                renderOptions
            );
        } else if (!hasAnyDefinedProp(column, ['color', 'fw', 'size'])) {
            content = formattedValue;
        } else {
            content = (
                <Text
                    c={column.color}
                    component="span"
                    fw={column.fw}
                    size={column.size}
                >
                    {formattedValue}
                </Text>
            );
        }

        if (
            !column.editable ||
            !column.accessor ||
            record?.__group ||
            typeof editingOptions?.isEditingCell !== 'function' ||
            typeof editingOptions?.handleValueChange !== 'function' ||
            typeof editingOptions?.closeEditor !== 'function'
        ) {
            return content;
        }

        const editorDefinition = column.editor || <TextInput size="xs" />;
        const editorNode = resolveTemplateRender(
            editorDefinition,
            record,
            index,
            column,
            locale,
            renderOptions
        );

        return (
            <EditableCellPopover
                closeEditor={editingOptions.closeEditor}
                content={content}
                editor={editorNode}
                editorDefinition={{
                    column,
                    editor: editorDefinition,
                }}
                handleValueChange={(nextValue) =>
                    editingOptions.handleValueChange(
                        record,
                        column,
                        normalizeEditableValue(nextValue, column, editorDefinition)
                    )
                }
                isEditing={editingOptions.isEditingCell(record, column)}
                value={rawValue}
            />
        );
    },
});

const buildGroup = (
    group,
    locale,
    defaultColumnRender,
    renderOptions,
    editingOptions = EMPTY_OBJECT
) => ({
    id: group.id,
    title: group.title,
    textAlign: group.textAlign,
    className: group.className,
    style: group.style,
    columns: Array.isArray(group.columns)
        ? group.columns.map((column) =>
              buildColumn(
                  column,
                  locale,
                  defaultColumnRender,
                  renderOptions,
                  editingOptions
              )
          )
        : undefined,
    groups: Array.isArray(group.groups)
        ? group.groups.map((childGroup) =>
              buildGroup(
                  childGroup,
                  locale,
                  defaultColumnRender,
                  renderOptions,
                  editingOptions
              )
          )
        : undefined,
});

const DataTable = (props) => {
    const {
        __groupLevel = 0,
        id,
        data,
        records,
        columns,
        groups,
        groupBy,
        childRowsAccessor,
        groupAggregations,
        idAccessor,
        locale,
        paginationMode,
        sortMode,
        searchMode,
        searchQuery,
        searchableAccessors,
        page,
        recordsPerPage,
        pageSize,
        totalRecords,
        sortStatus,
        sortIcons,
        selectedRecordIds,
        expandedRecordIds,
        selectionTrigger,
        selectionColumnClassName,
        selectionColumnStyle,
        selectionCheckboxProps,
        allRecordsSelectionCheckboxProps,
        selectableRowRules,
        disabledSelectionRowRules,
        selectionCheckboxRules,
        rowDragging,
        rowColor,
        rowBackgroundColor,
        rowClassName,
        rowStyle,
        rowAttributes,
        rowExpansion,
        setProps,
        emptyState,
        noRecordsIcon,
        noRecordsText,
        pageSizeOptions,
        recordsPerPageOptions,
        recordsPerPageLabel,
        paginationSize,
        paginationActiveTextColor,
        paginationActiveBackgroundColor,
        loadingText,
        customLoader,
        tableProps,
        scrollAreaProps,
        className,
        tableClassName,
    } = props;

    const allRecords = Array.isArray(records)
        ? records
        : Array.isArray(data)
          ? data
          : EMPTY_ARRAY;
    const normalizedGroupBy = normalizeGroupBy(groupBy);
    const normalizedChildRowsAccessor = normalizeChildRowsAccessor(childRowsAccessor);
    const normalizedGroupAggregations = normalizeGroupAggregations(groupAggregations);
    const hasRowGrouping = normalizedGroupBy.length > 0;
    const hasChildRowsHierarchy =
        !hasRowGrouping && Boolean(normalizedChildRowsAccessor);
    const hasInlineHierarchy = hasRowGrouping || hasChildRowsHierarchy;
    const isGroupedChildTable = __groupLevel > 0;
    const groupedRecordsForAllRows = hasRowGrouping
        ? buildGroupedRecords(
              allRecords,
              normalizedGroupBy,
              normalizedGroupAggregations
          )
        : undefined;
    const initialGroupedExpandedIds = hasRowGrouping
        ? collectGroupedRecordIds(groupedRecordsForAllRows)
        : EMPTY_ARRAY;
    const initialRowExpansionIds = Array.isArray(
        rowExpansion?.initiallyExpandedRecordIds
    )
        ? rowExpansion.initiallyExpandedRecordIds
        : EMPTY_ARRAY;
    const initialPageSize = recordsPerPage || pageSize || 10;

    const [internalPage, setInternalPage] = useState(page || 1);
    const [internalRecordsPerPage, setInternalRecordsPerPage] =
        useState(initialPageSize);
    const [internalSortStatus, setInternalSortStatus] = useState(
        sortStatus || null
    );
    const [internalSelectedIds, setInternalSelectedIds] = useState(
        Array.isArray(selectedRecordIds) ? selectedRecordIds : EMPTY_ARRAY
    );
    const [internalExpandedIds, setInternalExpandedIds] = useState(
        Array.isArray(expandedRecordIds)
            ? expandedRecordIds
            : mergeExpandedRecordIds(
                  initialGroupedExpandedIds,
                  initialRowExpansionIds
              )
    );
    const [activeEditableCell, setActiveEditableCell] = useState(null);

    const deferredSearchQuery = useDeferredValue(searchQuery);

    useEffect(() => {
        if (!isNil(page)) {
            setInternalPage(page);
        }
    }, [page]);

    useEffect(() => {
        if (!isNil(recordsPerPage) || !isNil(pageSize)) {
            setInternalRecordsPerPage(recordsPerPage || pageSize);
        }
    }, [recordsPerPage, pageSize]);

    useEffect(() => {
        if (sortStatus) {
            setInternalSortStatus(sortStatus);
        }
    }, [sortStatus]);

    useEffect(() => {
        if (Array.isArray(selectedRecordIds)) {
            setInternalSelectedIds(selectedRecordIds);
        }
    }, [selectedRecordIds]);

    useEffect(() => {
        if (Array.isArray(expandedRecordIds)) {
            setInternalExpandedIds(expandedRecordIds);
        }
    }, [expandedRecordIds]);

    const currentPage = isNil(page) ? internalPage : page;
    const currentRecordsPerPage = !isNil(recordsPerPage)
        ? recordsPerPage
        : !isNil(pageSize)
          ? pageSize
          : internalRecordsPerPage;
    const currentSortStatus = sortStatus || internalSortStatus;
    const currentSelectedIds = Array.isArray(selectedRecordIds)
        ? selectedRecordIds
        : internalSelectedIds;
    const currentExpandedIds = Array.isArray(expandedRecordIds)
        ? expandedRecordIds
        : internalExpandedIds;
    const rowDragSourceIdRef = useRef(null);
    const [draggedRowId, setDraggedRowId] = useState(null);
    const [dragOverRowId, setDragOverRowId] = useState(null);

    const groupedColumns = flattenGroupColumns(groups);
    const hasTopLevelColumns = Array.isArray(columns) && columns.length > 0;
    const hasGroups = Array.isArray(groups) && groups.length > 0;
    const sourceColumns = hasTopLevelColumns ? columns : groupedColumns;
    const { effectiveColumns } = useDataTableColumns({
        key: props.storeColumnsKey,
        columns: sourceColumns,
    });
    const resolvedColumns = Array.isArray(effectiveColumns)
        ? effectiveColumns
        : sourceColumns;
    const resolvedSearchableAccessors = Array.isArray(searchableAccessors)
        ? searchableAccessors
        : resolvedColumns
              .filter((column) => column.searchable !== false)
              .map((column) => column.accessor)
              .filter(Boolean);

    const clientFilteredRecords =
        searchMode === 'client'
            ? filterRecords(allRecords, deferredSearchQuery, resolvedSearchableAccessors)
            : allRecords;
    const clientSortedRecords =
        sortMode === 'client'
            ? sortRecords(clientFilteredRecords, currentSortStatus)
            : clientFilteredRecords;

    const computedTotalRecords =
        paginationMode === 'client'
            ? clientSortedRecords.length
            : totalRecords;

    const paginatedRecords =
        paginationMode === 'client'
            ? clientSortedRecords.slice(
                  Math.max(currentPage - 1, 0) * currentRecordsPerPage,
                  Math.max(currentPage - 1, 0) * currentRecordsPerPage +
                      currentRecordsPerPage
              )
            : clientSortedRecords;
    const groupedRecords = hasRowGrouping
        ? buildGroupedRecords(
              paginatedRecords,
              normalizedGroupBy,
              normalizedGroupAggregations
          )
        : undefined;
    const childRowsRecords = hasChildRowsHierarchy
        ? buildChildRowsRecords(
              paginatedRecords,
              normalizedChildRowsAccessor,
              normalizedGroupAggregations
          )
        : undefined;
    const displayedRecords = hasRowGrouping
        ? flattenGroupedRecords(groupedRecords, currentExpandedIds, idAccessor)
        : hasChildRowsHierarchy
          ? flattenGroupedRecords(
                childRowsRecords,
                currentExpandedIds,
                idAccessor
            )
          : paginatedRecords;

    const selectableRecords = hasChildRowsHierarchy
        ? collectHierarchyRecords(childRowsRecords)
        : allRecords;
    const selectedRecordsPayload = selectableRecords.filter((record) =>
        currentSelectedIds.includes(getRecordId(record, idAccessor))
    );
    const selectableRowResolver = buildRowBooleanResolver(
        selectableRowRules,
        'selectable',
        idAccessor,
        true
    );
    const disabledSelectionRowResolver = buildRowBooleanResolver(
        disabledSelectionRowRules,
        'disabled',
        idAccessor,
        false
    );
    const selectionCheckboxPropsResolver = buildRowValueResolver(
        selectionCheckboxRules,
        'checkboxProps',
        idAccessor,
        { merge: true }
    );
    const templateRenderOptions = {
        idAccessor,
    };
    const rowDraggingEnabled = Boolean(rowDragging) && !hasInlineHierarchy;

    const updateProps = (nextProps) => {
        if (setProps) {
            setProps(nextProps);
        }
    };

    const clearRowDraggingState = () => {
        rowDragSourceIdRef.current = null;
        setDraggedRowId(null);
        setDragOverRowId(null);
    };

    const closeEditableCell = () => {
        setActiveEditableCell(null);
    };

    const isEditingCell = (record, column) =>
        Boolean(
            activeEditableCell &&
                activeEditableCell.recordId === getRecordId(record, idAccessor) &&
                activeEditableCell.columnAccessor === column?.accessor
        );

    const handleEditableCellValueChange = (record, column, nextValue) => {
        const recordId = getRecordId(record, idAccessor);

        if (isNil(recordId) || !column?.accessor) {
            return;
        }

        const currentRecord = findRecordInCollection(
            allRecords,
            recordId,
            idAccessor,
            normalizedChildRowsAccessor
        );

        if (!currentRecord) {
            return;
        }

        const currentValue = getAccessorValue(currentRecord, column.accessor);

        if (areEditableValuesEqual(currentValue, nextValue)) {
            return;
        }

        const updatedRecords = updateRecordValueInCollection(
            allRecords,
            recordId,
            idAccessor,
            column.accessor,
            nextValue,
            normalizedChildRowsAccessor
        );

        if (!updatedRecords.didUpdate) {
            return;
        }

        updateProps({
            data: updatedRecords.records,
            records: updatedRecords.records,
        });
    };

    const handleCellDoubleClick = (params) => {
        const payload = buildEventPayload(params, idAccessor);
        const matchingColumn = resolvedColumns.find(
            (column) => column?.accessor === payload.columnAccessor
        );

        if (
            matchingColumn?.editable &&
            !params.record?.__group &&
            !isNil(payload.recordId)
        ) {
            setActiveEditableCell({
                columnAccessor: payload.columnAccessor,
                recordId: payload.recordId,
            });
        } else {
            closeEditableCell();
        }

        updateProps({
            cellDoubleClick: payload,
        });
    };

    const handlePageChange = (nextPage) => {
        if (isNil(page)) {
            setInternalPage(nextPage);
        }

        updateProps({
            page: nextPage,
            pagination: {
                page: nextPage,
                recordsPerPage: currentRecordsPerPage,
                totalRecords: computedTotalRecords,
                timestamp: Date.now(),
            },
        });
    };

    const handleRecordsPerPageChange = (nextRecordsPerPage) => {
        if (isNil(recordsPerPage) && isNil(pageSize)) {
            setInternalRecordsPerPage(nextRecordsPerPage);
        }

        if (isNil(page)) {
            setInternalPage(1);
        }

        updateProps({
            recordsPerPage: nextRecordsPerPage,
            pageSize: nextRecordsPerPage,
            page: 1,
            pagination: {
                page: 1,
                recordsPerPage: nextRecordsPerPage,
                totalRecords: computedTotalRecords,
                timestamp: Date.now(),
            },
        });
    };

    const handleSortStatusChange = (nextSortStatus) => {
        if (!sortStatus) {
            setInternalSortStatus(nextSortStatus);
        }

        updateProps({
            sortStatus: nextSortStatus,
            lastSortChange: {
                ...nextSortStatus,
                timestamp: Date.now(),
            },
        });
    };

    const handleSelectedRecordsChange = (nextSelectedRecords) => {
        const nextSelectedIds = nextSelectedRecords.map((record) =>
            getRecordId(record, idAccessor)
        );

        if (!Array.isArray(selectedRecordIds)) {
            setInternalSelectedIds(nextSelectedIds);
        }

        updateProps({
            selectedRecordIds: nextSelectedIds,
            selectedRecords: nextSelectedRecords,
            lastSelectionChange: {
                recordIds: nextSelectedIds,
                records: nextSelectedRecords,
                timestamp: Date.now(),
            },
        });
    };

    const buildExpandedRecordProps = (nextExpandedRecordIds) => ({
        expandedRecordIds: nextExpandedRecordIds,
        lastExpansionChange: {
            recordIds: nextExpandedRecordIds,
            timestamp: Date.now(),
        },
    });

    const syncExpandedRecordIds = (nextExpandedRecordIds) => {
        if (!Array.isArray(expandedRecordIds)) {
            setInternalExpandedIds(nextExpandedRecordIds);
        }

        return buildExpandedRecordProps(nextExpandedRecordIds);
    };

    const handleExpandedRecordIdsChange = (nextExpandedRecordIds) => {
        updateProps(syncExpandedRecordIds(nextExpandedRecordIds));
    };

    const toggleInlineHierarchyRecord = (record) => {
        const recordId = getRecordId(record, idAccessor);

        if (isNil(recordId)) {
            return EMPTY_OBJECT;
        }

        const nextExpandedRecordIds = currentExpandedIds.includes(recordId)
            ? currentExpandedIds.filter((expandedId) => expandedId !== recordId)
            : mergeExpandedRecordIds(currentExpandedIds, [recordId]);

        return syncExpandedRecordIds(nextExpandedRecordIds);
    };

    const handleRowDragStart = (event, record) => {
        if (!rowDraggingEnabled || isInteractiveDragTarget(event.target)) {
            event.preventDefault();
            return;
        }

        const recordId = getRecordId(record, idAccessor);
        rowDragSourceIdRef.current = recordId;
        setDraggedRowId(recordId);
        setDragOverRowId(recordId);

        if (event.dataTransfer) {
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.dropEffect = 'move';

            try {
                event.dataTransfer.setData('text/plain', String(recordId));
            } catch {
                // Some browsers restrict custom drag payloads for table rows.
            }
        }
    };

    const handleRowDragOver = (event, record) => {
        if (!rowDraggingEnabled || !rowDragSourceIdRef.current) {
            return;
        }

        event.preventDefault();

        if (event.dataTransfer) {
            event.dataTransfer.dropEffect = 'move';
        }

        const recordId = getRecordId(record, idAccessor);
        if (recordId !== dragOverRowId) {
            setDragOverRowId(recordId);
        }
    };

    const handleRowDrop = (event, record) => {
        if (!rowDraggingEnabled || !rowDragSourceIdRef.current) {
            return;
        }

        event.preventDefault();

        const sourceRecordId = rowDragSourceIdRef.current;
        const destinationRecordId = getRecordId(record, idAccessor);
        const sourceIndex = allRecords.findIndex(
            (row) => getRecordId(row, idAccessor) === sourceRecordId
        );
        const destinationIndex = allRecords.findIndex(
            (row) => getRecordId(row, idAccessor) === destinationRecordId
        );

        if (
            sourceIndex === -1 ||
            destinationIndex === -1 ||
            sourceIndex === destinationIndex
        ) {
            clearRowDraggingState();
            return;
        }

        const reorderedRecords = reorderByIndices(
            allRecords,
            sourceIndex,
            destinationIndex
        );

        updateProps({
            data: reorderedRecords,
            records: reorderedRecords,
            lastRowDragChange: {
                sourceIndex,
                destinationIndex,
                record: allRecords[sourceIndex],
                recordId: sourceRecordId,
                records: reorderedRecords,
                recordIds: reorderedRecords.map((row) =>
                    getRecordId(row, idAccessor)
                ),
                timestamp: Date.now(),
            },
        });

        clearRowDraggingState();
    };

    const builtRowFactory = rowDraggingEnabled
        ? ({ record, index, rowProps, children, expandedElement }) => {
              const recordId = getRecordId(record, idAccessor);

              return (
                  <React.Fragment key={recordId}>
                      <DataTableDraggableRow
                          {...rowProps}
                          draggable
                          className={clsx(
                              rowProps.className,
                              'dash-mantine-datatable-row-draggable',
                              draggedRowId === recordId &&
                                  'dash-mantine-datatable-row-dragging',
                              dragOverRowId === recordId &&
                                  draggedRowId !== recordId &&
                                  'dash-mantine-datatable-row-drag-over'
                          )}
                          isDragging={draggedRowId === recordId}
                          onDragEnd={clearRowDraggingState}
                          onDragOver={(event) =>
                              handleRowDragOver(event, record, index)
                          }
                          onDragStart={(event) =>
                              handleRowDragStart(event, record, index)
                          }
                          onDrop={(event) => handleRowDrop(event, record, index)}
                      >
                          {children}
                      </DataTableDraggableRow>
                      {expandedElement}
                  </React.Fragment>
              );
          }
        : undefined;

    useEffect(() => {
        if (!rowDraggingEnabled) {
            clearRowDraggingState();
        }
    }, [rowDraggingEnabled]);

    useEffect(() => {
        if (!activeEditableCell) {
            return;
        }

        const hasActiveColumn = resolvedColumns.some(
            (column) => column?.accessor === activeEditableCell.columnAccessor
        );
        const hasActiveRecord = displayedRecords.some(
            (record) =>
                !record?.__group &&
                getRecordId(record, idAccessor) === activeEditableCell.recordId
        );

        if (!hasActiveColumn || !hasActiveRecord) {
            closeEditableCell();
        }
    }, [activeEditableCell, displayedRecords, idAccessor, resolvedColumns]);

    const resolvedDefaultColumnProps = props.defaultColumnProps
        ? { ...props.defaultColumnProps }
        : undefined;
    const resolvedDefaultColumnRender = !isNil(props.defaultColumnRender)
        ? props.defaultColumnRender
        : resolvedDefaultColumnProps && !isNil(resolvedDefaultColumnProps.render)
          ? resolvedDefaultColumnProps.render
          : undefined;

    if (
        resolvedDefaultColumnProps &&
        Object.prototype.hasOwnProperty.call(resolvedDefaultColumnProps, 'render')
    ) {
        delete resolvedDefaultColumnProps.render;
    }

    if (
        resolvedDefaultColumnProps &&
        !isNil(resolvedDefaultColumnProps.filter) &&
        typeof resolvedDefaultColumnProps.filter !== 'function'
    ) {
        resolvedDefaultColumnProps.filter = resolveStaticTemplateNode(
            resolvedDefaultColumnProps.filter,
            { accessor: '__default_filter__' },
            locale,
            templateRenderOptions
        );
    }

    if (
        resolvedDefaultColumnProps &&
        !isNil(resolvedDefaultColumnProps.footer)
    ) {
        resolvedDefaultColumnProps.footer = resolveStaticTemplateNode(
            resolvedDefaultColumnProps.footer,
            { accessor: '__default_footer__' },
            locale,
            templateRenderOptions
        );
    }

    if (resolvedDefaultColumnProps) {
        const defaultCellAttributes = !isNil(resolvedDefaultColumnProps.cellAttributes)
            ? resolvedDefaultColumnProps.cellAttributes
            : resolvedDefaultColumnProps.customCellAttributes;

        if (!isNil(defaultCellAttributes)) {
            resolvedDefaultColumnProps.customCellAttributes =
                buildRowValueResolver(
                    defaultCellAttributes,
                    'attributes',
                    idAccessor,
                    { merge: true }
                );
        }

        if (
            Object.prototype.hasOwnProperty.call(
                resolvedDefaultColumnProps,
                'cellAttributes'
            )
        ) {
            delete resolvedDefaultColumnProps.cellAttributes;
        }
    }

    const builtColumns = resolvedColumns.map((column) =>
        buildColumn(
            column,
            locale,
            resolvedDefaultColumnRender,
            templateRenderOptions,
            {
                closeEditor: closeEditableCell,
                handleValueChange: handleEditableCellValueChange,
                isEditingCell,
            }
        )
    );
    const builtGroupedColumns =
        hasInlineHierarchy || isGroupedChildTable
            ? builtColumns.map((column, columnIndex) => {
                  if (columnIndex !== 0) {
                      return column;
                  }

                  const originalRender = column.render;

                  return {
                      ...column,
                      render: (record, index) => {
                          const renderedContent = originalRender(record, index);
                          const resolvedContent =
                              record?.__group &&
                              (isNil(renderedContent) || renderedContent === '')
                                  ? String(record.__groupValue ?? '')
                                  : renderedContent;

                          return wrapGroupedCellContent(
                              resolvedContent,
                              record,
                              currentExpandedIds,
                              record?.__groupLevel ?? __groupLevel
                          );
                      },
                  };
              })
            : builtColumns;
    const resolvedGroups = hasGroups
        ? syncGroupsWithEffectiveColumns(groups, resolvedColumns)
        : undefined;
    const builtGroups = hasGroups
        ? resolvedGroups.map((group) =>
              buildGroup(
                  group,
                  locale,
                  resolvedDefaultColumnRender,
                  templateRenderOptions,
                  {
                      closeEditor: closeEditableCell,
                      handleValueChange: handleEditableCellValueChange,
                      isEditingCell,
                  }
              )
          )
        : undefined;

    const builtRowExpansion = rowExpansion
        ? {
              trigger: rowExpansion.trigger || 'click',
              allowMultiple: rowExpansion.allowMultiple,
              expandable: ({ record, index }) =>
                  !isInlineHierarchyParentRecord(record) &&
                  (typeof rowExpansion.expandable === 'function'
                      ? rowExpansion.expandable({ record, index })
                      : true),
              initiallyExpanded: ({ record }) =>
                  !isInlineHierarchyParentRecord(record) &&
                  Array.isArray(rowExpansion.initiallyExpandedRecordIds) &&
                  rowExpansion.initiallyExpandedRecordIds.includes(
                      getRecordId(record, idAccessor)
                  ),
              expanded: {
                  recordIds: currentExpandedIds,
                  onRecordIdsChange: handleExpandedRecordIdsChange,
              },
              content: ({ record }) =>
                  isInlineHierarchyParentRecord(record)
                      ? null
                      : renderExpansionContent(
                            rowExpansion.content || rowExpansion,
                            record,
                            locale,
                            templateRenderOptions
                        ),
          }
        : undefined;

    const resolvedSortIcons = sortIcons
        ? {
              sorted: isNil(sortIcons.sorted)
                  ? sortIcons.sorted
                  : resolveStaticTemplateNode(
                        sortIcons.sorted,
                        { accessor: '__sort_icon_sorted__' },
                        locale,
                        templateRenderOptions
                    ),
              unsorted: isNil(sortIcons.unsorted)
                  ? sortIcons.unsorted
                  : resolveStaticTemplateNode(
                        sortIcons.unsorted,
                        { accessor: '__sort_icon_unsorted__' },
                        locale,
                        templateRenderOptions
                    ),
          }
        : undefined;

    const emptyStateNode =
        typeof emptyState === 'string' ? (
            <Text c="dimmed" ta="center">
                {emptyState}
            </Text>
        ) : emptyState && emptyState.type === 'text' && !emptyState.namespace ? (
            <Text c="dimmed" ta="center">
                {emptyState.value}
            </Text>
        ) : undefined;
    const resolvedEmptyStateNode =
        emptyStateNode ||
        ((React.isValidElement(emptyState) ||
            Array.isArray(emptyState) ||
            isDryComponent(emptyState)) &&
        !isNil(emptyState)
            ? resolveStaticTemplateNode(
                  emptyState,
                  { accessor: '__empty_state__' },
                  locale,
                  templateRenderOptions
              )
            : undefined);
    const resolvedNoRecordsIcon =
        isNil(emptyState) && !isNil(noRecordsIcon)
            ? resolveStaticTemplateNode(
                  noRecordsIcon,
                  { accessor: '__no_records_icon__' },
                  locale,
                  templateRenderOptions
              )
            : undefined;
    const resolvedCustomLoader = !isNil(customLoader)
        ? resolveStaticTemplateNode(
              customLoader,
              { accessor: '__custom_loader__' },
              locale,
              templateRenderOptions
          )
        : undefined;

    const rootStyleProps = pickDefinedProps(props, ROOT_STYLE_PROP_NAMES);
    const resolvedRootProps = {
        ...rootStyleProps,
        bg: isNil(props.bg) ? props.backgroundColor : props.bg,
        h: isNil(props.h) ? props.height : props.h,
        mih: isNil(props.mih) ? props.minHeight : props.mih,
        mah: isNil(props.mah) ? props.maxHeight : props.mah,
        radius: isNil(props.borderRadius) ? props.radius : props.borderRadius,
    };
    const resolvedTableProps =
        hasInlineHierarchy || isGroupedChildTable
            ? {
                  ...tableProps,
                  layout: tableProps?.layout || 'fixed',
              }
            : tableProps;
    const resolvedRowColor = buildRowValueResolver(
        rowColor,
        'color',
        idAccessor
    );
    const resolvedRowBackgroundColor = buildRowValueResolver(
        rowBackgroundColor,
        'backgroundColor',
        idAccessor
    );
    const resolvedRowClassName = buildRowClassNameResolver(
        rowClassName,
        idAccessor
    );
    const resolvedRowStyle = buildRowStyleResolver(rowStyle, idAccessor);
    const resolvedRowAttributes = buildRowValueResolver(
        rowAttributes,
        'attributes',
        idAccessor,
        { merge: true }
    );
    const resolvedMantineIdAccessor = hasInlineHierarchy
        ? (record) => getRecordId(record, idAccessor)
        : resolveMantineIdAccessor(idAccessor);
    const resolvedSelectionTrigger = hasRowGrouping
        ? undefined
        : selectionTrigger;
    const isRecordSelectable = resolvedSelectionTrigger
        ? (record, index) => {
              if (record?.__group) {
                  return false;
              }

              if (
                  disabledSelectionRowResolver &&
                  disabledSelectionRowResolver(record, index)
              ) {
                  return false;
              }

              if (selectableRowResolver) {
                  return selectableRowResolver(record, index);
              }

              return true;
          }
        : undefined;
    const getRecordSelectionCheckboxProps =
        selectionCheckboxPropsResolver && resolvedSelectionTrigger
            ? (record, index) =>
                  selectionCheckboxPropsResolver(record, index) || EMPTY_OBJECT
            : undefined;
    const layoutDirection = props.direction === 'rtl' ? 'rtl' : 'ltr';

    return (
        <DirectionProvider
            detectDirection={false}
            initialDirection={layoutDirection}
            key={`${id || 'datatable'}-${layoutDirection}`}
        >
            <Box dir={layoutDirection}>
                <MantineDataTable
                    {...resolvedRootProps}
                    {...resolvedTableProps}
                    id={id}
                    backgroundColor={resolvedRootProps.bg}
                    bodyRef={props.bodyRef}
                    borderColor={props.borderColor}
                    borderRadius={resolvedRootProps.radius}
                    c={props.c}
                    className={clsx(
                        className,
                        tableClassName,
                        rowDraggingEnabled &&
                            'dash-mantine-datatable-row-drag-enabled',
                        (hasInlineHierarchy || isGroupedChildTable) &&
                            'dash-mantine-datatable-grouped',
                        isGroupedChildTable &&
                            'dash-mantine-datatable-grouped-child',
                        props.striped && 'dash-mantine-datatable-striped',
                        props.highlightOnHover &&
                            'dash-mantine-datatable-highlight-on-hover'
                    )}
                    classNames={props.classNames}
                    columns={hasGroups ? undefined : builtGroupedColumns}
                    customLoader={resolvedCustomLoader}
                    customRowAttributes={resolvedRowAttributes}
                    defaultColumnProps={resolvedDefaultColumnProps}
                    emptyState={resolvedEmptyStateNode}
                    fetching={props.fetching}
                    groups={builtGroups}
                    height={resolvedRootProps.h}
                    highlightOnHover={props.highlightOnHover}
                    highlightOnHoverColor={props.highlightOnHoverColor}
                    idAccessor={resolvedMantineIdAccessor}
                    isRecordSelectable={isRecordSelectable}
                    getRecordSelectionCheckboxProps={
                        getRecordSelectionCheckboxProps
                    }
                    loadingText={loadingText}
                    loaderBackgroundBlur={props.loaderBackgroundBlur}
                    loaderColor={props.loaderColor}
                    loaderSize={props.loaderSize}
                    loaderType={props.loaderType}
                    maxHeight={resolvedRootProps.mah}
                    minHeight={resolvedRootProps.mih}
                    noHeader={props.noHeader}
                    noRecordsIcon={resolvedNoRecordsIcon}
                    noRecordsText={noRecordsText}
                    onCellClick={(params) =>
                        updateProps({
                            cellClick: buildEventPayload(params, idAccessor),
                        })
                    }
                    onCellContextMenu={(params) =>
                        updateProps({
                            cellContextMenu: buildEventPayload(
                                params,
                                idAccessor
                            ),
                        })
                    }
                    onCellDoubleClick={handleCellDoubleClick}
                    onPageChange={handlePageChange}
                    onRecordsPerPageChange={handleRecordsPerPageChange}
                    onRowClick={(params) =>
                        updateProps({
                            ...(isInlineHierarchyParentRecord(params.record)
                                ? toggleInlineHierarchyRecord(params.record)
                                : EMPTY_OBJECT),
                            rowClick: buildEventPayload(params, idAccessor),
                        })
                    }
                    onRowContextMenu={(params) =>
                        updateProps({
                            rowContextMenu: buildEventPayload(
                                params,
                                idAccessor
                            ),
                        })
                    }
                    onRowDoubleClick={(params) =>
                        updateProps({
                            rowDoubleClick: buildEventPayload(
                                params,
                                idAccessor
                            ),
                        })
                    }
                    onScroll={(position) =>
                        updateProps({
                            scrollPosition: {
                                ...position,
                                timestamp: Date.now(),
                            },
                        })
                    }
                    onScrollToBottom={() =>
                        updateProps({
                            scrollEdge: { edge: 'bottom', timestamp: Date.now() },
                        })
                    }
                    onScrollToLeft={() =>
                        updateProps({
                            scrollEdge: { edge: 'left', timestamp: Date.now() },
                        })
                    }
                    onScrollToRight={() =>
                        updateProps({
                            scrollEdge: { edge: 'right', timestamp: Date.now() },
                        })
                    }
                    onScrollToTop={() =>
                        updateProps({
                            scrollEdge: { edge: 'top', timestamp: Date.now() },
                        })
                    }
                    onSelectedRecordsChange={handleSelectedRecordsChange}
                    onSortStatusChange={handleSortStatusChange}
                    page={paginationMode === 'none' ? undefined : currentPage}
                    paginationActiveBackgroundColor={
                        paginationActiveBackgroundColor
                    }
                    paginationActiveTextColor={paginationActiveTextColor}
                    paginationSize={paginationSize}
                    paginationWithControls={props.paginationWithControls}
                    paginationWithEdges={props.paginationWithEdges}
                    pinFirstColumn={props.pinFirstColumn}
                    pinLastColumn={props.pinLastColumn}
                    horizontalSpacing={props.horizontalSpacing}
                    records={displayedRecords}
                    recordsPerPage={
                        paginationMode === 'none'
                            ? undefined
                            : currentRecordsPerPage
                    }
                    recordsPerPageLabel={recordsPerPageLabel}
                    recordsPerPageOptions={
                        recordsPerPageOptions || pageSizeOptions || EMPTY_ARRAY
                    }
                    rowBorderColor={props.rowBorderColor}
                    rowColor={resolvedRowColor}
                    rowBackgroundColor={resolvedRowBackgroundColor}
                    rowClassName={resolvedRowClassName}
                    rowFactory={builtRowFactory}
                    rowExpansion={builtRowExpansion}
                    rowStyle={resolvedRowStyle}
                    scrollAreaProps={scrollAreaProps}
                    selectedRecords={
                        resolvedSelectionTrigger || currentSelectedIds.length
                            ? selectedRecordsPayload
                            : undefined
                    }
                    allRecordsSelectionCheckboxProps={
                        allRecordsSelectionCheckboxProps
                    }
                    selectionCheckboxProps={selectionCheckboxProps}
                    selectionColumnClassName={selectionColumnClassName}
                    selectionColumnStyle={selectionColumnStyle}
                    selectionTrigger={resolvedSelectionTrigger}
                    shadow={props.shadow}
                    sortIcons={resolvedSortIcons}
                    sortStatus={currentSortStatus}
                    storeColumnsKey={props.storeColumnsKey}
                    stickyHeader={props.stickyHeader}
                    stickyHeaderOffset={props.stickyHeaderOffset}
                    striped={props.striped}
                    stripedColor={props.stripedColor}
                    style={props.style}
                    styles={props.styles}
                    tableRef={props.tableRef}
                    textSelectionDisabled={props.textSelectionDisabled}
                    totalRecords={
                        paginationMode === 'none'
                            ? undefined
                            : computedTotalRecords
                    }
                    verticalSpacing={props.verticalSpacing}
                    verticalAlign={props.verticalAlign}
                    withRowBorders={props.withRowBorders}
                    withColumnBorders={props.withColumnBorders}
                    withTableBorder={props.withTableBorder}
                />
            </Box>
        </DirectionProvider>
    );
};

DataTable.defaultProps = {
    data: EMPTY_ARRAY,
    columns: EMPTY_ARRAY,
    groups: undefined,
    groupBy: undefined,
    childRowsAccessor: undefined,
    groupAggregations: undefined,
    idAccessor: 'id',
    locale: 'en-US',
    paginationMode: 'client',
    sortMode: 'client',
    searchMode: 'client',
    recordsPerPage: 10,
    pageSize: 10,
    noRecordsText: 'No records found',
    pageSizeOptions: [10, 25, 50],
    recordsPerPageOptions: undefined,
    recordsPerPageLabel: 'Rows per page',
    paginationSize: 'sm',
    direction: 'ltr',
    selectionTrigger: undefined,
    tableProps: EMPTY_OBJECT,
    scrollAreaProps: EMPTY_OBJECT,
    withRowBorders: true,
    withTableBorder: true,
    withColumnBorders: false,
    striped: false,
    highlightOnHover: true,
    textSelectionDisabled: false,
};

DataTable.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),

    /**
     * Table records. `data` is the preferred Dash-facing alias.
     */
    data: PropTypes.arrayOf(PropTypes.object),

    /**
     * Optional alias for `data`, matching the original Mantine DataTable API.
     */
    records: PropTypes.arrayOf(PropTypes.object),

    /**
     * Column definitions. Each column may also define a Dash-friendly
     * `presentation` such as `text`, `number`, `currency`, `date`,
     * `datetime`, `badge`, `link`, `code`, `json` or `progress`.
     * Set `editable=True` to enable double-click editing, and pass a Dash
     * input component to `editor` when you want a custom in-place editor.
     */
    columns: PropTypes.arrayOf(PropTypes.object),

    /**
     * Optional column groups matching Mantine DataTable grouped headers.
     */
    groups: PropTypes.arrayOf(PropTypes.object),

    /**
     * Row grouping accessor or accessors. Grouped rows render inline nested
     * parents inside a single table, while leaf rows can still use
     * `rowExpansion` for detail panels.
     */
    groupBy: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * Nested child-record accessor for already hierarchical data. When set,
     * rows with this accessor render inline child rows using the same
     * indentation and expand/collapse affordance as `groupBy`.
     */
    childRowsAccessor: PropTypes.string,

    /**
     * Per-column aggregation mapping for parent rows. Values may be one of the
     * built-in aggregations (`sum`, `mean`, `median`, `min`, `max`, `count`) or
     * a custom client-side function / function source string.
     */
    groupAggregations: PropTypes.object,

    /**
     * Record identifier accessor. Defaults to `id`.
     */
    idAccessor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
        PropTypes.arrayOf(PropTypes.string),
    ]),

    /**
     * Locale used for number and date formatting.
     */
    locale: PropTypes.string,
    /**
     * Layout direction. Set to `rtl` to render the table in a right-to-left
     * Mantine direction context.
     */
    direction: PropTypes.oneOf(['ltr', 'rtl']),

    paginationMode: PropTypes.oneOf(['client', 'server', 'none']),
    sortMode: PropTypes.oneOf(['client', 'server']),
    searchMode: PropTypes.oneOf(['client', 'server']),
    searchQuery: PropTypes.string,
    searchableAccessors: PropTypes.arrayOf(PropTypes.string),
    page: PropTypes.number,
    recordsPerPage: PropTypes.number,
    pageSize: PropTypes.number,
    totalRecords: PropTypes.number,
    sortStatus: PropTypes.object,
    selectedRecordIds: PropTypes.array,
    selectedRecords: PropTypes.array,
    expandedRecordIds: PropTypes.array,
    selectionTrigger: PropTypes.oneOf(['cell', 'checkbox']),
    selectionColumnClassName: PropTypes.string,
    selectionColumnStyle: PropTypes.object,
    selectionCheckboxProps: PropTypes.object,
    allRecordsSelectionCheckboxProps: PropTypes.object,
    selectableRowRules: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.object,
        PropTypes.array,
    ]),
    disabledSelectionRowRules: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.object,
        PropTypes.array,
    ]),
    selectionCheckboxRules: PropTypes.oneOfType([
        PropTypes.object,
        PropTypes.array,
    ]),

    /**
     * Enables Dash-native row reordering. Pass `true` or a configuration object.
     * The reordered list is written back to both `data` and `records`, and the
     * latest drag payload is exposed through `lastRowDragChange`.
     */
    rowDragging: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),

    /**
     * Row text color. Accepts a static Mantine color or Dash-safe rule objects.
     */
    rowColor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
        PropTypes.array,
    ]),

    /**
     * Row background color. Accepts a static color or Dash-safe rule objects.
     */
    rowBackgroundColor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
        PropTypes.array,
    ]),

    /**
     * Row class names. Accepts a static className or Dash-safe rule objects.
     */
    rowClassName: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
        PropTypes.array,
    ]),
    rowAttributes: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),

    /**
     * Row inline styles. Accepts a static style object or Dash-safe rule objects.
     */
    rowStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
    rowExpansion: PropTypes.object,
    rowClick: PropTypes.object,
    rowDoubleClick: PropTypes.object,
    rowContextMenu: PropTypes.object,
    cellClick: PropTypes.object,
    cellDoubleClick: PropTypes.object,
    cellContextMenu: PropTypes.object,
    pagination: PropTypes.object,
    scrollPosition: PropTypes.object,
    scrollEdge: PropTypes.object,
    lastRowDragChange: PropTypes.object,
    lastSortChange: PropTypes.object,
    lastSelectionChange: PropTypes.object,
    lastExpansionChange: PropTypes.object,
    emptyState: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    noRecordsIcon: PropTypes.any,
    noRecordsText: PropTypes.string,
    recordsPerPageOptions: PropTypes.arrayOf(PropTypes.number),
    pageSizeOptions: PropTypes.arrayOf(PropTypes.number),
    recordsPerPageLabel: PropTypes.string,
    paginationSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    paginationActiveTextColor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
    ]),
    paginationActiveBackgroundColor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
    ]),
    loadingText: PropTypes.string,
    tableProps: PropTypes.object,
    scrollAreaProps: PropTypes.object,
    className: PropTypes.string,
    tableClassName: PropTypes.string,
    classNames: PropTypes.object,
    style: PropTypes.object,
    styles: PropTypes.object,
    radius: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    minHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    maxHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    shadow: PropTypes.string,
    bg: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    c: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    backgroundColor: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    borderColor: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    rowBorderColor: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    stripedColor: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    highlightOnHoverColor: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
    ]),
    withRowBorders: PropTypes.bool,
    withTableBorder: PropTypes.bool,
    withColumnBorders: PropTypes.bool,
    horizontalSpacing: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
    ]),
    verticalSpacing: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    borderRadius: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    striped: PropTypes.bool,
    highlightOnHover: PropTypes.bool,
    textSelectionDisabled: PropTypes.bool,
    fetching: PropTypes.bool,
    loaderBackgroundBlur: PropTypes.number,
    loaderSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    loaderType: PropTypes.string,
    loaderColor: PropTypes.string,
    customLoader: PropTypes.any,
    noHeader: PropTypes.bool,
    pinFirstColumn: PropTypes.bool,
    pinLastColumn: PropTypes.bool,
    stickyHeader: PropTypes.bool,
    stickyHeaderOffset: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    verticalAlign: PropTypes.oneOf(['top', 'center', 'bottom']),
    paginationWithEdges: PropTypes.bool,
    paginationWithControls: PropTypes.bool,
    /**
     * Local-storage key used by Mantine DataTable to persist
     * draggable / toggleable / resizable column state.
     */
    storeColumnsKey: PropTypes.string,
    defaultColumnProps: PropTypes.object,
    defaultColumnRender: PropTypes.any,
    sortIcons: PropTypes.object,
    bodyRef: PropTypes.any,
    tableRef: PropTypes.any,
    m: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mx: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    my: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mt: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mb: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ms: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    me: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ml: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mr: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    p: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    px: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    py: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    pt: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    pb: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ps: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    pe: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    pl: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    pr: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    w: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    miw: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    maw: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    h: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mih: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    mah: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    opacity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ff: PropTypes.string,
    fz: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    fw: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    lts: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ta: PropTypes.string,
    lh: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    fs: PropTypes.string,
    tt: PropTypes.string,
    display: PropTypes.string,
    flex: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    bd: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    bdrs: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    td: PropTypes.string,
    bgsz: PropTypes.string,
    bgp: PropTypes.string,
    bgr: PropTypes.string,
    bga: PropTypes.string,
    pos: PropTypes.string,
    top: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    left: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    bottom: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    right: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    inset: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    hiddenFrom: PropTypes.string,
    visibleFrom: PropTypes.string,

    /**
     * Dash-assigned callback that reports property changes back to Dash.
     */
    setProps: PropTypes.func,
};

DataTable.dashChildrenUpdate = true;

export default DataTable;

export const defaultProps = DataTable.defaultProps;
export const propTypes = DataTable.propTypes;

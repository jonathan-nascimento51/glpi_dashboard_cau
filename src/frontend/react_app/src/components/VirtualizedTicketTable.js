import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { memo, forwardRef, useCallback, useMemo, useRef, useState, } from 'react';
import { FixedSizeList } from 'react-window';
const priorityClasses = {
    'Very High': 'text-red-700',
    High: 'text-red-600',
    Major: 'text-red-800',
    Medium: 'text-yellow-600',
    Low: 'text-green-600',
    'Very Low': 'text-green-700',
};
const formatDate = (value) => {
    if (!value)
        return '';
    try {
        return new Intl.DateTimeFormat('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'short',
        }).format(new Date(value));
    }
    catch {
        return value;
    }
};
const Row = memo(({ index, style, data }) => {
    const row = data.rows[index];
    const handleClick = useCallback(() => data.onRowClick(row), [data, row]);
    const handleFocus = useCallback(() => data.onFocus(index), [data, index]);
    return (_jsxs("div", { style: style, role: "row", "data-row-index": index, tabIndex: 0, className: "grid grid-cols-[80px_auto_120px_100px_160px] ticket-row border-b px-2 py-1 hover:bg-gray-100 cursor-pointer", onClick: handleClick, onFocus: handleFocus, children: [_jsx("div", { role: "cell", children: row.id }), _jsx("div", { role: "cell", className: "truncate", title: row.name, children: row.name }), _jsx("div", { role: "cell", children: row.status }), _jsx("div", { role: "cell", className: priorityClasses[row.priority ?? ''], children: row.priority }), _jsx("div", { role: "cell", children: formatDate(row.date_creation) })] }));
});
Row.displayName = 'Row';
const RowGroup = forwardRef((props, ref) => _jsx("div", { ...props, ref: ref, role: "rowgroup" }));
RowGroup.displayName = 'RowGroup';
export function VirtualizedTicketTable({ rows, onRowClick, height = 400, rowHeight = 35, rowHeightClass = 'h-[35px]', }) {
    const [focusedIndex, setFocusedIndex] = useState(0);
    const containerRef = useRef(null);
    const listRef = useRef(null);
    const handleRowClick = useCallback((row) => {
        onRowClick?.(row);
    }, [onRowClick]);
    const handleRowFocus = useCallback((index) => {
        setFocusedIndex(index);
    }, []);
    const itemData = useMemo(() => ({ rows, onRowClick: handleRowClick, onFocus: handleRowFocus }), [rows, handleRowClick, handleRowFocus]);
    const focusRow = useCallback((index) => {
        setFocusedIndex(index);
        listRef.current?.scrollToItem(index);
        const selector = `[data-row-index='${index}']`;
        requestAnimationFrame(() => {
            const el = containerRef.current?.querySelector(selector);
            el?.focus();
        });
    }, []);
    const handleKeyDown = useCallback((event) => {
        const visible = Math.floor(height / rowHeight);
        let newIndex = focusedIndex;
        if (event.key === 'ArrowDown') {
            newIndex = Math.min(focusedIndex + 1, rows.length - 1);
        }
        else if (event.key === 'ArrowUp') {
            newIndex = Math.max(focusedIndex - 1, 0);
        }
        else if (event.key === 'PageDown') {
            newIndex = Math.min(focusedIndex + visible, rows.length - 1);
        }
        else if (event.key === 'PageUp') {
            newIndex = Math.max(focusedIndex - visible, 0);
        }
        else {
            return;
        }
        event.preventDefault();
        focusRow(newIndex);
    }, [focusedIndex, rows.length, height, rowHeight, focusRow]);
    if (rows.length < 100) {
        return (_jsx("div", { className: "ticket-table divide-y", role: "table", ref: containerRef, onKeyDown: handleKeyDown, children: _jsx("div", { role: "rowgroup", children: rows.map((row, idx) => (_jsxs("div", { role: "row", "data-row-index": idx, tabIndex: 0, className: `grid grid-cols-[80px_auto_120px_100px_160px] ticket-row px-2 py-1 hover:bg-gray-100 cursor-pointer ${rowHeightClass}`, onClick: () => handleRowClick(row), onFocus: () => handleRowFocus(idx), children: [_jsx("div", { role: "cell", children: row.id }), _jsx("div", { role: "cell", className: "truncate", title: row.name, children: row.name }), _jsx("div", { role: "cell", children: row.status }), _jsx("div", { role: "cell", className: priorityClasses[row.priority ?? ''], children: row.priority }), _jsx("div", { role: "cell", children: formatDate(row.date_creation) })] }, row.id))) }) }));
    }
    return (_jsx("div", { role: "table", ref: containerRef, onKeyDown: handleKeyDown, children: _jsx(FixedSizeList, { ref: listRef, height: height, itemCount: rows.length, itemSize: rowHeight, width: "100%", itemData: itemData, innerElementType: RowGroup, children: Row }) }));
}
VirtualizedTicketTable.displayName = 'VirtualizedTicketTable';

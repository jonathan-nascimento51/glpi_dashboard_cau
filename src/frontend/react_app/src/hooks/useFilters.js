import { useState } from 'react';
export function useFilters() {
    const [filters, setFilters] = useState({
        open: false,
        period: ['today'],
        level: ['n1', 'n2', 'n3', 'n4'],
        status: ['new', 'progress', 'pending', 'resolved'],
        priority: ['medium', 'low'],
    });
    const toggleFilters = () => setFilters((f) => ({ ...f, open: !f.open }));
    const toggleValue = (category, value) => {
        setFilters((f) => {
            const list = f[category];
            return {
                ...f,
                [category]: list.includes(value)
                    ? list.filter((v) => v !== value)
                    : [...list, value],
            };
        });
    };
    return { filters, toggleFilters, toggleValue };
}

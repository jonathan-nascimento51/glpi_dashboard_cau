import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen } from '@testing-library/react';
import { StatsCard } from '../StatsCard';
describe('StatsCard', () => {
    it('renders label and value', () => {
        render(_jsx(StatsCard, { label: "Total", value: 5 }));
        expect(screen.getByTestId('stats-value')).toHaveTextContent('5');
        expect(screen.getByTestId('stats-label')).toHaveTextContent('Total');
    });
});

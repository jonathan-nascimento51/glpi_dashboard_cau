import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen } from '@testing-library/react';
import Header from '../Header.js';
describe('Header', () => {
    it('renders brand title', () => {
        render(_jsx(Header, {}));
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Centro de Comando');
    });
});

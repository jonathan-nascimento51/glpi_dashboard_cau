import { Button } from './Button.js';
const meta = {
    title: 'shared/Button',
    component: Button,
    args: {
        children: 'Click me',
    },
    argTypes: {
        onClick: { action: 'clicked' },
        disabled: { control: 'boolean' },
    },
};
export default meta;
export const Primary = {};

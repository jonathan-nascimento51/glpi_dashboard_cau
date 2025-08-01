import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button.js';

const meta: Meta<typeof Button> = {
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

type Story = StoryObj<typeof Button>;

export const Primary: Story = {};

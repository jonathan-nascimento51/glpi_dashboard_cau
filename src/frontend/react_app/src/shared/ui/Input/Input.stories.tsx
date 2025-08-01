import type { Meta, StoryObj } from '@storybook/react'
import { Input } from './Input.js'

const meta: Meta<typeof Input> = {
  title: 'shared/Input',
  component: Input,
  args: { placeholder: 'Type here' },
}
export default meta

export type Story = StoryObj<typeof Input>
export const Primary: Story = {}

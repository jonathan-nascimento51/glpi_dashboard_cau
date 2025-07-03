import type { Meta, StoryObj } from '@storybook/react'
import { AddButton } from './AddButton'

const meta: Meta<typeof AddButton> = {
  title: 'features/AddToCart/AddButton',
  component: AddButton,
  args: { item: 'sample' },
}
export default meta

type Story = StoryObj<typeof AddButton>
export const Primary: Story = {}

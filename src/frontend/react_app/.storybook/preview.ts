import type { Preview } from '@storybook/react'

const preview: Preview = {
  parameters: {
    themes: {
      default: 'light',
      list: [
        { name: 'light', class: 'light', color: '#ffffff' },
        { name: 'dark', class: 'dark', color: '#000000' },
      ],
    },
  },
}

export default preview

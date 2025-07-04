import '@testing-library/jest-dom'

// Ensure react-window virtualization does not interfere with snapshots
// by wrapping list components in a simple container that renders all children.
// This mock keeps DOM structure stable across test runs.
jest.mock(
  'react-window',
  () => {
    // eslint-disable-next-line @typescript-eslint/no-var-requires, @typescript-eslint/no-require-imports
    const React = require('react')
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    function MockedList(props: any) {
      return React.createElement('div', null, props.children)
    }

    return {
      FixedSizeList: MockedList,
      VariableSizeList: MockedList,
    }
  },
  { virtual: true }
)

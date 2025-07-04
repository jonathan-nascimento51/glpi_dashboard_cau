import '@testing-library/jest-dom'

// Ensure react-window virtualization does not interfere with snapshots
// by wrapping list components in a simple container that renders all children.
// This mock keeps DOM structure stable across test runs.
jest.mock(
  'react-window',
  () => {
    const React = require('react')
    function MockedList(props) {
      return React.createElement('div', null, props.children)
    }

    return {
      FixedSizeList: MockedList,
      VariableSizeList: MockedList,
    }
  },
  { virtual: true }
)

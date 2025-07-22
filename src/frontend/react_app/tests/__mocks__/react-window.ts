import React from 'react'
import { jest } from '@jest/globals'

export const FixedSizeList = jest.fn((props: { itemCount: number; itemData: any; children: React.ReactNode }) =>
  React.createElement(
    'div',
    { 'data-testid': 'virtual-list' },
    Array.from({ length: props.itemCount }).map((_, idx: number) =>
      React.createElement(props.children as React.ElementType, { index: idx, style: {}, data: props.itemData })
    ),
  ),
)
export default { FixedSizeList }

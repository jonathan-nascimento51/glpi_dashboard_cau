import React from 'react'
import { useCartStore } from '../model/cartStore'

const AddButtonComponent: React.FC<{ item: string }> = ({ item }) => {
  const addItem = useCartStore((s) => s.addItem)
  return (
    <button type="button" onClick={() => addItem(item)}>
      Add to Cart
    </button>
  )
}

export const AddButton = React.memo(AddButtonComponent)

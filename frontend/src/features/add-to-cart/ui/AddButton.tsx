import React from 'react'
import { useCartStore } from '../model/cartStore'

export const AddButton: React.FC<{ item: string }> = ({ item }) => {
  const addItem = useCartStore((s) => s.addItem)
  return (
    <button type="button" onClick={() => addItem(item)}>
      Add to Cart
    </button>
  )
}

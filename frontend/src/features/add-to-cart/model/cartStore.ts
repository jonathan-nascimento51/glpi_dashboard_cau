import { create } from 'zustand'

interface CartState {
  items: string[]
  addItem: (item: string) => void
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  addItem: (item) => set((s) => ({ items: [...s.items, item] })),
}))

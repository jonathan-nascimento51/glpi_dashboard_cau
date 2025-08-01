import { useState } from 'react'

export interface FiltersState {
  open: boolean
  period: string[]
  level: string[]
  status: string[]
  priority: string[]
}

export const DEFAULT_FILTERS: FiltersState = {
  open: false,
  period: ['today'],
  level: ['n1', 'n2', 'n3', 'n4'],
  status: ['new', 'progress', 'pending', 'resolved'],
  priority: ['medium', 'low'],
}

export function useFilters(initial: FiltersState = DEFAULT_FILTERS) {
  const [filters, setFilters] = useState<FiltersState>({ ...initial })

  const toggleFilters = () => setFilters((f) => ({ ...f, open: !f.open }))

  const toggleValue = (
    category: keyof Omit<FiltersState, 'open'>,
    value: string,
  ) => {
    setFilters((f) => {
      const list = f[category]
      return {
        ...f,
        [category]: list.includes(value)
          ? list.filter((v) => v !== value)
          : [...list, value],
      }
    })
  }

  return { filters, toggleFilters, toggleValue }
}

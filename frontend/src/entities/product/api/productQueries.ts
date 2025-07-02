import { useQuery } from '@tanstack/react-query'

export const productKeys = {
  all: ['products'] as const,
  detail: (id: string) => [...productKeys.all, id] as const,
}

export function useProducts() {
  return useQuery({
    queryKey: productKeys.all,
    queryFn: async () => {
      const res = await fetch('/api/products')
      if (!res.ok) throw new Error('Failed to fetch products')
      return res.json()
    },
  })
}

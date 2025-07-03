export async function fetcher<T>(url: string): Promise<T> {
  const base = import.meta.env.VITE_API_URL || ''
  const res = await fetch(`${base}${url}`)
  if (!res.ok) {
    throw new Error('Failed to fetch')
  }
  return res.json() as Promise<T>
}

export interface FilterQuery {
  [key: string]: string[] | boolean | undefined
}

/**
 * Convert filter values into a stable query string.
 * `open` is ignored because it only controls panel visibility.
 */
export function buildQueryString(filters?: FilterQuery): string {
  if (!filters) return ''
  const entries = Object.entries(filters)
    .filter(([key]) => key !== 'open')
    .sort(([a], [b]) => a.localeCompare(b))
  const params = new URLSearchParams()
  for (const [key, value] of entries) {
    if (Array.isArray(value)) {
      const sortedValues = [...value].sort()
      for (const v of sortedValues) params.append(key, v)
    } else if (value != null) {
      params.append(key, String(value))
    }
  }
  const str = params.toString()
  return str ? `?${str}` : ''
}

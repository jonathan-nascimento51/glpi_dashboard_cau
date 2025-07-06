export async function fetcher<T>(url: string, init: RequestInit = {}): Promise<T> {
  const base =
    typeof import.meta !== 'undefined'
      ? import.meta.env.NEXT_PUBLIC_API_BASE_URL
      : process.env.NEXT_PUBLIC_API_BASE_URL

  const res = await fetch(`${base ?? ''}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(init.headers ?? {}),
    },
    ...init,
  })

  if (res.status >= 400) {
    const message = await res.text()
    throw new Error(message || `Request failed with status ${res.status}`)
  }

  return res.json() as Promise<T>
}

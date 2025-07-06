export async function fetcher<T>(url: string, init: RequestInit = {}): Promise<T> {
  const base =
    typeof import.meta !== 'undefined'
      ? import.meta.env.NEXT_PUBLIC_API_BASE_URL
      : process.env.NEXT_PUBLIC_API_BASE_URL

  if (!base) {
    console.error('Environment variable NEXT_PUBLIC_API_BASE_URL is not set')
    throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable not configured')
  }

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
    const error = new Error(message || res.statusText)
    ;(error as any).status = res.status
    ;(error as any).statusText = res.statusText
    throw error
  }

  return res.json() as Promise<T>
}

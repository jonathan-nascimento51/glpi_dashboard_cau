export async function fetcher<T>(url: string, init: RequestInit = {}): Promise<T> {
  const base = import.meta.env.NEXT_PUBLIC_API_BASE_URL

  if (!base) {
    console.error('Environment variable NEXT_PUBLIC_API_BASE_URL is not set')
    throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable not configured')
  }

  let res: Response

  try {
    res = await fetch(`${base ?? ''}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(init.headers ?? {}),
      },
      ...init,
    })
  } catch (err) {
    const error = new Error('Network error')
    ;(error as any).cause = err
    throw error
  }

  if (res.status >= 400) {
    const message = await res.text()
    const error = new Error(message || res.statusText)
    ;(error as any).status = res.status
    ;(error as any).statusText = res.statusText
    throw error
  }

  const contentType = res.headers.get('content-type') ?? ''
  const body = await res.text()

  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(body) as T
    } catch {
      return body as unknown as T
    }
  }

  return body as unknown as T
}

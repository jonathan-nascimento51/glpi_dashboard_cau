import type { paths } from './types'

export async function createUser(
  data: paths['/api/users']['post']['requestBody']['content']['application/json'],
  signal?: AbortSignal
): Promise<Response> {
  return fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: { 'Content-Type': 'application/json' },
    signal,
  })
}

import { fetcher } from '../../src/lib/swrClient'

beforeEach(() => {
  ;(import.meta as any).env = { NEXT_PUBLIC_API_BASE_URL: 'http://localhost' }
})

test('fetcher returns json on success', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    headers: { get: () => 'application/json' },
    json: () => Promise.resolve({ ok: true }),
    text: () => Promise.resolve(JSON.stringify({ ok: true })),
  }) as jest.Mock

  const data = await fetcher('/foo')
  expect(data).toEqual({ ok: true })
})

test('fetcher throws on error status', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 404,
    statusText: 'Not Found',
    text: () => Promise.resolve('missing'),
  }) as jest.Mock

  await expect(fetcher('/foo')).rejects.toMatchObject({
    message: 'missing',
    status: 404,
    statusText: 'Not Found',
  })
})

test('fetcher throws network error', async () => {
  global.fetch = jest.fn().mockRejectedValue(new Error('Failed'))

  await expect(fetcher('/foo')).rejects.toMatchObject({ message: 'Network error' })
})

test('fetcher returns text for non-JSON response', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    headers: { get: () => 'text/plain' },
    text: () => Promise.resolve('plain'),
  }) as jest.Mock

  const data = await fetcher('/foo')
  expect(data).toBe('plain')
})

test('fetcher returns text when JSON parse fails', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    headers: { get: () => 'application/json' },
    text: () => Promise.resolve('invalid'),
  }) as jest.Mock

  const data = await fetcher('/foo')
  expect(data).toBe('invalid')
})


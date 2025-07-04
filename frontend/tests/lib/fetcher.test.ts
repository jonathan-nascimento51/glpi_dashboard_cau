import { fetcher } from '@/lib/swrClient'

test('fetcher returns json on success', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 200,
    json: () => Promise.resolve({ ok: true }),
    text: () => Promise.resolve(''),
  }) as jest.Mock

  const data = await fetcher('/foo')
  expect(data).toEqual({ ok: true })
})

test('fetcher throws on error status', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    status: 404,
    text: () => Promise.resolve('missing'),
  }) as jest.Mock

  await expect(fetcher('/foo')).rejects.toThrow('missing')
})

import { renderHook, waitFor } from '@testing-library/react'
import axios from 'axios'
import { useApiQuery } from '../useApiQuery'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

process.env.NEXT_PUBLIC_API_BASE_URL = 'http://test-api.com'

// Helper to make fetch use axios under the hood
beforeEach(() => {
  mockedAxios.mockReset()
  global.fetch = jest.fn((url: RequestInfo, options?: RequestInit) =>
    mockedAxios.get(url.toString(), { signal: options?.signal }).then(res => ({
      ok: true,
      status: 200,
      json: async () => res.data,
    }))
  ) as unknown as typeof fetch
})

describe('useApiQuery', () => {
  it('updates state on success', async () => {
    mockedAxios.get.mockResolvedValue({ data: { foo: 'bar' } })
    const { result } = renderHook(() => useApiQuery('/test'))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toEqual({ foo: 'bar' })
    expect(result.current.error).toBeNull()
  })

  it('updates state on error', async () => {
    mockedAxios.get.mockRejectedValue(new Error('fail'))
    const { result } = renderHook(() => useApiQuery('/test'))
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBe('fail')
  })

  it('ignores abort errors', async () => {
    mockedAxios.get.mockRejectedValue({ name: 'AbortError', message: 'aborted' })
    const { result } = renderHook(() => useApiQuery('/test'))
    await waitFor(() => expect(mockedAxios.get).toHaveBeenCalled())
    expect(result.current.isLoading).toBe(true)
    expect(result.current.error).toBeNull()
  })
})

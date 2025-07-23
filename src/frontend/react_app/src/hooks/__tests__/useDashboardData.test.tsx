import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useDashboardData } from '../useDashboardData'
import { useApiQuery } from '../useApiQuery'

jest.mock('../useApiQuery')

describe('useDashboardData refresh interval', () => {
  beforeAll(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = 'http://test'
  })

  beforeEach(() => {
    (useApiQuery as jest.Mock).mockReturnValue({
      data: { status: {} },
      isLoading: false,
      error: null,
    })
  })

  afterAll(() => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL
  })
  it('clears refresh interval on unmount', () => {
    const clearSpy = jest.spyOn(global, 'clearInterval')
    const setSpy = jest
      .spyOn(global, 'setInterval')
      .mockReturnValue(123 as unknown as NodeJS.Timer)

    const queryClient = new QueryClient()
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
    const { unmount } = renderHook(() => useDashboardData(), { wrapper })
    unmount()
    expect(clearSpy).toHaveBeenCalledWith(123)
    setSpy.mockRestore()
  })
})

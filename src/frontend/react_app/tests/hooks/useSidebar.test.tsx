import { renderHook, act } from '@testing-library/react'
import { SidebarProvider, useSidebar } from '@/hooks/useSidebar'

test('toggles sidebar state', () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <SidebarProvider>{children}</SidebarProvider>
  )
  const { result } = renderHook(() => useSidebar(), { wrapper })
  act(() => result.current.toggle())
  expect(result.current.open).toBe(true)
})

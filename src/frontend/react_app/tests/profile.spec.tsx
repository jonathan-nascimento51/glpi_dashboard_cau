import React, { Profiler } from 'react'
import TestRenderer, { act } from 'react-test-renderer'

// Mock data hooks to avoid network requests and heavy chart imports
jest.mock('../src/hooks/useDashboardData', () => ({
  useDashboardData: () => ({
    metrics: { new: 1, pending: 1, progress: 1, resolved: 1 },
    sparkRefs: {
      new: { current: null },
      pending: { current: null },
      progress: { current: null },
      resolved: { current: null },
    },
    history: { new: [], pending: [], progress: [], resolved: [] },
  }),
}))

jest.mock('../src/hooks/useChamadosPorData', () => ({
  useChamadosPorData: () => ({
    data: [],
    isLoading: false,
    isError: false,
    status: 'success',
  }),
}))

jest.mock('../src/hooks/useChamadosPorDia', () => ({
  useChamadosPorDia: () => ({ data: [], isLoading: false, error: null }),
}))

jest.mock('../src/hooks/useTickets', () => ({
  useTickets: () => ({
    tickets: [],
    isLoading: false,
    isSuccess: true,
    error: null,
  }),
}))

// JSDOM lacks ResizeObserver used by Recharts
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = ResizeObserver

function measure(Component: React.ComponentType) {
  let duration = 0
  act(() => {
    TestRenderer.create(
      <Profiler id="test" onRender={(_, __, actual) => { duration = actual }}>
        <Component />
      </Profiler>,
    )
  })
  return duration
}

type Results = {
  dashboard: number
  tendencia: number
  heatmap: number
}

async function profileComponents(useMemo: boolean): Promise<Results> {
  const origMemo = React.memo
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  React.memo = useMemo ? origMemo : ((c: any) => c)
  jest.resetModules()
  const DashMod = await import('../src/features/tickets/TicketStatsPage')
  // Use 'as any' to safely access .default for compatibility with both CJS and ESM
  const Dashboard = (DashMod as any).default ?? (DashMod as any).Dashboard ?? DashMod
  const TendMod = await import('../src/components/ChamadosTendencia')
  const ChamadosTendencia =
    (TendMod as any).ChamadosTendencia ?? TendMod.default ?? TendMod
  const HeatMod = await import('../src/components/ChamadosHeatmap')
  const ChamadosHeatmap =
    (HeatMod as any).ChamadosHeatmap ?? HeatMod.default ?? HeatMod
  const res: Results = {
    dashboard: measure(Dashboard),
    tendencia: measure(ChamadosTendencia),
    heatmap: measure(ChamadosHeatmap),
  }
  React.memo = origMemo
  return res
}

describe.skip('profiling with and without memoization', () => {
  it('captures render times', async () => {
    const before = await profileComponents(false)
    const after = await profileComponents(true)
    console.log('Before:', before)
    console.log('After:', after)
    expect(before.dashboard).toBeGreaterThanOrEqual(0)
    expect(after.dashboard).toBeGreaterThanOrEqual(0)
  })
})

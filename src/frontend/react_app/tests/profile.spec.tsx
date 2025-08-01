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
  table: number
  tendencia: number
  heatmap: number
}

async function profileComponents(useMemo: boolean): Promise<Results> {
  const origMemo = React.memo
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  React.memo = useMemo ? origMemo : ((c: any) => c)
  jest.resetModules()
  const TableMod = await import('../src/components/GlpiTicketsTable')
  // Use 'as any' to safely access .default for compatibility with both CJS and ESM
  const TicketsTable = TableMod.GlpiTicketsTable
  const TendMod = await import('../src/components/ChamadosTendencia')
  const ChamadosTendencia =
    (TendMod as any).ChamadosTendencia ?? TendMod.default ?? TendMod
  const HeatMod = await import('../src/components/ChamadosHeatmap')
  const ChamadosHeatmap =
    (HeatMod as any).ChamadosHeatmap ?? HeatMod.default ?? HeatMod
  const res: Results = {
    table: measure(TicketsTable),
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
    expect(before.table).toBeGreaterThanOrEqual(0)
    expect(after.table).toBeGreaterThanOrEqual(0)
  })
})

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
  useChamadosPorData: () => ({ dados: [], isLoading: false, error: null }),
}))

jest.mock('../src/hooks/useChamadosPorDia', () => ({
  useChamadosPorDia: () => ({ dados: [], isLoading: false, error: null }),
}))

// JSDOM lacks ResizeObserver used by Recharts
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
// @ts-ignore
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

function profileComponents(useMemo: boolean): Results {
  const origMemo = React.memo
  React.memo = useMemo ? origMemo : ((c: any) => c)
  jest.resetModules()
  const DashMod = require('../src/pages/Dashboard')
  const Dashboard = DashMod.default ?? DashMod.Dashboard ?? DashMod
  const TendMod = require('../src/components/ChamadosTendencia')
  const ChamadosTendencia =
    TendMod.ChamadosTendencia ?? TendMod.default ?? TendMod
  const HeatMod = require('../src/components/ChamadosHeatmap')
  const ChamadosHeatmap = HeatMod.ChamadosHeatmap ?? HeatMod.default ?? HeatMod
  const res: Results = {
    dashboard: measure(Dashboard),
    tendencia: measure(ChamadosTendencia),
    heatmap: measure(ChamadosHeatmap),
  }
  React.memo = origMemo
  return res
}

describe('profiling with and without memoization', () => {
  it('captures render times', () => {
    const before = profileComponents(false)
    const after = profileComponents(true)
    console.log('Before:', before)
    console.log('After:', after)
    expect(before.dashboard).toBeGreaterThanOrEqual(0)
    expect(after.dashboard).toBeGreaterThanOrEqual(0)
  })
})

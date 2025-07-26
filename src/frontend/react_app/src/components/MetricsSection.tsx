import { Suspense, lazy } from 'react'
import TicketsDisplay from './TicketsDisplay'
import SkeletonChart from './SkeletonChart'
import SkeletonHeatmap from './SkeletonHeatmap'

const ChamadosTendencia = lazy(() => import('./ChamadosTendencia'))
const ChamadosHeatmap = lazy(() => import('./ChamadosHeatmap'))

export default function MetricsSection() {
  return (
    <section className="metrics-section">
      <TicketsDisplay />
      <Suspense fallback={<SkeletonChart />}>
        <ChamadosTendencia />
      </Suspense>
      <Suspense fallback={<SkeletonHeatmap />}>
        <ChamadosHeatmap />
      </Suspense>
    </section>
  )
}

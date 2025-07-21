import { Suspense } from 'react'
import Header from './components/Header'
import FilterPanel from './components/FilterPanel'
import { Sidebar } from './components/Sidebar'
import { LevelsPanel } from './components/LevelsPanel'
import TicketsDisplay from './components/TicketsDisplay'
import SkeletonChart from './components/SkeletonChart'
import SkeletonHeatmap from './components/SkeletonHeatmap'

// Lazy load heavy components to split them into separate chunks.
// This tells Vite/Rollup to create separate .js files for these components.
const ChamadosTendencia = React.lazy(() => import('./components/ChamadosTendencia'))
const ChamadosHeatmap = React.lazy(() => import('./components/ChamadosHeatmap'))

function App() {
  return (
    <div className="app-container">
      <Header />
      <FilterPanel />
      <main className="main-content">
        <div className="dashboard-grid">
          <TicketsDisplay />
          {/* The Suspense component shows a fallback (like a skeleton loader) while the component is loading */}
          <Suspense fallback={<SkeletonChart />}>
            <ChamadosTendencia />
          </Suspense>
          <Suspense fallback={<SkeletonHeatmap />}>
            <ChamadosHeatmap />
          </Suspense>
          <LevelsPanel levels={[]} />
        </div>
        <Sidebar performance={[]} ranking={[]} alerts={[]} />
      </main>
    </div>
  )
}

export default App

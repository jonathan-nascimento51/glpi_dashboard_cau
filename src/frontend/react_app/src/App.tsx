import { Suspense, lazy } from 'react'
import Header from './components/Header'
import { ErrorBoundary } from './components/ErrorBoundary'
import FilterPanel from './components/FilterPanel'
import { Sidebar } from './components/Sidebar'
import SidebarToggle from './components/SidebarToggle'
import { LevelsPanel } from './components/LevelsPanel'
import TicketsDisplay from './components/TicketsDisplay'
import SkeletonChart from './components/SkeletonChart'
import SkeletonHeatmap from './components/SkeletonHeatmap'
import { SidebarProvider } from './hooks/useSidebar'

// Lazy load heavy components to split them into separate chunks.
// This tells Vite/Rollup to create separate .js files for these components.
const ChamadosTendencia = lazy(() => import('./components/ChamadosTendencia'))
const ChamadosHeatmap = lazy(() => import('./components/ChamadosHeatmap'))

function App() {
  return (
    <ErrorBoundary>
      <SidebarProvider>
        <div className="app-container">
          <Header />
          <FilterPanel />
          <SidebarToggle />
          <main className="main-content">
            <div className="dashboard-grid">
              <TicketsDisplay />
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
      </SidebarProvider>
    </ErrorBoundary>
  )
}

export default App

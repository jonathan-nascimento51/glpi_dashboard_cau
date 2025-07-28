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
import { NotificationProvider } from './context/notification'
import NotificationToast from './components/NotificationToast'
import { useHotkeys } from './hooks/useHotkeys'

// Lazy load heavy components to split them into separate chunks.
// This tells Vite/Rollup to create separate .js files for these components.
const ChamadosTendencia = lazy(() => import('./components/ChamadosTendencia'))
const ChamadosHeatmap = lazy(() => import('./components/ChamadosHeatmap'))

function App() {
  useHotkeys()
  // useLevelsMetrics() apenas executa efeitos, não passa dados para LevelsPanel

  return (
    <ErrorBoundary>
      <NotificationProvider>
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
                <LevelsPanel />
              </div>
              <Sidebar performance={[]} ranking={[]} alerts={[]} />
            </main>
            <NotificationToast />
          </div>
        </SidebarProvider>
      </NotificationProvider>
    </ErrorBoundary>
  )
}

export default App

import { ErrorBoundary } from './components/ErrorBoundary'
import DashboardLayout from './components/DashboardLayout'
import { SidebarProvider } from './hooks/useSidebar'
import { NotificationProvider } from './context/notification'
import { useHotkeys } from './hooks/useHotkeys'

function App() {
  useHotkeys()
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <SidebarProvider>
          <DashboardLayout />
        </SidebarProvider>
      </NotificationProvider>
    </ErrorBoundary>
  )
}

export default App

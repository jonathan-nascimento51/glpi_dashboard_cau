import FilterPanel from './FilterPanel'
import Header from './Header'
import MetricsSection from './MetricsSection'
import LevelsSection from './LevelsSection'
import { Sidebar } from './Sidebar'
import SidebarToggle from './SidebarToggle'
import NotificationToast from './NotificationToast'

export default function DashboardLayout() {
  return (
    <div className="dashboard-container">
      <Header />
      <FilterPanel />
      <SidebarToggle />
      <main className="main-content">
        <div className="flex flex-col gap-6 flex-1 overflow-auto">
          <MetricsSection />
          <LevelsSection />
        </div>
        <Sidebar performance={[]} ranking={[]} alerts={[]} />
      </main>
      <NotificationToast />
    </div>
  )
}

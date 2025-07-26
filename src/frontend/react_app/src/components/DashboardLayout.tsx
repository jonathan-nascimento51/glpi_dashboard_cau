import FilterPanel from './FilterPanel'
import { Header } from './Header'
import { MetricsSection } from './MetricsSection'
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
        <div className="dashboard-grid">
          <MetricsSection />
          <LevelsSection />
        </div>
        <Sidebar performance={[]} ranking={[]} alerts={[]} />
      </main>
      <NotificationToast />
    </div>
  )
}

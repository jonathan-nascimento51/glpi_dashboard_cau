import { Header } from './components/Header'
import { FilterDrawer } from './components/FilterDrawer'
import { MetricsSection } from './components/MetricsSection'

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <FilterDrawer />
      <main className="p-4">
        <MetricsSection />
      </main>
    </div>
  )
}

export default App

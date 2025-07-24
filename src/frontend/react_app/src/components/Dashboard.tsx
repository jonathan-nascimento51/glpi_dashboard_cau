import { useEffect, useState } from 'react'
import axios from 'axios'
import type { MetricsOverview, LevelMetrics } from '../types/metricsOverview'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'

interface MetricCardProps {
  level: string
  data: LevelMetrics
}

function MetricCard({ level, data }: MetricCardProps) {
  return (
    <div className="border rounded p-4 shadow flex-1 min-w-[200px]" data-testid={`card-${level}`}>
      <h3 className="text-lg font-semibold mb-2">Nível {level}</h3>
      <p>Abertos: {data.open}</p>
      <p>Fechados: {data.closed}</p>
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricsOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const source = axios.CancelToken.source()

    const fetchMetrics = async () => {
      try {
        const res = await axios.get('/metrics/overview', { cancelToken: source.token })
        setMetrics(res.data)
        setError('')
      } catch (err) {
        if (!axios.isCancel(err)) {
          setError('Não foi possível carregar as métricas. Tente novamente mais tarde.')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
    const id = setInterval(fetchMetrics, 60000)
    return () => {
      clearInterval(id)
      source.cancel('unmounted')
    }
  }, [])

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={() => { setLoading(true); setError(''); }} />
  }

  return (
    <div className="dashboard grid gap-4 sm:grid-cols-2 md:grid-cols-4" data-testid="dashboard">
      {metrics && Object.entries(metrics).map(([level, data]) => (
        <MetricCard key={level} level={level} data={data} />
      ))}
    </div>
  )
}

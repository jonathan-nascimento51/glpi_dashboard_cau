"use client"
import React, { Suspense, useCallback, useMemo } from 'react'
import dynamic from 'next/dynamic'
import Header from '../components/Header'
import { MetricCard } from '../components/MetricCard'
import { LevelsPanel } from '../components/LevelsPanel'
import { Sidebar } from '../components/Sidebar'
import FilterPanel from '../components/FilterPanel'
import SkeletonChart from '../components/SkeletonChart'
import SkeletonHeatmap from '../components/SkeletonHeatmap'
import { VirtualizedTicketTable } from '../components/VirtualizedTicketTable'
import { useDashboardData } from '../hooks/useDashboardData'
import { useTickets } from '../hooks/useTickets'

const ChamadosTendencia = dynamic(
  () =>
    import('../components/ChamadosTendencia').then(
      (mod) => mod.ChamadosTendencia,
    ),
  { ssr: false, suspense: true },
)

const ChamadosHeatmap = dynamic(
  () =>
    import('../components/ChamadosHeatmap').then(
      (mod) => mod.ChamadosHeatmap,
    ),
  { ssr: false, suspense: true },
)

const Dashboard: React.FC = () => {
  const { metrics, sparkRefs } = useDashboardData()
  const { tickets } = useTickets()

  const levels = useMemo(() => {
    const groups = new Map<string, { new: number; progress: number; pending: number; resolved: number }>()
    tickets?.forEach((t) => {
      const group = String(t.group ?? 'N1')
      const status = String(t.status ?? '').toLowerCase()
      const m =
        groups.get(group) ??
        { new: 0, progress: 0, pending: 0, resolved: 0 }
      if (status === 'new') m.new += 1
      else if (status === 'pending') m.pending += 1
      else if (status === 'progress') m.progress += 1
      else if (status === 'resolved' || status === 'closed') m.resolved += 1
      groups.set(group, m)
    })
    return Array.from(groups.entries()).map(([name, metrics]) => ({
      name,
      metrics,
    }))
  }, [tickets])

  const performance = useMemo(
    () => [
      { label: 'Taxa de Resolução', value: '94.2%', barWidth: '94%' },
      { label: 'Tempo Médio', value: '2.4h', barWidth: '76%' },
      { label: 'Satisfação', value: '4.8/5', barWidth: '96%' },
      { label: 'Eficiência', value: '87.1%', barWidth: '87%' },
    ],
    [],
  )

  const ranking = useMemo(
    () => [
      { name: 'Gabriel Silva', level: 'N4', score: 247 },
      { name: 'Ana Costa', level: 'N3', score: 231 },
    ],
    [],
  )

  const alerts = useMemo(
    () => [
      {
        type: 'critical',
        icon: 'exclamation-triangle',
        text: 'Servidor principal com alta latência',
        time: '2min',
      },
    ],
    [],
  )

  type MetricType = 'new' | 'pending' | 'progress' | 'resolved'

  const handleMetricClick = useCallback((type: MetricType) => {
    console.log(`metric clicked: ${type}`)
  }, [])

  const handleNewClick = useCallback(
    () => handleMetricClick('new'),
    [handleMetricClick],
  )

  const handlePendingClick = useCallback(
    () => handleMetricClick('pending'),
    [handleMetricClick],
  )

  const handleProgressClick = useCallback(
    () => handleMetricClick('progress'),
    [handleMetricClick],
  )

  const handleResolvedClick = useCallback(
    () => handleMetricClick('resolved'),
    [handleMetricClick],
  )

  const ticketsList = tickets ?? []


  const handleRowClick = useCallback((row: { id: number; name: string }) => {
    console.log('row clicked', row.id)
  }, [])

  return (
    <div className="dashboard-container">
      <Header />
      <FilterPanel />
      <main className="main-content" id="mainContent">
        <div className="metrics-section">
          <div className="metrics-grid">
            <MetricCard
              type="new"
              value={metrics.new}
              change={5}
              onClick={handleNewClick}
              canvasRef={sparkRefs.new}
            />
            <MetricCard
              type="pending"
              value={metrics.pending}
              change={-3}
              onClick={handlePendingClick}
              canvasRef={sparkRefs.pending}
            />
            <MetricCard
              type="progress"
              value={metrics.progress}
              change={2}
              onClick={handleProgressClick}
              canvasRef={sparkRefs.progress}
            />
            <MetricCard
              type="resolved"
              value={metrics.resolved}
              change={8}
              onClick={handleResolvedClick}
              canvasRef={sparkRefs.resolved}
            />
          </div>
          <div className="bottom-section">
            <LevelsPanel levels={levels} />
            <Suspense fallback={<SkeletonChart />}>
              <ChamadosTendencia />
            </Suspense>
          </div>
          <div className="my-4">
            <Suspense fallback={<SkeletonHeatmap />}>
              <ChamadosHeatmap />
            </Suspense>
          </div>
          <div className="my-4">
            <VirtualizedTicketTable rows={ticketsList} onRowClick={handleRowClick} />
          </div>
        </div>
        <Sidebar performance={performance} ranking={ranking} alerts={alerts} />
      </main>
      <footer className="footer">
        <div className="footer-left">
          <div className="footer-item">
            <div className="footer-status" />
            <span>Sistema Online</span>
          </div>
          <div className="footer-item">
            <span>
              Usuários Ativos: <span id="activeUsers">47</span>
            </span>
          </div>
          <div className="footer-item">
            <span>
              Uptime: <span id="uptime">99.97%</span>
            </span>
          </div>
        </div>
        <div className="footer-right">
          Última atualização: <span id="lastUpdate" />
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

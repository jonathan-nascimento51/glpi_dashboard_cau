"use client"
import React from 'react'
import Header from '../components/Header'
import { MetricCard } from '../components/MetricCard'
import { LevelsPanel } from '../components/LevelsPanel'
import { Sidebar } from '../components/Sidebar'
import FilterPanel from '../components/FilterPanel'
import ChamadosTendencia from '../components/ChamadosTendencia'
import ChamadosHeatmap from '../components/ChamadosHeatmap'
import { useDashboardData } from '../hooks/useDashboardData'

const Dashboard: React.FC = () => {
  const { metrics, sparkRefs } = useDashboardData()

  const levels = [
    {
      name: 'N1 - Básico',
      metrics: { new: 15, progress: 12, pending: 4, resolved: 28 },
    },
    {
      name: 'N2 - Intermediário',
      metrics: { new: 12, progress: 15, pending: 4, resolved: 18 },
    },
    {
      name: 'N3 - Avançado',
      metrics: { new: 8, progress: 6, pending: 2, resolved: 10 },
    },
    {
      name: 'N4 - Especialista',
      metrics: { new: 6, progress: 4, pending: 1, resolved: 6 },
    },
  ]

  const performance = [
    { label: 'Taxa de Resolução', value: '94.2%', barWidth: '94%' },
    { label: 'Tempo Médio', value: '2.4h', barWidth: '76%' },
    { label: 'Satisfação', value: '4.8/5', barWidth: '96%' },
    { label: 'Eficiência', value: '87.1%', barWidth: '87%' },
  ]

  const ranking = [
    { name: 'Gabriel Silva', level: 'N4', score: 247 },
    { name: 'Ana Costa', level: 'N3', score: 231 },
  ]

  const alerts = [
    {
      type: 'critical',
      icon: 'exclamation-triangle',
      text: 'Servidor principal com alta latência',
      time: '2min',
    },
  ]

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
              onClick={() => {}}
              canvasRef={sparkRefs.new}
            />
            <MetricCard
              type="pending"
              value={metrics.pending}
              change={-3}
              onClick={() => {}}
              canvasRef={sparkRefs.pending}
            />
            <MetricCard
              type="progress"
              value={metrics.progress}
              change={2}
              onClick={() => {}}
              canvasRef={sparkRefs.progress}
            />
            <MetricCard
              type="resolved"
              value={metrics.resolved}
              change={8}
              onClick={() => {}}
              canvasRef={sparkRefs.resolved}
            />
          </div>
          <div className="bottom-section">
            <LevelsPanel levels={levels} />
            <ChamadosTendencia />
          </div>
          <div className="my-4">
            <ChamadosHeatmap />
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

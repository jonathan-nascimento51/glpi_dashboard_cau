import React from 'react'

export interface PerformanceMetric {
  label: string
  value: string
  barWidth: string
}

export interface RankingItem {
  name: string
  level: string
  score: number
}

export interface AlertItem {
  type: string
  icon: string
  text: string
  time: string
}

export interface SidebarProps {
  performance: PerformanceMetric[]
  ranking: RankingItem[]
  alerts: AlertItem[]
}

const SidebarComponent: React.FC<SidebarProps> = ({ performance, ranking, alerts }) => (
  <aside className="sidebar">
    <div className="sidebar-card">
      <div className="sidebar-header">
        <i className="fas fa-chart-line sidebar-icon" />
        <div className="sidebar-title">Performance do Sistema</div>
      </div>
      <div className="performance-metrics">
        {performance.map((p) => (
          <div key={p.label} className="performance-item">
            <div className="performance-header">
              <span className="performance-label">{p.label}</span>
              <span className="performance-value">{p.value}</span>
            </div>
            <div className="performance-bar">
              <div className={`performance-fill w-[${p.barWidth}]`} />
            </div>
          </div>
        ))}
      </div>
    </div>
    <div className="sidebar-card ranking-section">
      <div className="sidebar-header">
        <i className="fas fa-trophy sidebar-icon" />
        <div className="sidebar-title">Ranking de Técnicos</div>
      </div>
      <div className="ranking-list">
        {ranking.map((r) => (
          <div key={r.name} className="ranking-item">
            <span>{r.name}</span>
            <span>{r.level}</span>
            <span>{r.score}</span>
          </div>
        ))}
      </div>
    </div>
    <div className="sidebar-card alerts-section">
      <div className="sidebar-header">
        <i className="fas fa-exclamation-triangle sidebar-icon" />
        <div className="sidebar-title">Alertas Recentes</div>
      </div>
      <div className="alerts-list">
        {alerts.map((a, idx) => (
          <div key={idx} className={`alert-item ${a.type}`}>
            <i className={`fas fa-${a.icon}`} />
            <span>{a.text}</span>
            <small>{a.time}</small>
          </div>
        ))}
      </div>
    </div>
  </aside>
)

export const Sidebar = React.memo(SidebarComponent)

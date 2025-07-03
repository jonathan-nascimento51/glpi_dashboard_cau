import React from 'react'

interface LevelData {
  name: string
  metrics: { new: number; progress: number; pending: number; resolved: number }
}

interface Props {
  levels: LevelData[]
}

const LevelsPanel: React.FC<Props> = ({ levels }) => {
  return (
    <div className="levels-section">
      <div className="levels-header">
        <div>
          <div className="levels-title">Distribuição por Níveis</div>
          <div className="levels-subtitle">Visão detalhada por categoria</div>
        </div>
      </div>
      <div className="levels-grid">
        {levels.map((level) => (
          <div
            key={level.name}
            className={`level-card ${level.name.toLowerCase()}`}
          >
            <div className="level-header">
              <div className="level-badge">{level.name}</div>
            </div>
            <div className="level-metrics">
              <div className="level-metric">
                <span className="level-metric-label">Novos</span>
                <span className="level-metric-value">{level.metrics.new}</span>
              </div>
              <div className="level-metric">
                <span className="level-metric-label">Progresso</span>
                <span className="level-metric-value">
                  {level.metrics.progress}
                </span>
              </div>
              <div className="level-metric">
                <span className="level-metric-label">Pendente</span>
                <span className="level-metric-value">
                  {level.metrics.pending}
                </span>
              </div>
              <div className="level-metric">
                <span className="level-metric-label">Resolvido</span>
                <span className="level-metric-value">
                  {level.metrics.resolved}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default LevelsPanel

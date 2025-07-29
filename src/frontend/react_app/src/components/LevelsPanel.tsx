import { memo, type FC, useCallback } from 'react'
import { useModal } from '../hooks/useModal'
import { useMetricsLevels } from '../hooks/useMetricsLevels'

export interface LevelData {
  name: string
  metrics: { new: number; progress: number; pending: number; resolved: number }
}

const LevelsPanelComponent: FC = () => {
  const { levels, isLoading, isError } = useMetricsLevels()
  const { openModal, modalElement } = useModal()

  const showDetails = useCallback(
    (level: LevelData) => {
      openModal(
        <div>
          <h2 className="text-xl font-bold mb-4">{level.name}</h2>
          <ul className="space-y-2">
            <li>Novos: {level.metrics.new}</li>
            <li>Progresso: {level.metrics.progress}</li>
            <li>Pendente: {level.metrics.pending}</li>
            <li>Resolvido: {level.metrics.resolved}</li>
          </ul>
        </div>,
      )
    },
    [openModal],
  )

  return (
    <div className="levels-section">
      <div className="levels-header">
        <div>
          <div className="levels-title">Distribuição por Níveis</div>
          <div className="levels-subtitle">Visão detalhada por categoria</div>
        </div>
      </div>
      <div className="levels-grid">
        {isLoading && <span>Carregando...</span>}
        {isError && <span>Erro ao carregar métricas</span>}
        {!isLoading && !isError && levels?.length === 0 && (
          <span>Nenhum dado disponível</span>
        )}
        {levels?.map((level) => (
          <button
            key={level.name}
            className={`level-card ${level.name
              .toLowerCase()
              .replace(/\s+/g, '-')}`}
            onClick={() => showDetails(level)}
            role="button"
            aria-label={`View details for ${level.name}`}
            type="button"
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
          </button>
        ))}
      </div>
      {modalElement}
    </div>
  )
}

export const LevelsPanel = memo(LevelsPanelComponent)

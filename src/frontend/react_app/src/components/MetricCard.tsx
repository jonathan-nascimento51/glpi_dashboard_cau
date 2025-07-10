import { memo, type FC } from 'react'

export interface MetricCardProps {
  type: 'new' | 'pending' | 'progress' | 'resolved'
  value: number
  change: number
  onClick: () => void
  canvasRef: React.RefObject<HTMLCanvasElement>
}

const MetricCardComponent: FC<MetricCardProps> = ({
  type,
  value,
  change,
  onClick,
  canvasRef,
}) => {
  const sign = change >= 0 ? 'positive' : 'negative'
  const changeText = `${change > 0 ? '+' : ''}${change}%`

  return (
    <div className="metric-card" onClick={onClick} data-type={type}>
      <div className="metric-header">
        <div className={`metric-icon ${type}`}>
          <i className="fas fa-circle" />
        </div>
        <div className={`metric-change ${sign}`}>
          <i className={`fas fa-arrow-${change >= 0 ? 'up' : 'down'}`} />
          <span>{changeText}</span>
        </div>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">
        {type === 'new' && 'Novos Chamados'}
        {type === 'pending' && 'Pendentes'}
        {type === 'progress' && 'Em Progresso'}
        {type === 'resolved' && 'Resolvidos'}
      </div>
      <canvas className="metric-sparkline" ref={canvasRef} />
    </div>
  )
}

export const MetricCard = memo(MetricCardComponent)

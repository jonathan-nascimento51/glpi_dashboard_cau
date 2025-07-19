import { memo, useMemo } from 'react'
import { useChamadosPorDia } from '../hooks/useChamadosPorDia'
import type { ChamadoPorDia } from '../types/chamado'
import ReactCalendarHeatmap from 'react-calendar-heatmap'
import 'react-calendar-heatmap/dist/styles.css'

interface HeatmapValue {
  date?: Date
  count?: number
}

function ChamadosHeatmapComponent() {
  const { dados, isLoading, error } = useChamadosPorDia()
  const values = useMemo(
    () =>
      dados.map((item: ChamadoPorDia) => ({
        date: item.date,
        count: item.total,
      })),
    [dados],
  )

  const { startDate, endDate } = useMemo(() => {
    const end = new Date()
    const start = new Date(end)
    start.setFullYear(start.getFullYear() - 1)
    return { startDate: start, endDate: end }
  }, [])

  if (isLoading) return <div>Carregando heatmap...</div>
  if (error) return <div>Erro ao carregar dados do heatmap</div>

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-2">
        Chamados no Ano (Heatmap Diário)
      </h2>
      <ReactCalendarHeatmap
        startDate={startDate}
        endDate={endDate}
        values={values}
        classForValue={(value: HeatmapValue) => {
          if (!value || !value.count) return 'color-empty'
          if (value.count < 5) return 'color-scale-1'
          if (value.count < 10) return 'color-scale-2'
          if (value.count < 15) return 'color-scale-3'
          return 'color-scale-4'
        }}
        tooltipDataAttrs={(value: HeatmapValue) => ({
          'data-tip': value.date
            ? `${value.date}: ${value.count} chamados`
            : undefined,
        })}
        showWeekdayLabels
      />
    </div>
  )
}

export const ChamadosHeatmap = memo(ChamadosHeatmapComponent)

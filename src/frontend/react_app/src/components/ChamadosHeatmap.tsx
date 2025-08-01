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
  const { data, isLoading, error } = useChamadosPorDia()
  const values = useMemo(
    () =>
      data.map((item: ChamadoPorDia) => ({
        date: item.date,
        count: item.total,
      })),
    [data],
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
    <div className="bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg p-6 flex flex-col gap-4">
      {/* Header alinhado e padronizado */}
      <div className="flex flex-row items-center justify-between px-2 pb-3 border-b border-border/60 min-h-[48px]">
        <div className="levels-title">Chamados no Ano</div>
        <div className="levels-subtitle">Heatmap Diário</div>
      <div/>
    </div>
      <div className="overflow-x-auto pb-2 mb-4 mt-2">
        <ReactCalendarHeatmap
          startDate={startDate}
          endDate={endDate}
          values={values}
          classForValue={(value: HeatmapValue) => {
            if (!(value?.count)) return 'color-empty'
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
      {/* Legenda harmonizada */}
      <div className="flex flex-wrap justify-center items-center gap-x-6 gap-y-2 mt-6 px-2">
        {[
          { color: 'bg-[#f1f5f9]', label: 'Nenhum' },      // color-empty
          { color: 'bg-[#dbeafe]', label: 'Baixo' },       // color-scale-1
          { color: 'bg-[#60a5fa]', label: 'Médio' },       // color-scale-2
          { color: 'bg-[#2563eb]', label: 'Alto' },        // color-scale-3
          { color: 'bg-[#0f172a]', label: 'Muito alto' },  // color-scale-4
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-2">
            <span className={`w-4 h-4 rounded-full border border-border ${color}`} />
            <span className="text-xs font-medium text-muted">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default memo(ChamadosHeatmapComponent)

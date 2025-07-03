import { useChamadosPorDia } from '../hooks/useChamadosPorDia'
import ReactCalendarHeatmap from 'react-calendar-heatmap'
import 'react-calendar-heatmap/dist/styles.css'

export default function ChamadosHeatmap() {
  const { dados, loading, erro } = useChamadosPorDia()

  if (loading) return <div>Carregando heatmap...</div>
  if (erro) return <div>Erro ao carregar dados do heatmap</div>

  const values = dados.map((item) => ({ date: item.date, count: item.total }))

  const endDate = new Date()
  const startDate = new Date(endDate)
  startDate.setFullYear(startDate.getFullYear() - 1)

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-2">Chamados no Ano (Heatmap Diário)</h2>
      <ReactCalendarHeatmap
        startDate={startDate}
        endDate={endDate}
        values={values}
        classForValue={(value) => {
          if (!value || !value.count) return 'color-empty'
          if (value.count < 5) return 'color-scale-1'
          if (value.count < 10) return 'color-scale-2'
          if (value.count < 15) return 'color-scale-3'
          return 'color-scale-4'
        }}
        tooltipDataAttrs={(value) => ({
          'data-tip': value.date ? `${value.date}: ${value.count} chamados` : undefined,
        })}
        showWeekdayLabels
      />
    </div>
  )
}

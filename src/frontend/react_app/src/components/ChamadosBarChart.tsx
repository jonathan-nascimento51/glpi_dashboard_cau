import { memo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts'
import { useChamadosPorData } from '../hooks/useChamadosPorData'
import SkeletonChart from './SkeletonChart'
import { ErrorMessage } from './ErrorMessage'

function ChamadosBarChartComponent() {
  const { data, isLoading, isError, error } = useChamadosPorData()

  if (isLoading) {
    return <SkeletonChart />
  }

  if (isError) {
    return (
      <ErrorMessage
        title="Erro no Gráfico de Barras"
        message={error?.message || 'Não foi possível carregar os dados.'}
      />
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow w-full">
      <h2 className="text-xl font-semibold mb-2">Total de Chamados por Dia</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data ?? []}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={date => new Date(date).toLocaleDateString('pt-BR')}
            tick={{ fontSize: 12 }}
          />
          <YAxis />
          <Tooltip
            formatter={(value: number) => [`${value} chamados`, 'Total']}
            labelFormatter={(label: string) =>
              new Date(label).toLocaleDateString('pt-BR')
            }
          />
          <Legend />
          <Bar dataKey="total" fill="#8884d8" name="Total de Chamados" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export const ChamadosBarChart = memo(ChamadosBarChartComponent)

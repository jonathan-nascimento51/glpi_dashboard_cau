import { memo } from 'react'
import { useChamadosPorData } from '../hooks/useChamadosPorData'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'


function ChamadosTendenciaComponent() {
  // Exibe estado da query e mensagens de carregamento/erro
  const { data, isLoading, isError } = useChamadosPorData()

  if (isLoading) return <p>Carregando chamados...</p>
  if (isError) return <p>Erro ao carregar chamados.</p>

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow w-full">
      {/* Debug information removed. Use React Query Devtools for debugging. */}
      <h2 className="text-xl font-semibold mb-2">Chamados por Dia</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data ?? []} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(date) => new Date(date).toLocaleDateString()}
          />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="total" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default memo(ChamadosTendenciaComponent)

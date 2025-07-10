import { memo } from 'react'
import { useChamadosPorData } from '@/hooks/useChamadosPorData'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'


function ChamadosTendenciaComponent() {
  const { dados, isLoading, error } = useChamadosPorData()

  if (isLoading) return <div>Carregando tendência...</div>
  if (error) return <div>Erro ao carregar dados de tendência</div>

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow w-full">
      <h2 className="text-xl font-semibold mb-2">Chamados por Dia</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={dados} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="total" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export const ChamadosTendencia = memo(ChamadosTendenciaComponent)

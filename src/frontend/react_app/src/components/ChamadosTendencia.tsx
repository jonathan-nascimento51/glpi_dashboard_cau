import { memo } from 'react'
import { useChamadosPorData } from '../hooks/useChamadosPorData'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  Brush,
  ReferenceLine,
} from 'recharts'


function ChamadosTendenciaComponent() {
  const { data, isLoading, isError } = useChamadosPorData()

  if (isLoading) return <p>Carregando chamados...</p>
  if (isError) return <p>Erro ao carregar chamados.</p>

  // Cálculo de média para linha de referência
  const totalSum = (data ?? []).reduce((acc, d) => acc + (d.total ?? 0), 0)
  const totalCount = (data ?? []).length
  const media = totalCount > 0 ? Math.round(totalSum / totalCount) : 0

  return (
    <div className="bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg p-6 flex flex-col gap-4">
      <div className="flex flex-row items-center justify-between px-2 pb-3 border-b border-border/60 min-h-[48px]">
        <div className="levels-title">Chamados por Dia</div>
        <div className="levels-subtitle">Tendência Temporal</div>
      </div>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart
          data={data ?? []}
          margin={{ top: 16, right: 32, left: 8, bottom: 32 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 13, fill: "#cbd5e1", fontWeight: 500 }}
            tickFormatter={(date) => {
              const d = new Date(date)
              return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1)
                .toString()
                .padStart(2, '0')}`
            }}
            minTickGap={16}
            axisLine={{ stroke: "#475569" }}
            tickLine={false}
            height={36}
          />
          <YAxis
            tick={{ fontSize: 13, fill: "#cbd5e1", fontWeight: 500 }}
            axisLine={{ stroke: "#475569" }}
            tickLine={false}
            width={48}
            allowDecimals={false}
            label={{
              value: 'Qtd. Chamados',
              angle: -90,
              position: 'insideLeft',
              fill: "#64748b",
              fontSize: 13,
              fontWeight: 600,
              offset: 10,
            }}
          />
          <Tooltip
            contentStyle={{
              background: "#1e293b",
              border: "1px solid #334155",
              borderRadius: 8,
              color: "#f1f5f9",
              fontSize: 15,
              fontWeight: 500,
            }}
            labelStyle={{
              color: "#38bdf8",
              fontWeight: 700,
              fontSize: 15,
            }}
            labelFormatter={date => {
              const d = new Date(date as string)
              return `Data: ${d.toLocaleDateString()}`
            }}
            formatter={(value: number) => [`${value} chamados`, "Total"]}
          />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: 12, color: "#94a3b8", fontSize: 14, fontWeight: 600 }}
          />
          <ReferenceLine
            y={media}
            stroke="#f59e42"
            strokeDasharray="6 3"
            label={{
              value: `Média: ${media}`,
              position: "right",
              fill: "#f59e42",
              fontSize: 13,
              fontWeight: 600,
              offset: 10,
            }}
            ifOverflow="extendDomain"
          />
          <Line
            type="monotone"
            dataKey="total"
            name="Total de Chamados"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{
              r: 3,
              stroke: "#3b82f6",
              strokeWidth: 2,
              fill: "#fff",
            }}
            activeDot={{
              r: 6,
              fill: "#3b82f6",
              stroke: "#fff",
              strokeWidth: 2,
              style: { filter: "drop-shadow(0 0 4px #3b82f6aa)" },
            }}
            isAnimationActive={true}
          />
          <Brush
            dataKey="date"
            height={28}
            stroke="#3b82f6"
            travellerWidth={10}
            tickFormatter={(date) => {
              const d = new Date(date)
              return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1)
                .toString()
                .padStart(2, '0')}`
            }}
            fill="#1e293b"
            handleStyle={{ fill: "#3b82f6" }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="text-xs text-muted text-center mt-2">
        <span className="font-semibold text-primary">Dica:</span> Selecione um período na barra abaixo para ampliar, ou passe o mouse sobre os pontos para detalhes.
      </div>
    </div>
  )
}

export default memo(ChamadosTendenciaComponent)

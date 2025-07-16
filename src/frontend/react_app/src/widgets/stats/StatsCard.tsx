
interface Props {
  label: string
  value: number
}

export function StatsCard({ label, value }: Props) {
  return (
    <div className="p-4 bg-white rounded shadow text-center">
      <div className="text-2xl font-bold" data-testid="stats-value">
        {value}
      </div>
      <div className="text-gray-500" data-testid="stats-label">
        {label}
      </div>
    </div>
  )
}

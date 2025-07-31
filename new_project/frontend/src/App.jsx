import { useQuery } from '@tanstack/react-query'

function Tickets() {
  const apiBase = process.env.VITE_API_BASE_URL
  const { data, isLoading, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/tickets`)
      if (!res.ok) throw new Error('Failed to load')
      return res.json()
    },
  })

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error loading tickets</p>

  return (
    <ul>
      {data.map((t) => (
        <li key={t.id}>{t.name || t.title || `Ticket ${t.id}`}</li>
      ))}
    </ul>
  )
}

export default function App() {
  return (
    <div>
      <h1>Tickets</h1>
      <Tickets />
    </div>
  )
}

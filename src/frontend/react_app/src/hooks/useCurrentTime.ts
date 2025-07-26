import { useEffect, useState } from 'react'

export function useCurrentTime(): string {
  const [time, setTime] = useState(new Date().toLocaleTimeString('pt-BR', { hour12: false }))

  useEffect(() => {
    const update = () => {
      const now = new Date()
      setTime(now.toLocaleTimeString('pt-BR', { hour12: false }))
    }
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  return time
}

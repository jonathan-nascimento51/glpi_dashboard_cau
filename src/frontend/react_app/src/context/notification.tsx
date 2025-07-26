import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'

export type NotificationType = 'success' | 'warning' | 'error'

export interface Notification {
  id: number
  message: string
  type: NotificationType
}

interface NotificationContextValue {
  notifications: Notification[]
  notify: (message: string, type?: NotificationType) => void
  remove: (id: number) => void
}

const NotificationContext = createContext<NotificationContextValue | undefined>(
  undefined,
)

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const idCounter = useRef(0)
  const timeoutsRef = useRef<Record<number, ReturnType<typeof setTimeout>>>({})
  const removeRef = useRef<(id: number) => void>(() => {})

  const remove = useCallback((id: number) => {
    if (timeoutsRef.current[id]) {
      clearTimeout(timeoutsRef.current[id])
      delete timeoutsRef.current[id]
    }
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  useEffect(() => {
    removeRef.current = remove
  }, [remove])

  useEffect(() => {
    const existing = timeoutsRef.current
    return () => {
      Object.values(existing).forEach(clearTimeout)
    }
  }, [])

  const notify = useCallback((message: string, type: NotificationType = 'success') => {
    const id = ++idCounter.current
    setNotifications((prev) => [...prev, { id, message, type }])
    const timeoutId = setTimeout(() => removeRef.current(id), 4000)
    timeoutsRef.current[id] = timeoutId
    return timeoutId
  }, [])
  return (
    <NotificationContext.Provider value={{ notifications, notify, remove }}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const ctx = useContext(NotificationContext)
  if (!ctx) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }
  return ctx
}

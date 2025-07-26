import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'

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

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined)

let idCounter = 0

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const remove = useCallback((id: number) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const notify = useCallback(
    (message: string, type: NotificationType = 'success') => {
      const id = ++idCounter
      setNotifications((prev) => [...prev, { id, message, type }])
      setTimeout(() => remove(id), 4000)
    },
    [remove],
  )

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

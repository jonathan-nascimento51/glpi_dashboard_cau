import { useNotifications } from '../context/notification'

export default function NotificationToast() {
  const { notifications } = useNotifications()
  return (
    <div className="notification-container">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`notification-toast show ${n.type}`}
          role="alert"
        >
          {n.message}
        </div>
      ))}
    </div>
  )
}

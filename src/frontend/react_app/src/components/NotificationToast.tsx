import { useNotifications } from '../context/notification'

export default function NotificationToast() {
  const { notifications } = useNotifications()
  return (
    <>
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`fixed top-0 right-0 p-4 block ${n.type === 'error' ? 'bg-red-500' : n.type === 'success' ? 'bg-green-500' : 'bg-gray-500'}`}
          role="alert"
        >
          {n.message}
        </div>
      ))}
    </>
  )
}

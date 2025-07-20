interface Props {
  title?: string
  message: string
  onAction?: () => void
  actionText?: string
}

export function EmptyState({
  title = 'Nenhum item encontrado',
  message,
  onAction,
  actionText = 'Tentar novamente',
}: Props) {
  return (
    <div className="text-center p-8">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-gray-500 my-2">{message}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {actionText}
        </button>
      )}
    </div>
  )
}

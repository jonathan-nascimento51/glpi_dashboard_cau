interface Props {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorMessage({ title = 'Erro', message, onRetry }: Props) {
  return (
    <div className="text-center p-4 text-red-700">
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Tentar novamente
        </button>
      )}
    </div>
  )
}

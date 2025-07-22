import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    // Atualiza o estado para que a próxima renderização mostre a UI de fallback.
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Você pode registrar o erro em um serviço de monitoramento aqui
    console.error('Erro não capturado:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      // UI de fallback customizada
      return (
        <div className="flex h-screen flex-col items-center justify-center bg-red-50 p-4 text-red-800">
          <h1 className="mb-4 text-2xl font-bold">Algo deu errado.</h1>
          <p className="mb-4">
            Nossa equipe foi notificada. Por favor, tente recarregar a página.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Recarregar
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

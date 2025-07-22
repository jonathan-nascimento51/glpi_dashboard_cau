import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from '../ErrorBoundary'
import { JSX } from 'react'

// Espiona o console.error para evitar poluir a saída do teste e verificar se foi chamado.
const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

// Um componente simples que sempre lança um erro para simular uma falha.
function ProblematicComponent(): JSX.Element {
  throw new Error('Erro de Teste')
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    consoleErrorSpy.mockClear()
  })

  afterAll(() => {
    consoleErrorSpy.mockRestore()
  })

  it('deve renderizar os componentes filhos quando não há erro', () => {
    render(
      <ErrorBoundary>
        <div>Componente filho</div>
      </ErrorBoundary>,
    )
    expect(screen.getByText('Componente filho')).toBeInTheDocument()
  })

  it('deve capturar um erro e exibir a UI de fallback', () => {
    render(
      <ErrorBoundary>
        <ProblematicComponent />
      </ErrorBoundary>,
    )

    expect(screen.getByText('Algo deu errado.')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /recarregar/i }),
    ).toBeInTheDocument()

    // Verifica se o erro foi logado
    expect(consoleErrorSpy).toHaveBeenCalledTimes(1)
  })

  it('deve tentar recarregar a página ao clicar no botão', () => {
    const { reload } = window.location
    Object.defineProperty(window, 'location', {
      value: { ...window.location, reload: jest.fn() },
      writable: true,
    })

    render(
      <ErrorBoundary>
        <ProblematicComponent />
      </ErrorBoundary>,
    )

    fireEvent.click(screen.getByRole('button', { name: /recarregar/i }))
    expect(window.location.reload).toHaveBeenCalledTimes(1)

    Object.defineProperty(window, 'location', { value: { ...window.location, reload }, writable: true })
  })
})

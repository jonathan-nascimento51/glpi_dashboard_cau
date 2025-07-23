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
    expect(consoleErrorSpy).toHaveBeenCalled()
  })

  it('deve tentar recarregar a página ao clicar no botão', () => {
    const original = window.location
    delete (window as any).location
    Object.defineProperty(window, 'location', {
      value: { ...original, reload: jest.fn() },
      writable: true,
      configurable: true,
    })

    render(
      <ErrorBoundary>
        <ProblematicComponent />
      </ErrorBoundary>,
    )

    fireEvent.click(screen.getByRole('button', { name: /recarregar/i }))
    expect(window.location.reload).toHaveBeenCalledTimes(1)

    delete (window as any).location
    Object.defineProperty(window, 'location', { value: original, writable: true, configurable: true })
  })
})

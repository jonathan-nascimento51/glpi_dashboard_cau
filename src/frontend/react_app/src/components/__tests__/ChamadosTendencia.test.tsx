import { render, screen } from '@testing-library/react'
import { jest } from '@jest/globals'
import { ChamadosTendencia } from '../ChamadosTendencia'
import * as dataHook from '@/hooks/useChamadosPorData'

jest.mock('@/hooks/useChamadosPorData')

const mockedData = dataHook as jest.Mocked<typeof dataHook>

describe('ChamadosTendencia', () => {
  it('formats ISO dates in the X axis', () => {
    mockedData.useChamadosPorData.mockReturnValue({
      data: [{ date: '2024-01-01', total: 3 }],
      isLoading: false,
      isError: false,
      status: 'success',
    } as any)
    render(<ChamadosTendencia />)
    const formatted = new Date('2024-01-01').toLocaleDateString()
    expect(screen.getByText(formatted)).toBeInTheDocument()
  })
})

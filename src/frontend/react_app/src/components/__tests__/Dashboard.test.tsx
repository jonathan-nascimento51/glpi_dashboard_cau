import { render, screen, waitFor } from '@testing-library/react'
import Dashboard from '../Dashboard'
import axios from 'axios'

jest.mock('axios')
const mockedGet = axios.get as jest.Mock

const mockMetrics = {
  N1: { open: 5, closed: 2 },
  N2: { open: 1, closed: 3 },
}

function setup() {
  return render(<Dashboard />)
}

describe('Dashboard component', () => {
  beforeEach(() => {
    mockedGet.mockReset()
    ;(axios as any).CancelToken = {
      source: () => ({ token: 't', cancel: jest.fn() }),
    }
  })

  it('shows loading indicator initially', async () => {
    mockedGet.mockResolvedValue({ data: mockMetrics })
    setup()
    expect(screen.getByRole('status')).toBeInTheDocument()
    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument())
  })

  it('renders metric cards after fetch', async () => {
    mockedGet.mockResolvedValue({ data: mockMetrics })
    setup()
    await waitFor(() => screen.getByTestId('card-N1'))
    expect(screen.getByText('Abertos: 5')).toBeInTheDocument()
    expect(screen.getByText('Fechados: 2')).toBeInTheDocument()
  })

  it('shows error message on failure', async () => {
    mockedGet.mockRejectedValue(new Error('fail'))
    setup()
    await waitFor(() => screen.getByText(/Não foi possível carregar/))
    expect(screen.getByRole('button', { name: /tentar novamente/i })).toBeInTheDocument()
  })
})

import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from '../src/App.jsx'

const queryClient = new QueryClient()

global.fetch = jest.fn(() =>
  Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: 1, name: 'Test' }]) })
)

process.env.VITE_API_BASE_URL = 'http://localhost:8000'

test('renders tickets from API', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  )

  await waitFor(() => {
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})

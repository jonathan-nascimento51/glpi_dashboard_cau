import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { GlpiTicketsTable } from '@/components/GlpiTicketsTable'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>
)

beforeEach(() => {
  const mockImportMetaEnv: ImportMetaEnv = { NEXT_PUBLIC_API_BASE_URL: 'http://localhost' };
  Object.defineProperty(import.meta, 'env', { value: mockImportMetaEnv, writable: true });
})

test('renders ticket rows with null fields', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    headers: { get: () => 'application/json' },
    text: () =>
      Promise.resolve(
        JSON.stringify([
          { id: 1, name: 'Teste', status: 'new', priority: null, date_creation: null },
        ])
      ),
  }) as jest.Mock

  render(<GlpiTicketsTable />, { wrapper })
  await waitFor(() => expect(screen.getByText('Teste')).toBeInTheDocument())
  expect(screen.getAllByText('-')).toHaveLength(2)
})

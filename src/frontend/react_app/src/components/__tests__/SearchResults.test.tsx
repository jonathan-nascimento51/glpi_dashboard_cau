import { render, screen } from '@testing-library/react'
import SearchResults from '../SearchResults'
import * as useSearchHook from '../../hooks/useSearch'

jest.mock('../../hooks/useSearch')

const mockUseSearch = useSearchHook as jest.Mocked<typeof useSearchHook>

test('renders results', () => {
  mockUseSearch.useSearch.mockReturnValue({
    data: [{ id: 1, name: 'T1' }],
    isLoading: false,
    isError: false,
  } as any)

  render(<SearchResults term="t" visible={true} />)
  expect(screen.getByText('T1')).toBeInTheDocument()
})

import { render, screen } from '@testing-library/react'
import SearchResults from '../SearchResults'
import * as useSearchHook from '../../hooks/useSearch'
import type { UseQueryResult } from '@tanstack/react-query'

jest.mock('../../hooks/useSearch')

const mockUseSearch = useSearchHook as jest.Mocked<typeof useSearchHook>

test('renders results', () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: [{ id: 1, name: 'T1', requester: undefined }],
    isLoading: false,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="t" visible={true} />)
  expect(screen.getByText('T1')).toBeInTheDocument()
})

test('shows loading spinner', () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: undefined,
    isLoading: true,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="t" visible={true} />)
  expect(screen.getByRole('status')).toBeInTheDocument()
})

test('renders nothing when visible is false', () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: [{ id: 1, name: 'T1', requester: undefined }],
    isLoading: false,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  const { container } = render(<SearchResults term="t" visible={false} />)
  expect(container).toBeEmptyDOMElement()
})

test('shows error message', () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: undefined,
    isLoading: false,
    isError: true,
    error: new Error('oops'),
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="t" visible={true} />)
  expect(
    screen.getByText(
      'Erro ao buscar chamados. Tente novamente ou verifique sua conexão.',
    ),
  ).toBeInTheDocument()
})

test('shows no results message', () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: [],
    isLoading: false,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="t" visible={true} />)
  expect(screen.getByText('Nenhum resultado encontrado')).toBeInTheDocument()
})

test("does not show 'Nenhum resultado encontrado' when search term is empty", () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: [],
    isLoading: false,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="" visible={true} />)
  expect(screen.queryByText('Nenhum resultado encontrado')).not.toBeInTheDocument()
})

test("does not show 'Nenhum resultado encontrado' when search term is whitespace only", () => {
  const result: Partial<UseQueryResult<useSearchHook.SearchResult[], Error>> = {
    data: [],
    isLoading: false,
    isError: false,
  }
  mockUseSearch.useSearch.mockReturnValue(
    result as UseQueryResult<useSearchHook.SearchResult[], Error>,
  )

  render(<SearchResults term="   " visible={true} />)
  expect(screen.queryByText('Nenhum resultado encontrado')).not.toBeInTheDocument()
})

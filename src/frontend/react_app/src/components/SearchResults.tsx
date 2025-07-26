import type { FC } from 'react'
import { useSearch } from '../hooks/useSearch'
import { useDebounce } from '../hooks/useDebounce'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'

interface Props {
  term: string
  visible: boolean
}

const SearchResults: FC<Props> = ({ term, visible }) => {
  const debouncedTerm = useDebounce(term, 300)
  const { data, isLoading, isError } = useSearch(debouncedTerm)

  if (!visible) return null

  if (isLoading) {
    return (
      <div className="search-results show">
        <LoadingSpinner />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="search-results show">
        <ErrorMessage message="Erro ao buscar chamados. Tente novamente ou verifique sua conexão." />
      </div>
    )
  }

  if (!data || data.length === 0) {
    if (debouncedTerm.trim().length > 0) {
      return (
        <div className="search-results show">
          <div className="search-result-item">Nenhum resultado encontrado</div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="search-results show">
      {data.map((item) => (
        <div key={item.id} className="search-result-item">
          {item.name}
          {item.requester ? ` - ${item.requester}` : ''}
        </div>
      ))}
    </div>
  )
}

export default SearchResults

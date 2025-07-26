import type { FC } from 'react'
import { useSearch } from '../hooks/useSearch'
import { LoadingSpinner } from './LoadingSpinner'
import { ErrorMessage } from './ErrorMessage'

interface Props {
  term: string
  visible: boolean
}

const SearchResults: FC<Props> = ({ term, visible }) => {
  const { data, isLoading, isError } = useSearch(term)

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

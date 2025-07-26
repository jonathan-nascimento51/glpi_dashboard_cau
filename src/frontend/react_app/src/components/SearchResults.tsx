import type { FC } from 'react'
import { useState, useEffect, useRef } from 'react'
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
  const [activeIndex, setActiveIndex] = useState(0)
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setActiveIndex(0)
  }, [data])

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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!data) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex((i) => (i + 1) % data.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex((i) => (i - 1 + data.length) % data.length)
    }
  }

  return (
    <div
      className="search-results show"
      role="listbox"
      tabIndex={0}
      aria-activedescendant={data ? `result-${data[activeIndex].id}` : undefined}
      onKeyDown={handleKeyDown}
      ref={listRef}
    >
      {data.map((item, idx) => (
        <div
          key={item.id}
          id={`result-${item.id}`}
          role="option"
          aria-selected={activeIndex === idx}
          className={`search-result-item ${activeIndex === idx ? 'active' : ''}`}
        >
          {item.name}
          {item.requester ? ` - ${item.requester}` : ''}
        </div>
      ))}
    </div>
  )
}

export default SearchResults

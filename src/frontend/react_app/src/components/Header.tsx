import { type FC, useCallback, useState } from 'react'
import ThemeSwitcher from './ThemeSwitcher'
import { useFilters } from '../hooks/useFilters'
import { useVoiceCommands } from '../hooks/useVoiceCommands'
import { useCurrentTime } from '../hooks/useCurrentTime'
import VoiceIndicator from './VoiceIndicator'
import SearchResults from './SearchResults'

// The delay value for the blur handler ensures smooth UI transitions and prevents
// accidental dismissal of search results when interacting with related elements.
const SEARCH_BLUR_DELAY = 100

const Header: FC = () => {
  const { filters, toggleFilters } = useFilters()
  const { isListening, startListening, stopListening } = useVoiceCommands()
  const time = useCurrentTime()
  const toggleVoice = useCallback(
    () => (isListening ? stopListening() : startListening()),
    [isListening, startListening, stopListening],
  )

  const [term, setTerm] = useState('')
  const [showResults, setShowResults] = useState(false)

  const handleFocus = () => setShowResults(true)
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.relatedTarget?.closest('.search-container')) {
      return
    }
    setTimeout(() => setShowResults(false), SEARCH_BLUR_DELAY)
  }


  return (
    <header className="header">
      <div className="brand">
        <div className="brand-logo">
          <i className="fas fa-microchip" />
        </div>
        <div className="brand-info">
          <h1>Centro de Comando</h1>
          <p>Departamento de Tecnologia</p>
        </div>
      </div>
      <div className="header-controls">
        <ThemeSwitcher />
        <div className="search-container">
          <i className="fas fa-search search-icon" />
          <input
            id="searchInput"
            name="search"
            type="text"
            className="search-input"
            placeholder="Buscar chamados, técnicos..."
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
          />
          <SearchResults term={term} visible={showResults} />
        </div>
        <div className="status-live">
          <div className="live-indicator" />
          <span>SISTEMA ATIVO</span>
        </div>
        <button className="refresh-btn">
          <i className="fas fa-sync-alt" />
          <span>Atualizar</span>
        </button>
        <button
          className="refresh-btn"
          onClick={toggleFilters}
          aria-controls="filterPanel"
          aria-expanded={filters.open}
        >
          <i className="fas fa-filter" />
          <span>Filtros</span>
        </button>
        <button className="refresh-btn" onClick={toggleVoice}>
          <i className="fas fa-microphone" />
          <span>{isListening ? 'Parar' : 'Falar'}</span>
        </button>
        <span aria-live="polite" aria-label="Current time">{time}</span>
      </div>
      <VoiceIndicator isListening={isListening} />
    </header>
  )
}

export default Header

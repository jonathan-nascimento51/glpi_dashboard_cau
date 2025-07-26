import { type FC, useCallback, useState } from 'react'
import { useThemeSwitcher } from '../hooks/useThemeSwitcher'
import { useFilters } from '../hooks/useFilters'
import { useVoiceCommands } from '../hooks/useVoiceCommands'
import VoiceIndicator from './VoiceIndicator'
import SearchResults from './SearchResults'

// The delay value for the blur handler ensures smooth UI transitions and prevents
// accidental dismissal of search results when interacting with related elements.
const SEARCH_BLUR_DELAY = 100

const Header: FC = () => {
  const { theme, setTheme } = useThemeSwitcher()
  const { toggleFilters } = useFilters()
  const { isListening, startListening, stopListening } = useVoiceCommands()
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

  const setLight = useCallback(() => setTheme('light'), [setTheme])
  const setDark = useCallback(() => setTheme('dark'), [setTheme])
  const setCorporate = useCallback(() => setTheme('corporate'), [setTheme])
  const setTech = useCallback(() => setTheme('tech'), [setTheme])

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
        <div className="theme-switcher">
          <button
            className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
            onClick={setLight}
          >
            Light
          </button>
          <button
            className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
            onClick={setDark}
          >
            Dark
          </button>
          <button
            className={`theme-btn ${theme === 'corporate' ? 'active' : ''}`}
            onClick={setCorporate}
          >
            Corp
          </button>
          <button
            className={`theme-btn ${theme === 'tech' ? 'active' : ''}`}
            onClick={setTech}
          >
            Tech
          </button>
        </div>
        <div className="search-container">
          <i className="fas fa-search search-icon" />
          <input
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
        <button className="refresh-btn" onClick={toggleFilters}>
          <i className="fas fa-filter" />
          <span>Filtros</span>
        </button>
        <button className="refresh-btn" onClick={toggleVoice}>
          <i className="fas fa-microphone" />
          <span>{isListening ? 'Parar' : 'Falar'}</span>
        </button>
        <div className="current-time" id="currentTime" />
      </div>
      <VoiceIndicator isListening={isListening} />
    </header>
  )
}

export default Header

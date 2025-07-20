import React from 'react'
import { type FC, useCallback } from 'react'
import { useThemeSwitcher } from '../hooks/useThemeSwitcher'
import { useFilters } from '../hooks/useFilters'

const Header: FC = () => {
  const { theme, setTheme } = useThemeSwitcher()
  const { toggleFilters } = useFilters()

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
          />
          <div className="search-results" id="searchResults" />
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
        <div className="current-time" id="currentTime" />
      </div>
    </header>
  )
}

export default Header

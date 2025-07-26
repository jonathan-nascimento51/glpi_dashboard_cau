import { type FC, useCallback, useEffect, useRef } from 'react'
import { useFilters } from '../hooks/useFilters'

const FilterPanel: FC = () => {
  const { filters, toggleFilters, toggleValue } = useFilters()

  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!filters.open || !panelRef.current) return

    const focusable = panelRef.current.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    )
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    first?.focus()

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (focusable.length === 0) return
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault()
            last.focus()
          }
        } else if (document.activeElement === last) {
          e.preventDefault()
          first.focus()
        }
      } else if (e.key === 'Escape') {
        toggleFilters()
      }
    }

    panelRef.current.addEventListener('keydown', handleKeyDown)
    return () => {
      panelRef.current?.removeEventListener('keydown', handleKeyDown)
    }
  }, [filters.open, toggleFilters])

  const renderOptions = useCallback(
    (category: keyof Omit<typeof filters, 'open'>) => {
      const values = filters[category] as string[]
      return values.map((value) => (
        <div
          key={value}
          className="filter-option"
          onClick={() => toggleValue(category, value)}
        >
          <div
            className={`filter-checkbox ${values.includes(value) ? 'checked' : ''}`}
          >
            <i className="fas fa-check" />
          </div>
          <div className="filter-label">{value}</div>
        </div>
      ))
    },
    [filters, toggleValue],
  )

  return (
    <div
      className={`filter-panel ${filters.open ? 'open' : ''}`}
      id="filterPanel"
      role="dialog"
      aria-modal="true"
      ref={panelRef}
    >
      <div className="filter-header">
        <div className="filter-title">Filtros Avançados</div>
        <button className="filter-close" onClick={toggleFilters} title='Fechar filtros'>
          <i className="fas fa-times" />
        </button>
      </div>
      <div className="filter-group">
        <div className="filter-group-title">Período</div>
        <div className="filter-options">{renderOptions('period')}</div>
      </div>
      <div className="filter-group">
        <div className="filter-group-title">Níveis</div>
        <div className="filter-options">{renderOptions('level')}</div>
      </div>
      <div className="filter-group">
        <div className="filter-group-title">Status</div>
        <div className="filter-options">{renderOptions('status')}</div>
      </div>
      <div className="filter-group">
        <div className="filter-group-title">Prioridade</div>
        <div className="filter-options">{renderOptions('priority')}</div>
      </div>
    </div>
  )
}

export default FilterPanel

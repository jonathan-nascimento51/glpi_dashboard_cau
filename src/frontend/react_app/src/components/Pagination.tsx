import React from 'react'

interface Props {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

export function Pagination({ currentPage, totalPages, onPageChange, className = '' }: Props) {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)
  const goto = (page: number) => () => {
    if (page < 1 || page > totalPages || page === currentPage) return
    onPageChange(page)
  }
  return (
    <nav aria-label="Paginação" className={className}>
      <ul className="flex items-center gap-2">
        <li>
          <button
            onClick={goto(currentPage - 1)}
            disabled={currentPage === 1}
            aria-label="Página anterior"
            className="rounded border px-2 py-1 disabled:opacity-50"
          >
            Anterior
          </button>
        </li>
        {pages.map(page => (
          <li key={page}>
            <button
              onClick={goto(page)}
              aria-current={page === currentPage ? 'page' : undefined}
              className={`rounded border px-3 py-1 ${
                page === currentPage ? 'bg-blue-600 text-white' : 'bg-white text-blue-600'
              }`}
            >
              {page}
            </button>
          </li>
        ))}
        <li>
          <button
            onClick={goto(currentPage + 1)}
            disabled={currentPage === totalPages}
            aria-label="Próxima página"
            className="rounded border px-2 py-1 disabled:opacity-50"
          >
            Próxima
          </button>
        </li>
      </ul>
    </nav>
  )
}

export default Pagination

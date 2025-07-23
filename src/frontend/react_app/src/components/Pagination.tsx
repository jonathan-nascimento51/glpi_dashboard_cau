import React from 'react'

interface Props {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

export function Pagination({ currentPage, totalPages, onPageChange, className = '' }: Props) {
  const getTruncatedPages = (currentPage: number, totalPages: number) => {
    const delta = 2; // Number of pages to show around the current page
    const range = [];
    const left = Math.max(1, currentPage - delta);
    const right = Math.min(totalPages, currentPage + delta);

    for (let i = left; i <= right; i++) {
      range.push(i);
    }

    if (left > 2) {
      range.unshift('...');
      range.unshift(1);
    } else if (left === 2) {
      range.unshift(1);
    }

    if (right < totalPages - 1) {
      range.push('...');
      range.push(totalPages);
    } else if (right === totalPages - 1) {
      range.push(totalPages);
    }

    return range;
  };

  const pages = getTruncatedPages(currentPage, totalPages);
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

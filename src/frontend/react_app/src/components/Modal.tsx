import { type FC, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
}

const FOCUS_SELECTOR =
  'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([-1]), [contenteditable=true]'

function useFocusTrap(ref: React.RefObject<HTMLDivElement>, isActive: boolean, onClose: () => void) {
  useEffect(() => {
    if (!isActive || !ref.current) return
    const root = ref.current
    const focusable = Array.from(root.querySelectorAll<HTMLElement>(FOCUS_SELECTOR))
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const previouslyFocused = document.activeElement as HTMLElement | null
    first?.focus()
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (focusable.length === 0) {
          e.preventDefault()
          return
        }
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault()
            last?.focus()
          }
        } else if (document.activeElement === last) {
          e.preventDefault()
          first?.focus()
        }
      } else if (e.key === 'Escape') {
        onClose()
      }
    }
    root.addEventListener('keydown', handleKeyDown)
    return () => {
      root.removeEventListener('keydown', handleKeyDown)
      previouslyFocused?.focus()
    }
  }, [isActive, ref, onClose])
}

export const Modal: FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  useFocusTrap(containerRef, isOpen, onClose)

  useEffect(() => {
    if (!isOpen) return
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div role="dialog" aria-modal="true" ref={containerRef} className="modal">
        {children}
        <button className="absolute top-2 right-2" onClick={onClose} aria-label="Fechar">
          &times;
        </button>
      </div>
    </div>,
    document.body,
  )
}

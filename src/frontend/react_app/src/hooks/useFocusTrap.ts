import { useEffect } from 'react'

const FOCUS_SELECTOR =
  'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([-1]), [contenteditable=true]'

export function useFocusTrap(
  ref: React.RefObject<HTMLElement>,
  active: boolean,
  onClose: () => void,
) {
  useEffect(() => {
    if (!active || !ref.current) return
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
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      previouslyFocused?.focus()
    }
  }, [active, ref, onClose])
}

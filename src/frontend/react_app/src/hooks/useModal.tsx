import { useState, useCallback, useMemo } from 'react'
import { Modal } from '../components/Modal'

export function useModal() {
  const [content, setContent] = useState<React.ReactNode | null>(null)
  const openModal = useCallback((node: React.ReactNode) => setContent(node), [])
  const closeModal = useCallback(() => setContent(null), [])
  const modalElement = useMemo(
    () => (
      <Modal isOpen={content !== null} onClose={closeModal}>
        {content}
      </Modal>
    ),
    [content, closeModal],
  )
  return { openModal, closeModal, modalElement }
}

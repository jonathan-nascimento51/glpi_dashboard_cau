import { useState } from 'react'
import { Modal } from '../components/Modal'

export function useModal() {
  const [content, setContent] = useState<React.ReactNode | null>(null)
  const openModal = (node: React.ReactNode) => setContent(node)
  const closeModal = () => setContent(null)
  const modalElement = (
    <Modal isOpen={content !== null} onClose={closeModal}>
      {content}
    </Modal>
  )
  return { openModal, closeModal, modalElement }
}

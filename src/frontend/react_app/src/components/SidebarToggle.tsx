import { type FC } from 'react'
import { useSidebar } from '../hooks/useSidebar'

const SidebarToggle: FC = () => {
  const { toggle } = useSidebar()
  return (
    <button className="sidebar-toggle" onClick={toggle} aria-label="Toggle sidebar">
      <i className="fas fa-bars" />
    </button>
  )
}

export default SidebarToggle

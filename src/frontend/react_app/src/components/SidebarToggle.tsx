import { type FC } from 'react'
import { useSidebar } from '../hooks/useSidebar'

const SidebarToggle: FC = () => {
  const { toggle } = useSidebar()
  return (
    <button
      className="sidebar-toggle"
      onClick={toggle}
      aria-label="Toggle sidebar"
      type="button"
      id="sidebar-toggle"
      name="sidebar-toggle"
    >
      <i className="fas fa-bars" aria-hidden="true"></i>
    </button>
  )
}

export default SidebarToggle

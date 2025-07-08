import React from 'react'
import { ChamadosTendencia } from './components/ChamadosTendencia'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">GLPI Dashboard</h1>
      <ChamadosTendencia />
    </div>
  )
}

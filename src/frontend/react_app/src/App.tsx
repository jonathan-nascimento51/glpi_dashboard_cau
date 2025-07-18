import React from 'react';
import Header from './components/Header';
import { ChamadosTendencia } from './components/ChamadosTendencia';

export default function App() {
  return (
    <div className="dashboard-container">
      <Header />
      <main className="p-4">
        <h1 className="text-2xl font-bold mb-4">GLPI Dashboard</h1>
        <ChamadosTendencia />
      </main>
    </div>
  )
}

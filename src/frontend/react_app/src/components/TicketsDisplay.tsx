import { GlpiTicketsTable } from './GlpiTicketsTable'

function TicketsDisplay() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard de Chamados GLPI</h1>
      {/* O componente GlpiTicketsTable agora gerencia seu próprio estado
          de carregamento, erro, dados e exibição, incluindo a ordenação
          e a barra de rolagem. */}
      <GlpiTicketsTable />
    </div>
  )
}

export default TicketsDisplay

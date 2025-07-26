import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { DrawerTrigger } from '@/components/ui/drawer'

export function Header() {
  return (
    <header className="flex items-center justify-between border-b bg-background p-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-primary px-2 py-1 text-white">GLPI</span>
        <h1 className="text-lg font-bold">Dashboard</h1>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative">
          <Input placeholder="Buscar..." className="pl-8" />
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground">
            <i className="fas fa-search" />
          </span>
        </div>
        <Button variant="outline">Atualizar</Button>
        <DrawerTrigger asChild>
          <Button variant="outline">
            <i className="fas fa-filter mr-2" />Filtros
          </Button>
        </DrawerTrigger>
      </div>
    </header>
  )
}

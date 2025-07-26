import { Drawer, DrawerContent, DrawerClose } from '@/components/ui/drawer'
import { Button } from '@/components/ui/button'

export function FilterDrawer() {
  return (
    <Drawer>
      <DrawerContent className="space-y-4">
        <div className="flex items-center justify-between border-b pb-2">
          <h2 className="text-lg font-semibold">Filtros</h2>
          <DrawerClose asChild>
            <Button variant="ghost" aria-label="Fechar">
              <i className="fas fa-times" />
            </Button>
          </DrawerClose>
        </div>
        {/* filtro placeholder */}
        <div className="space-y-2">
          <label className="block text-sm font-medium">Status</label>
          <div className="flex gap-2">
            <Button variant="outline">Aberto</Button>
            <Button variant="outline">Fechado</Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

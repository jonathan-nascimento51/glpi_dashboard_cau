import { Drawer, DrawerContent, DrawerClose, DrawerTitle } from '@/components/ui/drawer'
import { Button, ButtonProps } from '@/components/ui/button'

export function FilterDrawer() {
  return (
    <Drawer>
      <DrawerContent className="space-y-4">
        <div className="flex items-center justify-between border-b pb-2">
          <DrawerTitle className="text-lg font-semibold">Filtros</DrawerTitle>
          <DrawerClose asChild>
            <Button className="btn-ghost" aria-label="Fechar">
              <i className="fas fa-times" />
            </Button>
          </DrawerClose>
        </div>
        {/* filtro placeholder */}
        <div className="space-y-2">
          <label className="block text-sm font-medium">Status</label>
          <div className="flex gap-2">
            <Button className="btn-outline">Aberto</Button>
            <Button className="btn-outline">Fechado</Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export interface ExtendedButtonProps extends ButtonProps {
  // Adicione aqui as props adicionais que você precisa
}

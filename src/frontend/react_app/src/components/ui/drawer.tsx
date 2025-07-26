import * as DialogPrimitive from '@radix-ui/react-dialog'
import { cn } from '@/lib/cn'

export const Drawer = DialogPrimitive.Root
export const DrawerTrigger = DialogPrimitive.Trigger
export const DrawerClose = DialogPrimitive.Close
export const DrawerTitle = DialogPrimitive.Title

export function DrawerContent({ className, ...props }: DialogPrimitive.DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 bg-black/50" />
      <DialogPrimitive.Content
        {...props}
        className={cn(
          'fixed right-0 top-0 h-full w-80 bg-background p-6 shadow-lg outline-none',
          className,
        )}
      />
    </DialogPrimitive.Portal>
  )
}

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(' ')
}

export function theme(token: string): string {
  return `var(--${token})`
}

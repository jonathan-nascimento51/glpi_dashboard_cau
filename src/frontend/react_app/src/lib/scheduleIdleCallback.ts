/**
 * IdleHandle is a union of possible handle types returned by requestIdleCallback and setTimeout.
 * In most browsers, both return a number, but in some environments (like Node.js), setTimeout returns a Timeout object.
 * This union ensures type safety across environments.
 */
export type IdleHandle = number | ReturnType<typeof setTimeout>

export function scheduleIdleCallback(cb: () => void): IdleHandle {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    return (window as any).requestIdleCallback(() => cb())
  }
  if (typeof window !== 'undefined') {
    return (window as Window & typeof globalThis).setTimeout(cb, 0)
  }
  return (globalThis as typeof globalThis).setTimeout(cb, 0)
}

export function cancelIdleCallback(handle: IdleHandle) {
  if (typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
    (window as { cancelIdleCallback: (handle: IdleHandle) => void }).cancelIdleCallback(handle)
  } else {
    clearTimeout(handle)
  }
}

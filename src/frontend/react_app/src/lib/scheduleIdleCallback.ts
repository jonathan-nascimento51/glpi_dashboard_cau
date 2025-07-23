export type IdleHandle = number

export function scheduleIdleCallback(cb: () => void): IdleHandle {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    return (window as unknown as { requestIdleCallback: (fn: IdleRequestCallback) => IdleHandle }).requestIdleCallback(() => cb())
  }
  if (typeof window !== 'undefined') {
    return window.setTimeout(cb, 0)
  }
  return setTimeout(cb, 0)
}

export function cancelIdleCallback(handle: IdleHandle) {
  if (typeof window !== 'undefined' && 'cancelIdleCallback' in window) {
    (window as { cancelIdleCallback: (handle: IdleHandle) => void }).cancelIdleCallback(handle)
  } else {
    clearTimeout(handle)
  }
}

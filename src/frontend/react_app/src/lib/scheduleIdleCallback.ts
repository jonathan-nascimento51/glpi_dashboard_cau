/**
 * IdleHandle is a union of possible handle types returned by requestIdleCallback and setTimeout.
 * In most browsers, both return a number, but in some environments (like Node.js), setTimeout returns a Timeout object.
 * This union ensures type safety across environments.
 */
export type IdleHandle = number | ReturnType<typeof setTimeout>

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

'use client'
import React, { useEffect, PropsWithChildren, unstable_Profiler as Profiler } from 'react'

export function ProfilerProvider({ children }: PropsWithChildren) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      import('@welldone-software/why-did-you-render').then((mod) => {
        mod.default(React, { trackAllPureComponents: true })
      }).catch(() => {})
    }
  }, [])

  const onRender = (
    id: string,
    phase: 'mount' | 'update',
    actualDuration: number
  ) => {
    console.table([{ id, phase, actualDuration }])
  }

  return <Profiler id="App" onRender={onRender}>{children}</Profiler>
}

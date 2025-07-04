'use client'
import { ReactNode } from 'react'
import { SWRConfig } from 'swr'
import { captureException } from '@sentry/nextjs'
import { fetcher } from '@/lib/swrClient'

export function SWRProvider({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher,
        dedupingInterval: 10000,
        refreshInterval: 30000,
        revalidateOnFocus: true,
        onError: (err) => captureException(err),
      }}
    >
      {children}
    </SWRConfig>
  )
}

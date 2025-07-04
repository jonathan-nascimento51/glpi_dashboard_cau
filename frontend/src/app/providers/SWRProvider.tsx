'use client'
import { ReactNode } from 'react'
import { SWRConfig } from 'swr'
import { fetcher } from '@/lib/swrClient'

export function SWRProvider({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher,
        dedupingInterval: 10000,
        refreshInterval: 30000,
        revalidateOnFocus: true,
        onError: (err: any) => {
          if (process.env.NODE_ENV === 'development') {
            console.error(err)
          }
        },
      }}
    >
      {children}
    </SWRConfig>
  )
}
import type { AppProps } from 'next/app'
import React from 'react'
export { reportWebVitals } from '@/reportWebVitals'

export default function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}

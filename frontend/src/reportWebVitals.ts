import type { ReportHandler } from 'web-vitals'
import { captureMessage } from '@sentry/nextjs'

export const reportWebVitals: ReportHandler = (metric) => {
  const { id, name, value, label } = metric
  if (label === 'web-vital' && ['CLS', 'LCP', 'FCP', 'INP'].includes(name)) {
    if (process.env.NODE_ENV === 'production') {
      captureMessage(`web-vital:${name}`, {
        level: 'info',
        tags: { id },
        extra: { value },
      })
    } else {
      console.log(metric)
    }
  }
}

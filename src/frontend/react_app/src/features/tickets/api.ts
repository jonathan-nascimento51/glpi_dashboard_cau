import { useApiQuery } from '../../hooks/useApiQuery'
import type { MetricsOverview } from '../../types/metricsOverview'

export function useTicketMetrics() {
  return useApiQuery<MetricsOverview>(
    ['ticket-metrics'],
    '/v1/metrics/aggregated',
    {
      transformResponse: (data: unknown): MetricsOverview => {
        if (
          typeof data === 'object' &&
          data !== null &&
          'metric1' in data &&
          'metric2' in data
        ) {
          return data as MetricsOverview;
        } else {
          throw new Error('Invalid response structure for MetricsOverview');
        }
      }
    }
  );
}

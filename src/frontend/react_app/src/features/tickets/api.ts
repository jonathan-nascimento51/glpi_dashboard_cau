import { useApiQuery } from '../../hooks/useApiQuery'
import type { MetricsOverview } from '../../types/metricsOverview'

export function useTicketMetrics() {
  return useApiQuery<MetricsOverview>(
    ['ticket-metrics'],
    '/v1/metrics/aggregated',
    {
      select: (data: any): MetricsOverview => {
        if (
          data &&
          typeof data === 'object' &&
          'status' in data &&
          typeof data.status === 'object' &&
          data.status !== null &&
          Object.values(data.status).every((v) => typeof v === 'number') &&
          'per_user' in data &&
          typeof data.per_user === 'object' &&
          data.per_user !== null &&
          Object.values(data.per_user).every((v) => typeof v === 'number')
        ) {
          return data as MetricsOverview;
        }
        throw new Error('Invalid response structure for MetricsOverview');
      },
    }
  );
}

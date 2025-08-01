import { useApiQuery } from '../../hooks/useApiQuery'
import type { TicketMetrics } from '../../types/dashboard'

export function useTicketMetrics() {
  return useApiQuery<TicketMetrics>(
    ['ticket-metrics'], 
    '/v1/metrics/summary',
    {
      transformResponse: (data: unknown): TicketMetrics => {
        // Validate and transform the response to ensure it matches TicketMetrics
        if (typeof data === 'object' && data !== null && 'metric1' in data && 'metric2' in data) {
          return data as TicketMetrics;
        } else {
          throw new Error('Invalid response structure for TicketMetrics');
        }
      }
    }
  );
}

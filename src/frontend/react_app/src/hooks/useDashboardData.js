'use client';
import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from '@/hooks/useApiQuery';
export function useDashboardData() {
    const queryClient = useQueryClient();
    const query = useApiQuery(['metrics-aggregated'], '/metrics/aggregated');
    const metrics = {
        new: query.data?.status?.new ?? 0,
        pending: query.data?.status?.pending ?? 0,
        progress: query.data?.status?.progress ?? 0,
        resolved: query.data?.status?.resolved ?? 0,
    };
    const trendChart = useRef(null);
    const sparkRefs = {
        new: useRef(null),
        pending: useRef(null),
        progress: useRef(null),
        resolved: useRef(null),
    };
    useEffect(() => {
        let chartModule = null;
        const loadChart = async () => {
            chartModule = await import('chart.js/auto');
            const ctx = document.getElementById('trendsChart');
            if (!ctx) {
                return;
            }
            trendChart.current = new chartModule.Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array.from({ length: 12 }, (_, i) => `${i}`),
                    datasets: [
                        {
                            label: 'Novos',
                            data: [],
                            borderColor: '#1e40af',
                            backgroundColor: 'rgba(30,64,175,0.1)',
                            fill: true,
                        },
                        {
                            label: 'Resolvidos',
                            data: [],
                            borderColor: '#059669',
                            backgroundColor: 'rgba(5,150,105,0.1)',
                            fill: true,
                        },
                    ],
                },
                options: { responsive: true, maintainAspectRatio: false },
            });
        };
        loadChart();
        return () => trendChart.current?.destroy();
    }, []);
    useEffect(() => {
        const id = setInterval(() => {
            queryClient
                .invalidateQueries({ queryKey: ['metrics-aggregated'] })
                .catch(() => undefined);
        }, 30000);
        return () => clearInterval(id);
    }, [queryClient]);
    const refreshMetrics = () => queryClient.invalidateQueries({ queryKey: ['metrics-aggregated'] });
    return {
        metrics,
        sparkRefs,
        refreshMetrics,
        isLoading: query.isLoading,
        error: query.error,
    };
}

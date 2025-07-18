import { captureMessage } from '@sentry/react';
export const reportWebVitals = (metric) => {
    const { id, name, value, label } = metric;
    if (label === 'web-vital' && ['CLS', 'LCP', 'FCP', 'INP'].includes(name)) {
        if (process.env.NODE_ENV === 'production') {
            captureMessage(`web-vital:${name}`, {
                level: 'info',
                tags: { id },
                extra: { value },
            });
        }
        else {
            console.log(metric);
        }
    }
};

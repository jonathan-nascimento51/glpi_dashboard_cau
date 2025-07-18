export async function fetcher(url, init = {}) {
    const base = import.meta.env.NEXT_PUBLIC_API_BASE_URL;
    if (!base) {
        console.error('Environment variable NEXT_PUBLIC_API_BASE_URL is not set');
        throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable not configured');
    }
    let res;
    try {
        res = await fetch(`${base ?? ''}${url}`, {
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                ...(init.headers ?? {}),
            },
            ...init,
        });
    }
    catch (err) {
        const error = new Error('Network error');
        error.cause = err;
        throw error;
    }
    if (res.status >= 400) {
        const message = await res.text();
        const error = new Error(message || res.statusText);
        error.status = res.status;
        error.statusText = res.statusText;
        throw error;
    }
    const contentType = res.headers.get('content-type') ?? '';
    const body = await res.text();
    if (contentType.includes('application/json')) {
        try {
            return JSON.parse(body);
        }
        catch {
            return body;
        }
    }
    return body;
}

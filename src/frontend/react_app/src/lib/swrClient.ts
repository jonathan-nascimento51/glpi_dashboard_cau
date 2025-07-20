export async function fetcher<T>(
  path: string,
  init: RequestInit = {},
  opts: { timeoutMs?: number; baseUrl?: string } = {}
): Promise<T> {
  const base = opts.baseUrl ?? import.meta.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(new DOMException('Timeout', 'AbortError')),
    opts.timeoutMs ?? 15_000
  );

  const defaultHeaders = new Headers({
    'Content-Type': 'application/json',
    Accept: 'application/json',
  });

  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: defaultHeaders,
    signal: controller.signal,
  });

  clearTimeout(timeout);

  if (!res.ok) {
    const raw = await res.text().catch(() => '');
    const err = new Error(raw || res.statusText);
    Object.assign(err, { status: res.status, statusText: res.statusText });
    throw err;
  }

  const ctype = res.headers.get('content-type') ?? '';
  const rawBody = await res.text();
  if (ctype.includes('application/json')) {
    return JSON.parse(rawBody) as T;
  }
  return rawBody as unknown as T;
}

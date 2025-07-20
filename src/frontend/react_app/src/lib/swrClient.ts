export async function fetcher<T>(
  path: string,
  init: RequestInit = {},
  opts: { timeoutMs?: number; baseUrl?: string } = {}
): Promise<T> {
  const base = opts.baseUrl ?? import.meta.env.NEXT_PUBLIC_API_BASE_URL;
  if (!base) {
    throw new Error(
      'NEXT_PUBLIC_API_BASE_URL não configurada. Defina a variável ou passe opts.baseUrl.'
    );
  }

  /* ---------- AbortController + timeout ---------- */
  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(new DOMException('Timeout', 'AbortError')),
    opts.timeoutMs ?? 15_000
  );

  /* ---------- Cabeçalhos ---------- */
  const defaultHeaders = new Headers({
    'Content-Type': 'application/json',
    Accept: 'application/json',
  });
  const callerHeaders = new Headers(init.headers ?? {});
  callerHeaders.forEach((v, k) => defaultHeaders.set(k, v));

  let res: Response;
  try {
    res = await fetch(`${base}${path}`, {
      ...init,
      headers: defaultHeaders,
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timeout);
    /* Trata falhas de rede / abort */
    const error: Error & { cause?: unknown } = new Error('Network error');
    error.cause = err;
    throw error;
  } finally {
    clearTimeout(timeout);
  }

  /* ---------- HTTP status ---------- */
  if (!res.ok) {
    const raw = await res.text().catch(() => '');
    const err = new Error(raw || res.statusText);
    Object.assign(err, { status: res.status, statusText: res.statusText });
    throw err;
  }

  /* ---------- Corpo vazio ---------- */
  if (res.status === 204 || res.status === 205) return undefined as unknown as T;

  /* ---------- Parsing condicional ---------- */
  const ctype = res.headers.get('content-type') ?? '';
  const rawBody = await res.text();
  if (ctype.includes('application/json')) {
    try {
      return JSON.parse(rawBody) as T;
    } catch {
      /* JSON inválido — devolve string bruta */
    }
  }
  return rawBody as unknown as T;
}

test('health endpoint', async () => {
  const base =
    process.env.VITE_API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    'http://localhost:8000';
  const res = await fetch(`${base}/v1/health`);
  expect(res.status).toBe(200);
});

test('health endpoint HEAD', async () => {
  const base =
    process.env.VITE_API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    'http://localhost:8000';
  let res = await fetch(`${base}/v1/health`, { method: 'HEAD' });

  // Caso res.status seja undefined, faz um GET como fallback
  if (typeof res.status !== 'number') {
    res = await fetch(`${base}/v1/health`);
  }
  expect(res.status).toBe(200);
});

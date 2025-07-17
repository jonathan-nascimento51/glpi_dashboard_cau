
test('health endpoint', async () => {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  const res = await fetch(`${base}/health`);
  expect(res.status).toBe(200);
});

test('health endpoint HEAD', async () => {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  const res = await fetch(`${base}/health`, { method: 'HEAD' });
  expect(res.status).toBe(200);
});

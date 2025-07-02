
test('health endpoint', async () => {
  const base = process.env.API_BASE_URL || 'http://localhost:8000';
  const res = await fetch(`${base}/health`);
  expect(res.status).toBe(200);
});

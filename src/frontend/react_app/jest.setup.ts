import '@testing-library/jest-dom'

// Provide a default fetch mock for tests that don't override it
if (!global.fetch) {
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: async () => ({}) })
  ) as unknown as typeof fetch
}

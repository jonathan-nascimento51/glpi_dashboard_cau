module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run dev',
      url: ['http://localhost:5173'],
      numberOfRuns: 1,
    },
    assert: {
      assertions: {
        'largest-contentful-paint': ['error', { numericValue: 3000 }],
        'interactive': ['error', { numericValue: 3500 }],
        'total-byte-weight': ['error', { numericValue: 250000 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}

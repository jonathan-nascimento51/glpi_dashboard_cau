module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run start',
      url: ['http://localhost:3000'],
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

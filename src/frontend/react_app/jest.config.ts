import type { Config } from 'jest'

// Jest requires additional configuration to handle ES modules produced by
// ts-jest.  Without this, constructs like `import.meta` fail to parse during
// tests.  Enabling the `default-esm` preset and `useESM` option allows ts-jest
// to output native ESM which Node can execute.

const config: Config = {
  preset: 'ts-jest/presets/default-esm',
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  coverageProvider: 'v8',
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(ts|tsx)$': [
      'ts-jest',
      { tsconfig: 'tsconfig.test.json', useESM: true },
    ],
  },
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testMatch: [
    '<rootDir>/src/**/*.test.ts?(x)',
    '<rootDir>/tests/**/*.test.ts?(x)',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    'react-window': '<rootDir>/tests/__mocks__/react-window.ts',
  },
}

export default config

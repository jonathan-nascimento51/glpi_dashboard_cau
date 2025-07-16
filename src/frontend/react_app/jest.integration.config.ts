import type { Config } from 'jest';

const config: Config = {
  testEnvironment: 'node',
  testMatch: ['<rootDir>/tests/integration/**/*.test.ts'],
  globalSetup: '<rootDir>/jest.integration.setup.ts',
  globalTeardown: '<rootDir>/jest.integration.teardown.ts',
};

export default config;

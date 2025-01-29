const { createJestConfig } = require('./test/createJestConfig');

module.exports = createJestConfig({
  testTimeout: 10000,
  displayName: 'coreCli',
  projects: ['<rootDir>', '<rootDir>/packages/*'],
  globalSetup: './test/setup.js',
  setupFilesAfterEnv: ['./test/setup-jest.ts'],
  globalTeardown: './test/teardown.ts',
});

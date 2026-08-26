import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { usesLiveBackend } from './config.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../..');
const liveBackend = usesLiveBackend();

export default defineConfig({
  testDir: '.',
  testMatch: 'capture.spec.ts',
  timeout: liveBackend ? 300_000 : 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never', outputFolder: path.join(repoRoot, 'screenshots-report') }]],
  use: {
    ...devices['Desktop Chrome'],
    baseURL: 'http://127.0.0.1:3000',
    viewport: { width: 1400, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'dark',
    locale: 'en-US',
    timezoneId: 'UTC',
    launchOptions: {
      args: ['--font-render-hinting=none'],
    },
  },
  outputDir: path.join(repoRoot, 'screenshots-test-results'),
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 3000',
    cwd: path.join(repoRoot, 'frontend'),
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});

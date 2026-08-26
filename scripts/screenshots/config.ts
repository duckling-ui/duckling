import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** Use live Duckling backend (default) instead of mocked /api responses. Set to `0` for mock-only UI shots. */
export function usesLiveBackend(): boolean {
  return process.env.SCREENSHOTS_LIVE_BACKEND !== '0';
}

export const SAMPLE_PDF_PATH = path.resolve(__dirname, 'fixtures/sample-document.pdf');

export const BACKEND_HEALTH_URL =
  process.env.SCREENSHOTS_BACKEND_URL ?? 'http://127.0.0.1:5001/api/health';

export const BACKEND_BASE_URL = BACKEND_HEALTH_URL.replace(/\/api\/health\/?$/, '');

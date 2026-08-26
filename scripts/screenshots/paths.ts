import path from 'node:path';
import { fileURLToPath } from 'node:url';

export type Locale = 'en' | 'de' | 'fr' | 'es';

export const LOCALES: Locale[] = ['en', 'de', 'fr', 'es'];

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const SCREENSHOT_ROOT = path.resolve(__dirname, '../../docs/assets/screenshots');

const MAIN_BASENAMES: Record<Locale, string> = {
  en: 'main-english',
  de: 'main-german',
  fr: 'main-french',
  es: 'main-spanish',
};

/** Map logical shot id + locale to on-disk PNG path under docs/assets/screenshots. */
export function screenshotPath(relativeBase: string, locale: Locale): string {
  if (relativeBase === 'ui/main') {
    return path.join(SCREENSHOT_ROOT, 'ui', `${MAIN_BASENAMES[locale]}.png`);
  }
  if (locale === 'en') {
    return path.join(SCREENSHOT_ROOT, `${relativeBase}.png`);
  }
  return path.join(SCREENSHOT_ROOT, `${relativeBase}-${locale}.png`);
}

/** All PNG paths referenced by the capture manifest (for tests/docs). */
export function listManifestOutputPaths(): string[] {
  const bases = [
    'ui/dropzone-empty',
    'ui/dropzone-hover',
    'ui/dropzone-uploading',
    'ui/dropzone-batch',
    'ui/main',
    'ui/header',
    'ui/history-panel',
    'ui/history-search',
    'settings/settings-ocr',
    'settings/settings-ocr-install',
    'settings/settings-ocr-tesseract',
    'settings/settings-tables',
    'settings/settings-images',
    'settings/settings-pipeline',
    'settings/settings-pdf',
    'settings/settings-performance',
    'settings/settings-chunking',
    'settings/settings-enrichment',
    'settings/settings-enrichment-warning',
    'settings/settings-output',
    'features/conversion-progress',
    'features/conversion-complete',
    'features/confidence-display',
    'features/images-gallery',
    'features/images-hover',
    'features/images-lightbox',
    'features/tables-list',
    'features/tables-download',
    'features/chunks-list',
    'export/export-formats',
    'export/export-format-selected',
    'export/preview-toggle',
    'export/preview-markdown-rendered',
    'export/preview-markdown-raw',
    'export/preview-html-rendered',
    'export/preview-html-raw',
    'export/preview-json',
  ];
  return LOCALES.flatMap((locale) => bases.map((base) => screenshotPath(base, locale)));
}

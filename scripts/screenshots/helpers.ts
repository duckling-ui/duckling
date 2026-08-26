import type { Locator, Page } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import type { Locale } from './paths.js';
import { SAMPLE_PDF_PATH } from './config.js';
import { BACKEND_BASE_URL } from './config.js';
import { screenshotPath } from './paths.js';

const LOCALE_STORAGE_KEY = 'duckling.locale';

export async function preparePage(page: Page): Promise<void> {
  await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' });
  await page.addInitScript(() => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: (query: string) => ({
        matches: query.includes('prefers-reduced-motion'),
        media: query,
        onchange: null,
        addListener: () => undefined,
        removeListener: () => undefined,
        addEventListener: () => undefined,
        removeEventListener: () => undefined,
        dispatchEvent: () => false,
      }),
    });
    const style = document.createElement('style');
    style.textContent = `
      *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
      }
    `;
    document.head.appendChild(style);
  });
}

const LOCALE_HEADING: Record<Locale, RegExp> = {
  en: /Convert Any Document/i,
  de: /Beliebige Dokumente konvertieren/i,
  fr: /Convertissez n/i,
  es: /Convierte cualquier documento/i,
};

export async function setLocale(page: Page, locale: Locale): Promise<void> {
  await page.addInitScript(
    ([key, value]) => {
      window.localStorage.setItem(key, value);
    },
    [LOCALE_STORAGE_KEY, locale] as const,
  );
}

export async function waitForAppReady(page: Page, locale: Locale): Promise<void> {
  await page.goto('/');
  await page.getByTestId('dropzone-root').waitFor({ state: 'visible' });

  const activeLocale = await page.evaluate(() => document.documentElement.lang);
  if (activeLocale !== locale) {
    await page.selectOption('#language-select', locale);
  }

  await page.waitForFunction(
    (expected) => document.documentElement.lang === expected,
    locale,
  );
  await page.getByText(LOCALE_HEADING[locale]).waitFor({ state: 'visible' });
}

export async function screenshotLocator(
  locator: Locator,
  outputPath: string,
): Promise<void> {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await locator.screenshot({ path: outputPath, animations: 'disabled' });
}

export async function screenshotMainOverview(page: Page, outputPath: string): Promise<void> {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await page.getByTestId('app-root').waitFor({ state: 'visible' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.getByTestId('app-root').screenshot({ path: outputPath, animations: 'disabled' });
}

export async function openSettings(page: Page): Promise<void> {
  await page.getByTestId('open-settings').click();
  await page.getByTestId('settings-panel').waitFor({ state: 'visible' });
  await page.locator('[data-section="ocr"]').waitFor({ state: 'visible' });
}

export async function closeSettings(page: Page): Promise<void> {
  const panel = page.getByTestId('settings-panel');
  if (await panel.isVisible()) {
    await page.getByTestId('close-settings-panel').click();
    await panel.waitFor({ state: 'hidden' });
  }
}

export async function closePanelWithEscape(page: Page): Promise<void> {
  await closeSettings(page);
}

export async function openHistory(page: Page): Promise<void> {
  await page.getByTestId('open-history').click();
  await page.getByTestId('history-panel').waitFor({ state: 'visible' });
  await page.locator('[data-testid="history-panel"] h2').waitFor({ state: 'visible' });
}

export async function captureHistorySearch(page: Page, locale: Locale): Promise<void> {
  await openHistory(page);
  const search = page.getByTestId('history-panel-search');
  await search.fill('');
  await search.fill('sample-document');
  await page.waitForTimeout(500);
  await screenshotLocator(page.getByTestId('history-panel'), screenshotPath('ui/history-search', locale));
  await page.keyboard.press('Escape');
  await page.getByTestId('history-panel').waitFor({ state: 'hidden' });
}

export async function captureHistoryPanel(page: Page, locale: Locale): Promise<void> {
  await openHistory(page);
  await page.getByTestId('history-panel-search').fill('');
  await page.waitForTimeout(500);
  await screenshotLocator(page.getByTestId('history-panel'), screenshotPath('ui/history-panel', locale));
  await page.keyboard.press('Escape');
  await page.getByTestId('history-panel').waitFor({ state: 'hidden' });
}

export async function captureDropzoneHover(page: Page, locale: Locale): Promise<void> {
  const dropzone = page.getByTestId('dropzone-root');
  await dropzone.scrollIntoViewIfNeeded();
  await dropzone.dispatchEvent('dragenter');
  await page.waitForTimeout(200);
  await screenshotLocator(dropzone, screenshotPath('ui/dropzone-hover', locale));
  await dropzone.dispatchEvent('dragleave');
}

async function ensurePreviewVisible(page: Page): Promise<void> {
  const previewContent = page.getByTestId('export-preview-content');
  if (!(await previewContent.isVisible())) {
    await page.getByTestId('export-preview-visibility').click();
    await previewContent.waitFor({ state: 'visible' });
  }
}

async function waitForFormatPreviewReady(
  page: Page,
  format: 'markdown' | 'html' | 'json',
  mode: 'rendered' | 'raw',
): Promise<void> {
  const waitOpts = { timeout: 30_000 };

  await page.waitForFunction(
    () => !document.querySelector('[data-testid="export-preview-content"] .animate-spin'),
    undefined,
    waitOpts,
  );

  if (format === 'html' && mode === 'rendered') {
    const iframe = page.locator('[data-testid="export-preview-content"] iframe');
    await iframe.waitFor({ state: 'visible', timeout: 30_000 });
    await page.waitForTimeout(800);
    return;
  }

  if (format === 'markdown' && mode === 'rendered') {
    await page.waitForFunction(
      () => {
        const prose = document.querySelector('[data-testid="export-preview-content"] .prose');
        return (prose?.textContent?.trim().length ?? 0) > 20;
      },
      undefined,
      waitOpts,
    );
    await page.waitForTimeout(400);
    return;
  }

  await page.waitForFunction(
    () => {
      const pre = document.querySelector('[data-testid="export-preview-content"] pre');
      return (pre?.textContent?.trim().length ?? 0) > 20;
    },
    undefined,
    waitOpts,
  );
  await page.waitForTimeout(400);
}

async function setPreviewMode(page: Page, mode: 'rendered' | 'raw'): Promise<void> {
  const toggle = page.getByTestId('export-preview-toggle');
  if (!(await toggle.isVisible())) {
    return;
  }
  await toggle.locator('button').nth(mode === 'rendered' ? 0 : 1).click();
  await page.waitForTimeout(400);
}

async function screenshotFormatPreview(
  page: Page,
  outputPath: string,
  format: 'markdown' | 'html' | 'json',
  mode: 'rendered' | 'raw',
): Promise<void> {
  await ensurePreviewVisible(page);
  await waitForFormatPreviewReady(page, format, mode);

  if (format === 'html' && mode === 'rendered') {
    await screenshotLocator(
      page.locator('[data-testid="export-preview-content"] iframe'),
      outputPath,
    );
    return;
  }

  await screenshotLocator(page.getByTestId('export-preview-content'), outputPath);
}

export async function clearHistoryViaApi(page: Page): Promise<void> {
  await page.request.delete(`${BACKEND_BASE_URL}/api/history`);
}

export async function prepareFastConversionSettings(page: Page): Promise<void> {
  await page.request.put(`${BACKEND_BASE_URL}/api/settings/enrichment`, {
    data: {
      enrichment: {
        code_enrichment: false,
        formula_enrichment: false,
        picture_classification: false,
        picture_description: false,
        chart_extraction: false,
      },
    },
  });
}

export async function captureSettingsSection(
  page: Page,
  sectionId: string,
  outputPath: string,
): Promise<void> {
  const section = page.locator(`[data-section="${sectionId}"]`);
  await section.scrollIntoViewIfNeeded();
  await screenshotLocator(section, outputPath);
}

export async function uploadSamplePdf(page: Page): Promise<void> {
  await page.getByTestId('dropzone-file-input').setInputFiles(SAMPLE_PDF_PATH);
}

export async function waitForConversionComplete(page: Page, timeoutMs = 180_000): Promise<void> {
  await page.getByTestId('export-options').waitFor({ state: 'visible', timeout: timeoutMs });
  await page.getByTestId('export-formats-list').waitFor({ state: 'visible' });
}

export async function captureConversionShots(page: Page, locale: Locale): Promise<void> {
  await prepareFastConversionSettings(page);

  const progress = page.getByTestId('conversion-progress');
  const uploadPromise = uploadSamplePdf(page);
  const progressVisible = progress.waitFor({ state: 'visible', timeout: 15_000 }).catch(() => undefined);
  await uploadPromise;
  await progressVisible;
  if (await progress.isVisible()) {
    await screenshotLocator(progress, screenshotPath('ui/dropzone-uploading', locale));
    await screenshotLocator(progress, screenshotPath('features/conversion-progress', locale));
  }

  await waitForConversionComplete(page);

  await screenshotLocator(
    page.getByTestId('conversion-complete-header'),
    screenshotPath('features/conversion-complete', locale),
  );

  const confidenceLine = page.getByTestId('conversion-complete-header').locator('.text-primary-400').first();
  if (await confidenceLine.isVisible()) {
    await screenshotLocator(
      page.getByTestId('conversion-complete-header'),
      screenshotPath('features/confidence-display', locale),
    );
  }

  await screenshotLocator(
    page.getByTestId('export-formats-list'),
    screenshotPath('export/export-formats', locale),
  );

  const markdownButton = page
    .getByTestId('export-formats-list')
    .locator('button[data-format="markdown"]')
    .first();
  if (await markdownButton.count()) {
    await markdownButton.click();
    await screenshotLocator(
      page.getByTestId('export-formats-list'),
      screenshotPath('export/export-format-selected', locale),
    );
  }

  const previewToggle = page.getByTestId('export-preview-toggle');
  if (await previewToggle.isVisible()) {
    await ensurePreviewVisible(page);
    await screenshotLocator(previewToggle, screenshotPath('export/preview-toggle', locale));
    await setPreviewMode(page, 'rendered');
    await screenshotFormatPreview(
      page,
      screenshotPath('export/preview-markdown-rendered', locale),
      'markdown',
      'rendered',
    );

    await setPreviewMode(page, 'raw');
    await screenshotFormatPreview(
      page,
      screenshotPath('export/preview-markdown-raw', locale),
      'markdown',
      'raw',
    );
  }

  const htmlButton = page.getByTestId('export-formats-list').locator('button[data-format="html"]').first();
  if (await htmlButton.count()) {
    await htmlButton.click();
    await ensurePreviewVisible(page);
    await setPreviewMode(page, 'rendered');
    await screenshotFormatPreview(
      page,
      screenshotPath('export/preview-html-rendered', locale),
      'html',
      'rendered',
    );

    await setPreviewMode(page, 'raw');
    await screenshotFormatPreview(
      page,
      screenshotPath('export/preview-html-raw', locale),
      'html',
      'raw',
    );
  }

  const jsonButton = page.getByTestId('export-formats-list').locator('button[data-format="json"]').first();
  if (await jsonButton.count()) {
    await jsonButton.click();
    await screenshotFormatPreview(page, screenshotPath('export/preview-json', locale), 'json', 'raw');
  }

  const imagesTab = page.getByTestId('export-tab-images');
  if (await imagesTab.isVisible()) {
    await imagesTab.click();
    await page.waitForTimeout(800);
    const exportOptions = page.getByTestId('export-options');
    await page.waitForFunction(
      () => {
        const panel = document.querySelector('[data-testid="export-options"]');
        return panel != null && panel.querySelectorAll('img').length > 0;
      },
      undefined,
      { timeout: 15_000 },
    ).catch(() => undefined);
    await screenshotLocator(exportOptions, screenshotPath('features/images-gallery', locale));

    const firstImageCard = exportOptions.locator('.group').first();
    if (await firstImageCard.count()) {
      await firstImageCard.hover();
      await page.waitForTimeout(400);
      await screenshotLocator(exportOptions, screenshotPath('features/images-hover', locale));
    }
  }

  const tablesTab = page.getByTestId('export-tab-tables');
  if (await tablesTab.isVisible()) {
    await tablesTab.click();
    await page.waitForTimeout(800);
    const exportOptions = page.getByTestId('export-options');
    await page.waitForFunction(() => {
      const panel = document.querySelector('[data-testid="export-options"]');
      return panel != null && (panel.textContent?.includes('CSV') || panel.textContent?.includes('csv'));
    }).catch(() => undefined);
    await screenshotLocator(exportOptions, screenshotPath('features/tables-list', locale));
    await screenshotLocator(exportOptions, screenshotPath('features/tables-download', locale));
  }

  const chunksTab = page.getByTestId('export-tab-chunks');
  if (await chunksTab.isVisible()) {
    await chunksTab.click();
    await page.waitForTimeout(800);
    const exportOptions = page.getByTestId('export-options');
    const generateButton = exportOptions
      .locator('button')
      .filter({ hasText: /generate|generieren|generar|générer/i })
      .first();
    if (await generateButton.count()) {
      await generateButton.click();
      await page.waitForTimeout(2000);
    }
    await screenshotLocator(exportOptions, screenshotPath('features/chunks-list', locale));
  }
}

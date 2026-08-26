import { test } from '@playwright/test';
import { installApiMocks } from './mock-api.js';
import { usesLiveBackend } from './config.js';
import {
  captureConversionShots,
  captureDropzoneHover,
  captureHistoryPanel,
  captureHistorySearch,
  captureSettingsSection,
  clearHistoryViaApi,
  closePanelWithEscape,
  openSettings,
  preparePage,
  screenshotLocator,
  screenshotMainOverview,
  setLocale,
  waitForAppReady,
} from './helpers.js';
import { LOCALES, screenshotPath, type Locale } from './paths.js';

const liveBackend = usesLiveBackend();

test.describe('documentation screenshots', () => {
  test.beforeEach(async ({ page }) => {
    await preparePage(page);
    if (!liveBackend) {
      await installApiMocks(page);
    }
  });

  for (const locale of LOCALES) {
    test(`capture UI and settings (${locale})`, async ({ page }) => {
      test.setTimeout(liveBackend ? 300_000 : 120_000);

      await setLocale(page, locale);
      await waitForAppReady(page, locale);

      if (liveBackend) {
        await clearHistoryViaApi(page);
      }

      await screenshotLocator(page.getByTestId('dropzone-root'), screenshotPath('ui/dropzone-empty', locale));
      await captureDropzoneHover(page, locale);
      await screenshotLocator(page.getByTestId('app-header'), screenshotPath('ui/header', locale));
      await screenshotMainOverview(page, screenshotPath('ui/main', locale));

      if (liveBackend) {
        await captureConversionShots(page, locale);
      }

      await openSettings(page);
      await captureSettingsSection(page, 'ocr', screenshotPath('settings/settings-ocr', locale));
      await captureSettingsSection(page, 'tables', screenshotPath('settings/settings-tables', locale));
      await captureSettingsSection(page, 'images', screenshotPath('settings/settings-images', locale));
      await captureSettingsSection(page, 'pipeline', screenshotPath('settings/settings-pipeline', locale));
      await captureSettingsSection(page, 'pdf', screenshotPath('settings/settings-pdf', locale));
      await captureSettingsSection(page, 'performance', screenshotPath('settings/settings-performance', locale));
      await captureSettingsSection(page, 'chunking', screenshotPath('settings/settings-chunking', locale));
      await captureSettingsSection(page, 'enrichment', screenshotPath('settings/settings-enrichment', locale));

      const warning = page.getByTestId('settings-enrichment-warning');
      if (await warning.isVisible()) {
        await screenshotLocator(warning, screenshotPath('settings/settings-enrichment-warning', locale));
      }

      await captureSettingsSection(page, 'output', screenshotPath('settings/settings-output', locale));
      await captureSettingsSection(page, 'ocr', screenshotPath('settings/settings-ocr-install', locale));

      await closePanelWithEscape(page);
      await captureHistorySearch(page, locale);
      await captureHistoryPanel(page, locale);
    });
  }
});

/** Exported for manifest validation tests in Python. */
export const MANIFEST_LOCALES: Locale[] = LOCALES;

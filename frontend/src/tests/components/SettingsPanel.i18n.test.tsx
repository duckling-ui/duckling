/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-present David G. Simmons
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { act } from 'react';

import i18n from '../../i18n';
import SettingsPanel from '../../components/SettingsPanel';

vi.mock('../../hooks/useSettings', () => {
  return {
    useAllSettings: () => ({
      isLoading: false,
      settings: {
        resetSettings: vi.fn(),
        isResetting: false,
      },
      ocr: {
        ocr: { enabled: true, backend: 'easyocr', language: 'en' },
        availableLanguages: [],
        availableBackends: [],
        backendsStatus: [],
        isUpdating: false,
        isInstalling: false,
        installError: null,
        clearInstallError: vi.fn(),
        updateOcr: vi.fn(),
        installBackend: vi.fn(),
      },
      tables: {
        tables: { enabled: true, mode: 'accurate', structure_extraction: true, do_cell_matching: true },
        availableModes: [],
        isUpdating: false,
        updateTables: vi.fn(),
      },
      images: {
        images: {
          extract: true,
          classify: true,
          generate_page_images: false,
          generate_picture_images: true,
          generate_table_images: true,
          images_scale: 1.0,
        },
        isUpdating: false,
        updateImages: vi.fn(),
      },
      performance: {
        performance: { device: 'auto', num_threads: 4, document_timeout: null },
        availableDevices: [],
        isUpdating: false,
        updatePerformance: vi.fn(),
      },
      chunking: {
        chunking: { enabled: false, max_tokens: 512, merge_peers: true },
        isUpdating: false,
        updateChunking: vi.fn(),
      },
      enrichment: {
        enrichment: {
          code_enrichment: false,
          formula_enrichment: false,
          picture_classification: false,
          picture_description: false,
        },
        isUpdating: false,
        updateEnrichment: vi.fn(),
        models: [],
        downloadingModels: {},
        downloadProgress: {},
        downloadModel: vi.fn(),
      },
      output: {
        output: { default_format: 'markdown' },
        availableFormats: [],
        isUpdating: false,
        updateOutput: vi.fn(),
      },
    }),
  };
});

describe('SettingsPanel i18n', () => {
  it('renders Settings strings in Spanish when language is es', async () => {
    await act(async () => {
      await i18n.changeLanguage('es');
    });

    render(<SettingsPanel isOpen={true} onClose={() => {}} />);

    expect(screen.getByText('Configuración')).toBeInTheDocument();
    expect(screen.getByText('Habilitar OCR')).toBeInTheDocument();
  });
});



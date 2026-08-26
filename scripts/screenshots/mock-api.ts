import type { Page, Route } from '@playwright/test';

const baseSettings = {
  pipeline: { kind: 'standard', vlm_preset: 'default', vlm_custom_config: null, force_backend_text: false },
  pdf: {
    pdf_backend: 'docling_parse',
    image_export_mode: 'placeholder',
    do_pdf_heading_hierarchy: false,
    pdf_heading_hierarchy_options: {
      use_bookmarks: true,
      use_numbering: true,
      use_style: true,
      max_level: 6,
    },
  },
  ocr: {
    enabled: true,
    language: 'en',
    backend: 'easyocr',
    mode: 'default',
    scale: 3.0,
    force_full_page_ocr: false,
    use_gpu: false,
    confidence_threshold: 0.5,
  },
  tables: { enabled: true, structure_extraction: true, mode: 'accurate', do_cell_matching: true },
  images: {
    extract: true,
    classify: true,
    generate_page_images: false,
    generate_picture_images: true,
    generate_table_images: true,
    images_scale: 1.0,
  },
  enrichment: {
    code_enrichment: false,
    formula_enrichment: false,
    picture_classification: false,
    picture_description: true,
    chart_extraction: false,
    picture_description_preset: null,
    picture_description_custom_config: null,
    code_formula_preset: null,
    code_formula_custom_config: null,
    picture_classification_preset: null,
    layout_preset: null,
    table_structure_preset: null,
  },
  output: { default_format: 'markdown' },
  performance: { device: 'auto', num_threads: 4, document_timeout: null },
  chunking: {
    enabled: true,
    chunker: 'hybrid',
    chunking_preset: null,
    max_tokens: 512,
    merge_peers: true,
    tokenizer: 'sentence-transformers/all-MiniLM-L6-v2',
    use_markdown_tables: false,
    use_markdown_images: false,
    image_placeholder: '[image]',
    include_raw_text: false,
  },
};

const ocrBackends = [
  {
    id: 'easyocr',
    name: 'EasyOCR',
    description: 'General-purpose OCR',
    installed: true,
    available: true,
    error: null,
    pip_installable: true,
    requires_system_install: false,
    platform: 'linux',
    note: '',
  },
  {
    id: 'tesseract',
    name: 'Tesseract',
    description: 'Classic OCR engine',
    installed: false,
    available: false,
    error: 'System package required',
    pip_installable: false,
    requires_system_install: true,
    platform: 'linux',
    note: 'Install tesseract-ocr via apt',
  },
];

const enrichmentModels = [
  {
    id: 'picture_description',
    name: 'Picture Description',
    feature: 'picture_description',
    installed: false,
    available: true,
    size_mb: 1200,
    description: 'Vision model for image captions',
  },
];

const historyEntry = {
  id: 'demo-job-1',
  filename: 'sample-document.pdf',
  original_filename: 'sample-document.pdf',
  input_format: 'pdf',
  status: 'completed',
  created_at: '2026-08-21T12:00:00Z',
  completed_at: '2026-08-21T12:01:00Z',
  confidence: 0.98,
};

const historyStats = {
  conversions: {
    total: 1,
    completed: 1,
    failed: 0,
    pending: 0,
    processing: 0,
    success_rate: 100,
    format_breakdown: { pdf: 1 },
    avg_processing_seconds: 12.4,
  },
  queue_depth: 0,
};

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

function apiPath(url: string): string {
  const parsed = new URL(url);
  const idx = parsed.pathname.indexOf('/api/');
  return idx >= 0 ? parsed.pathname.slice(idx) : parsed.pathname;
}

export async function installApiMocks(page: Page): Promise<void> {
  await page.route('**/api/**', async (route) => {
    const pathname = apiPath(route.request().url());
    const method = route.request().method();

    if (pathname === '/api/health' && method === 'GET') {
      return json(route, { status: 'healthy', service: 'duckling-backend' });
    }
    if (pathname === '/api/settings' && method === 'GET') {
      return json(route, baseSettings);
    }
    if (pathname === '/api/settings/pipeline' && method === 'GET') {
      return json(route, {
        pipeline: baseSettings.pipeline,
        options: { kind: ['standard', 'vlm', 'asr'], vlm_presets: ['default'], allow_custom_vlm_config: false },
      });
    }
    if (pathname === '/api/settings/pdf' && method === 'GET') {
      return json(route, {
        pdf: baseSettings.pdf,
        options: {
          pdf_backend: ['docling_parse', 'pypdfium2'],
          image_export_mode: ['placeholder', 'embedded', 'referenced'],
        },
      });
    }
    if (pathname === '/api/settings/ocr' && method === 'GET') {
      return json(route, {
        ocr: baseSettings.ocr,
        available_backends: ocrBackends.map(({ id, name, description }) => ({ id, name, description })),
        available_languages: [{ code: 'en', name: 'English' }],
      });
    }
    if (pathname === '/api/settings/ocr/backends' && method === 'GET') {
      return json(route, { backends: ocrBackends, current_platform: 'linux' });
    }
    if (pathname.startsWith('/api/settings/ocr/backends/') && method === 'GET') {
      const backend = pathname.split('/').pop() ?? 'easyocr';
      const match = ocrBackends.find((b) => b.id === backend) ?? ocrBackends[0];
      return json(route, { backend: match.id, ...match });
    }
    if (pathname === '/api/settings/tables' && method === 'GET') {
      return json(route, { tables: baseSettings.tables, options: { mode: ['fast', 'accurate'] } });
    }
    if (pathname === '/api/settings/images' && method === 'GET') {
      return json(route, { images: baseSettings.images });
    }
    if (pathname === '/api/settings/performance' && method === 'GET') {
      return json(route, {
        performance: baseSettings.performance,
        options: { device: ['auto', 'cpu', 'cuda', 'mps'] },
      });
    }
    if (pathname === '/api/settings/chunking' && method === 'GET') {
      return json(route, {
        chunking: baseSettings.chunking,
        options: { chunker: ['hybrid', 'hierarchical'] },
      });
    }
    if (pathname === '/api/settings/output' && method === 'GET') {
      return json(route, {
        output: baseSettings.output,
        formats: [{ id: 'markdown', name: 'Markdown', extension: '.md' }],
      });
    }
    if (pathname === '/api/settings/enrichment' && method === 'GET') {
      return json(route, {
        enrichment: baseSettings.enrichment,
        models: enrichmentModels,
        options: {
          code_enrichment: { enabled: false },
          formula_enrichment: { enabled: false },
          picture_classification: { enabled: false },
          picture_description: { enabled: true },
        },
      });
    }
    if (pathname === '/api/settings/enrichment/models' && method === 'GET') {
      return json(route, { models: enrichmentModels });
    }
    if (pathname.startsWith('/api/settings/enrichment/models/') && pathname.endsWith('/status') && method === 'GET') {
      return json(route, { model_id: 'picture_description', installed: false, available: true, progress: 0 });
    }
    if (pathname === '/api/settings/formats' && method === 'GET') {
      return json(route, {
        input_formats: [{ id: 'pdf', name: 'PDF', extensions: ['.pdf'] }],
        output_formats: [{ id: 'markdown', name: 'Markdown', extension: '.md' }],
      });
    }
    if (pathname === '/api/history/recent' && method === 'GET') {
      return json(route, { entries: [historyEntry], count: 1 });
    }
    if (pathname.startsWith('/api/history/search') && method === 'GET') {
      return json(route, { entries: [historyEntry], count: 1, query: 'sample' });
    }
    if (pathname === '/api/history' && method === 'GET') {
      return json(route, { entries: [historyEntry], count: 1, limit: 20, offset: 0 });
    }
    if (pathname === '/api/history/stats' && method === 'GET') {
      return json(route, historyStats);
    }
    if (method === 'PUT' || method === 'POST' || method === 'DELETE') {
      return json(route, { message: 'ok', settings: baseSettings });
    }

    return json(route, {});
  });
}

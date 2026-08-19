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

// API Types

export interface InputFormat {
  id: string;
  name: string;
  extensions: string[];
  icon?: string;
}

export interface OutputFormat {
  id: string;
  name: string;
  extension: string;
  mime_type?: string;
}

export interface FormatsResponse {
  input_formats: InputFormat[];
  output_formats: OutputFormat[];
}

export interface OcrSettings {
  enabled: boolean;
  language: string;
  backend: 'easyocr' | 'tesseract' | 'ocrmac' | 'rapidocr';
  mode: 'default' | 'full_page' | 'layout_regions' | 'pdf_aware_layout_regions';
  scale: number;
  /** @deprecated Prefer mode=full_page; still accepted as a shim */
  force_full_page_ocr: boolean;
  use_gpu: boolean;
  confidence_threshold: number;
  /** @deprecated Removed from Docling OcrOptions (2.116+); ignored by backend */
  bitmap_area_threshold?: number;
}

export interface TableSettings {
  enabled: boolean;
  structure_extraction: boolean;
  mode: 'fast' | 'accurate';
  do_cell_matching: boolean;
}

export interface ImageSettings {
  extract: boolean;
  classify: boolean;
  generate_page_images: boolean;
  generate_picture_images: boolean;
  generate_table_images: boolean;
  images_scale: number;
}

export interface PerformanceSettings {
  device: 'auto' | 'cpu' | 'cuda' | 'mps';
  num_threads: number;
  document_timeout: number | null;
}

export interface ChunkingSettings {
  enabled: boolean;
  chunker: 'hybrid' | 'hierarchical';
  chunking_preset?: string | null;
  max_tokens: number;
  merge_peers: boolean;
  tokenizer: string;
  use_markdown_tables: boolean;
  use_markdown_images: boolean;
  image_placeholder: string;
  include_raw_text: boolean;
}

export interface EnrichmentSettings {
  code_enrichment: boolean;
  formula_enrichment: boolean;
  picture_classification: boolean;
  picture_description: boolean;
  chart_extraction: boolean;
  picture_description_preset?: string | null;
  picture_description_custom_config?: Record<string, unknown> | null;
  code_formula_preset?: string | null;
  code_formula_custom_config?: Record<string, unknown> | null;
  picture_classification_preset?: string | null;
  layout_preset?: string | null;
  table_structure_preset?: string | null;
}

export interface PipelineSettings {
  kind: 'standard' | 'vlm' | 'asr';
  vlm_preset: string;
  vlm_custom_config?: Record<string, unknown> | null;
  force_backend_text: boolean;
}

export interface PdfSettings {
  pdf_backend: string;
  image_export_mode: 'placeholder' | 'embedded' | 'referenced';
  do_pdf_heading_hierarchy: boolean;
  pdf_heading_hierarchy_options: {
    use_bookmarks: boolean;
    use_numbering: boolean;
    use_style: boolean;
    max_level: number;
  };
}

export interface OutputSettings {
  default_format: string;
}

export interface ConversionSettings {
  pipeline: PipelineSettings;
  pdf: PdfSettings;
  ocr: OcrSettings;
  tables: TableSettings;
  images: ImageSettings;
  enrichment: EnrichmentSettings;
  output: OutputSettings;
  performance: PerformanceSettings;
  chunking: ChunkingSettings;
}

export interface SettingsResponse {
  settings: ConversionSettings;
  defaults: ConversionSettings;
}

export interface ConversionJob {
  job_id: string;
  filename: string;
  input_format: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface ConversionStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  confidence?: number;
  formats_available?: string[];
  preview?: string;
  page_count?: number;
  images_count?: number;
  tables_count?: number;
  chunks_count?: number;
  error?: string;
}

export interface ConversionResult {
  job_id: string;
  status: string;
  confidence?: number;
  formats_available: string[];
  result: {
    markdown_preview: string;
    formats_available: string[];
    page_count?: number;
    images_count?: number;
    tables_count?: number;
    chunks_count?: number;
    warnings?: string[];
  };
  images_count?: number;
  tables_count?: number;
  chunks_count?: number;
  completed_at?: string;
}

export interface ExtractedImage {
  id: number;
  filename: string;
  path: string;
  caption?: string;
  label?: string;
}

export interface ExtractedTable {
  id: number;
  label?: string;
  caption?: string;
  rows: string[][];
  csv_path?: string;
  image_path?: string;
}

export interface DocumentChunk {
  id: number;
  text: string;
  meta?: {
    headings?: string[];
    page?: number;
  };
}

export interface HistoryEntry {
  id: string;
  filename: string;
  original_filename: string;
  input_format: string;
  status: string;
  confidence?: number;
  created_at: string;
  completed_at?: string;
  settings?: ConversionSettings;
  error_message?: string;
  output_path?: string;
  file_size?: number;
  document_json_path?: string;
}

export interface HistoryResponse {
  entries: HistoryEntry[];
  count: number;
  limit: number;
  offset: number;
}

export interface HistoryStats {
  conversions: {
    total: number;
    completed: number;
    failed: number;
    pending: number;
    processing: number;
    success_rate: number;
    format_breakdown: Record<string, number>;
    avg_processing_seconds?: number;
    ocr_backend_breakdown?: Record<string, number>;
    output_format_breakdown?: Record<string, number>;
    performance_device_breakdown?: Record<string, number>;
    chunking_enabled_count?: number;
    error_category_breakdown?: Record<string, number>;
    source_type_breakdown?: Record<string, number>;
    system?: {
      cpu_count?: number;
      hardware_type?: string;
      gpu_name?: string | null;
      gpu_memory_mb?: number | null;
      cpu_usage_current?: number | null;
    };
    avg_pages_per_second?: number | null;
    avg_pages_per_second_per_cpu?: number | null;
    conversion_time_distribution?: {
      p50: number;
      p95: number;
      p99: number;
    } | null;
    pages_per_second_over_time?: Array<{
      job_id: string;
      created_at: string | null;
      pages_per_sec: number;
    }>;
    by_hardware?: Record<
      string,
      {
        count: number;
        avg_processing_seconds?: number;
        avg_pages_per_second?: number;
        conversion_time_p50?: number;
        conversion_time_p95?: number;
        conversion_time_p99?: number;
      }
    >;
    by_ocr_backend?: Record<
      string,
      {
        count: number;
        avg_processing_seconds?: number;
        avg_pages_per_second?: number;
        conversion_time_p50?: number;
        conversion_time_p95?: number;
        conversion_time_p99?: number;
      }
    >;
    by_images_classify?: Record<
      string,
      {
        count: number;
        avg_processing_seconds?: number;
        avg_pages_per_second?: number;
        conversion_time_p50?: number;
        conversion_time_p95?: number;
        conversion_time_p99?: number;
      }
    >;
  };
  storage: {
    uploads: {
      count: number;
      size_bytes: number;
      size_mb: number;
    };
    outputs: {
      count: number;
      size_bytes: number;
      size_mb: number;
    };
    total_size_mb: number;
  };
  queue_depth?: number;
}

export interface OcrSettingsResponse {
  ocr: OcrSettings;
  available_languages: {
    code: string;
    name: string;
  }[];
  available_backends: {
    id: string;
    name: string;
    description: string;
  }[];
  options: Record<string, {
    description: string;
    default: string | number | boolean | null;
    min?: number;
    max?: number;
  }>;
}

export interface TableSettingsResponse {
  tables: TableSettings;
  available_modes: {
    id: string;
    name: string;
    description: string;
  }[];
  options: Record<string, {
    description: string;
    default: string | number | boolean;
  }>;
}

export interface ImageSettingsResponse {
  images: ImageSettings;
  options: Record<string, {
    description: string;
    default: string | number | boolean;
    min?: number;
    max?: number;
  }>;
}

export interface PerformanceSettingsResponse {
  performance: PerformanceSettings;
  available_devices: {
    id: string;
    name: string;
    description: string;
  }[];
  options: Record<string, {
    description: string;
    default: string | number | boolean | null;
    min?: number;
    max?: number;
  }>;
}

export interface ChunkingSettingsResponse {
  chunking: ChunkingSettings;
  options: Record<string, {
    description: string;
    default: string | number | boolean;
    min?: number;
    max?: number;
  }>;
}

export interface EnrichmentSettingsResponse {
  enrichment: EnrichmentSettings;
  options: Record<string, {
    description: string;
    default: boolean;
    note?: string;
  }>;
}

export interface BatchJob {
  job_id?: string;
  filename: string;
  input_format?: string;
  status: 'processing' | 'completed' | 'failed' | 'rejected';
  error?: string;
}

export interface BatchConversionResponse {
  jobs: BatchJob[];
  total: number;
  message: string;
}

// Component Props Types

export interface DropZoneProps {
  onFilesAccepted: (files: File[]) => void;
  onUrlsSubmitted?: (urls: string[]) => void;
  isUploading: boolean;
  disabled?: boolean;
}

export interface ConversionProgressProps {
  jobId: string;
  onComplete: (result: ConversionResult) => void;
  onError: (error: string) => void;
}

export interface ExportOptionsProps {
  jobId: string;
  formatsAvailable: string[];
  preview?: string;
  imagesCount?: number;
  tablesCount?: number;
  chunksCount?: number;
}

export interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export interface HistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectEntry: (entry: HistoryEntry) => void;
}

// App State Types

export type AppState = 'idle' | 'uploading' | 'processing' | 'complete' | 'error';

export interface AppContextType {
  state: AppState;
  currentJob: ConversionJob | null;
  result: ConversionResult | null;
  error: string | null;
  settings: ConversionSettings | null;
}


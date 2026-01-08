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
  force_full_page_ocr: boolean;
  backend: 'easyocr' | 'tesseract' | 'ocrmac' | 'rapidocr';
  use_gpu: boolean;
  confidence_threshold: number;
  bitmap_area_threshold: number;
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
  max_tokens: number;
  merge_peers: boolean;
}

export interface EnrichmentSettings {
  code_enrichment: boolean;
  formula_enrichment: boolean;
  picture_classification: boolean;
  picture_description: boolean;
}

export interface OutputSettings {
  default_format: string;
}

export interface ConversionSettings {
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
  onFileAccepted: (file: File) => void;
  onFilesAccepted?: (files: File[]) => void;
  isUploading: boolean;
  disabled?: boolean;
  multiple?: boolean;
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


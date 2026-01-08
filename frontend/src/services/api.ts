import axios from 'axios';
import type {
  FormatsResponse,
  SettingsResponse,
  ConversionSettings,
  ConversionJob,
  ConversionStatus,
  ConversionResult,
  HistoryResponse,
  HistoryEntry,
  HistoryStats,
  OcrSettingsResponse,
  TableSettingsResponse,
  ImageSettingsResponse,
  PerformanceSettingsResponse,
  ChunkingSettingsResponse,
  ExtractedImage,
  ExtractedTable,
  DocumentChunk,
  BatchConversionResponse,
} from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async (): Promise<{ status: string; service: string }> => {
  const response = await api.get('/health');
  return response.data;
};

// Formats
export const getFormats = async (): Promise<FormatsResponse> => {
  const response = await api.get('/settings/formats');
  return response.data;
};

// Conversion
export const uploadAndConvert = async (
  file: File,
  settings?: Partial<ConversionSettings>
): Promise<ConversionJob> => {
  const formData = new FormData();
  formData.append('file', file);
  if (settings) {
    formData.append('settings', JSON.stringify(settings));
  }

  const response = await api.post('/convert', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Batch conversion
export const uploadAndConvertBatch = async (
  files: File[],
  settings?: Partial<ConversionSettings>
): Promise<BatchConversionResponse> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  if (settings) {
    formData.append('settings', JSON.stringify(settings));
  }

  const response = await api.post('/convert/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// URL conversion
export const convertFromUrl = async (
  url: string,
  settings?: Partial<ConversionSettings>
): Promise<ConversionJob & { source_url: string }> => {
  const response = await api.post('/convert/url', {
    url,
    settings,
  });
  return response.data;
};

// Batch URL conversion
export const convertFromUrlsBatch = async (
  urls: string[],
  settings?: Partial<ConversionSettings>
): Promise<BatchConversionResponse & { jobs: (BatchConversionResponse['jobs'][0] & { url?: string })[] }> => {
  const response = await api.post('/convert/url/batch', {
    urls,
    settings,
  });
  return response.data;
};

export const getConversionStatus = async (jobId: string): Promise<ConversionStatus> => {
  const response = await api.get(`/convert/${jobId}/status`);
  return response.data;
};

export const getConversionResult = async (jobId: string): Promise<ConversionResult> => {
  const response = await api.get(`/convert/${jobId}/result`);
  return response.data;
};

export const getExportContent = async (
  jobId: string,
  format: string
): Promise<{ job_id: string; format: string; content: string }> => {
  const response = await api.get(`/export/${jobId}/${format}/content`);
  return response.data;
};

export const downloadExport = async (jobId: string, format: string): Promise<Blob> => {
  const response = await api.get(`/export/${jobId}/${format}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const deleteJob = async (jobId: string): Promise<void> => {
  await api.delete(`/convert/${jobId}`);
};

// Extracted content
export const getExtractedImages = async (
  jobId: string
): Promise<{ job_id: string; images: ExtractedImage[]; count: number }> => {
  const response = await api.get(`/convert/${jobId}/images`);
  return response.data;
};

export const downloadExtractedImage = async (jobId: string, imageId: number): Promise<Blob> => {
  const response = await api.get(`/convert/${jobId}/images/${imageId}`, {
    responseType: 'blob',
  });
  return response.data;
};

export const getExtractedTables = async (
  jobId: string
): Promise<{ job_id: string; tables: ExtractedTable[]; count: number }> => {
  const response = await api.get(`/convert/${jobId}/tables`);
  return response.data;
};

export const downloadTableCsv = async (jobId: string, tableId: number): Promise<Blob> => {
  const response = await api.get(`/convert/${jobId}/tables/${tableId}/csv`, {
    responseType: 'blob',
  });
  return response.data;
};

export const downloadTableImage = async (jobId: string, tableId: number): Promise<Blob> => {
  const response = await api.get(`/convert/${jobId}/tables/${tableId}/image`, {
    responseType: 'blob',
  });
  return response.data;
};

export const getDocumentChunks = async (
  jobId: string
): Promise<{ job_id: string; chunks: DocumentChunk[]; count: number }> => {
  const response = await api.get(`/convert/${jobId}/chunks`);
  return response.data;
};

// Settings
export const getSettings = async (): Promise<SettingsResponse> => {
  const response = await api.get('/settings');
  return response.data;
};

export const updateSettings = async (
  settings: Partial<ConversionSettings>
): Promise<{ message: string; settings: ConversionSettings }> => {
  const response = await api.put('/settings', settings);
  return response.data;
};

export const resetSettings = async (): Promise<{ message: string; settings: ConversionSettings }> => {
  const response = await api.post('/settings/reset');
  return response.data;
};

export const getOcrSettings = async (): Promise<OcrSettingsResponse> => {
  const response = await api.get('/settings/ocr');
  return response.data;
};

export const updateOcrSettings = async (
  settings: Partial<{
    enabled: boolean;
    language: string;
    backend: string;
    force_full_page_ocr: boolean;
    use_gpu: boolean;
    confidence_threshold: number;
    bitmap_area_threshold: number;
  }>,
  autoInstall = false
): Promise<{ message: string; ocr: Record<string, unknown> }> => {
  const response = await api.put(`/settings/ocr${autoInstall ? '?auto_install=true' : ''}`, settings);
  return response.data;
};

// OCR Backend management
export interface OcrBackendStatus {
  id: string;
  name: string;
  description: string;
  installed: boolean;
  available: boolean;
  error: string | null;
  pip_installable: boolean;
  requires_system_install: boolean;
  platform: string | null;
  note: string;
}

export const getOcrBackendsStatus = async (): Promise<{
  backends: OcrBackendStatus[];
  current_platform: string;
}> => {
  const response = await api.get('/settings/ocr/backends');
  return response.data;
};

export const checkOcrBackend = async (backendId: string): Promise<{
  backend: string;
  installed: boolean;
  available: boolean;
  error: string | null;
  pip_installable: boolean;
  requires_system_install: boolean;
  note: string;
}> => {
  const response = await api.get(`/settings/ocr/backends/${backendId}/check`);
  return response.data;
};

export const installOcrBackend = async (backendId: string): Promise<{
  message: string;
  success: boolean;
  installed?: boolean;
  available?: boolean;
  already_installed?: boolean;
  error?: string;
  requires_system_install?: boolean;
  note?: string;
}> => {
  const response = await api.post(`/settings/ocr/backends/${backendId}/install`);
  return response.data;
};

export const getTableSettings = async (): Promise<TableSettingsResponse> => {
  const response = await api.get('/settings/tables');
  return response.data;
};

export const updateTableSettings = async (
  settings: Partial<{
    enabled: boolean;
    structure_extraction: boolean;
    mode: string;
    do_cell_matching: boolean;
  }>
): Promise<{ message: string; tables: Record<string, unknown> }> => {
  const response = await api.put('/settings/tables', settings);
  return response.data;
};

export const getImageSettings = async (): Promise<ImageSettingsResponse> => {
  const response = await api.get('/settings/images');
  return response.data;
};

export const updateImageSettings = async (
  settings: Partial<{
    extract: boolean;
    classify: boolean;
    generate_page_images: boolean;
    generate_picture_images: boolean;
    generate_table_images: boolean;
    images_scale: number;
  }>
): Promise<{ message: string; images: Record<string, unknown> }> => {
  const response = await api.put('/settings/images', settings);
  return response.data;
};

export const getOutputSettings = async (): Promise<{
  output: { default_format: string };
  available_formats: { id: string; name: string; extension: string; mime_type?: string }[];
}> => {
  const response = await api.get('/settings/output');
  return response.data;
};

export const updateOutputSettings = async (
  settings: { default_format?: string }
): Promise<{ message: string; output: { default_format: string } }> => {
  const response = await api.put('/settings/output', settings);
  return response.data;
};

export const getPerformanceSettings = async (): Promise<PerformanceSettingsResponse> => {
  const response = await api.get('/settings/performance');
  return response.data;
};

export const updatePerformanceSettings = async (
  settings: Partial<{
    device: string;
    num_threads: number;
    document_timeout: number | null;
  }>
): Promise<{ message: string; performance: Record<string, unknown> }> => {
  const response = await api.put('/settings/performance', settings);
  return response.data;
};

export const getChunkingSettings = async (): Promise<ChunkingSettingsResponse> => {
  const response = await api.get('/settings/chunking');
  return response.data;
};

export const updateChunkingSettings = async (
  settings: Partial<{
    enabled: boolean;
    max_tokens: number;
    merge_peers: boolean;
  }>
): Promise<{ message: string; chunking: Record<string, unknown> }> => {
  const response = await api.put('/settings/chunking', settings);
  return response.data;
};

// Enrichment settings
export interface EnrichmentModelStatus {
  model_id: string;
  model_name: string;
  downloaded: boolean;
  available: boolean;
  size_mb: number;
}

export interface EnrichmentSettingsResponse {
  enrichment: {
    code_enrichment: boolean;
    formula_enrichment: boolean;
    picture_classification: boolean;
    picture_description: boolean;
  };
  models_status: Record<string, EnrichmentModelStatus>;
  options: Record<string, {
    description: string;
    default: boolean;
    note?: string;
    model_size_mb?: number;
  }>;
}

export interface EnrichmentModelInfo {
  id: string;
  name: string;
  description: string;
  feature: string;
  model_name: string;
  size_mb: number;
  note: string;
  downloaded: boolean;
  available: boolean;
  error?: string;
  requires_upgrade?: boolean;
  docling_version?: string;
  min_docling_version?: string;
}

export interface EnrichmentModelsResponse {
  models: EnrichmentModelInfo[];
}

export interface ModelDownloadProgress {
  model_id: string;
  status: 'idle' | 'downloading' | 'completed' | 'error';
  progress: number;
  message: string;
}

export const getEnrichmentSettings = async (): Promise<EnrichmentSettingsResponse> => {
  const response = await api.get('/settings/enrichment');
  return response.data;
};

export const updateEnrichmentSettings = async (
  settings: Partial<{
    code_enrichment: boolean;
    formula_enrichment: boolean;
    picture_classification: boolean;
    picture_description: boolean;
  }>
): Promise<{ message: string; enrichment: Record<string, unknown> }> => {
  const response = await api.put('/settings/enrichment', settings);
  return response.data;
};

// Enrichment models
export const getEnrichmentModelsStatus = async (): Promise<EnrichmentModelsResponse> => {
  const response = await api.get('/settings/enrichment/models');
  return response.data;
};

export const getEnrichmentModelStatus = async (modelId: string): Promise<EnrichmentModelInfo & { download_progress: ModelDownloadProgress }> => {
  const response = await api.get(`/settings/enrichment/models/${modelId}/status`);
  return response.data;
};

export const downloadEnrichmentModel = async (modelId: string): Promise<{ success: boolean; message: string; model_id: string; already_downloaded?: boolean; error?: string }> => {
  const response = await api.post(`/settings/enrichment/models/${modelId}/download`);
  return response.data;
};

export const getModelDownloadProgress = async (modelId: string): Promise<ModelDownloadProgress> => {
  const response = await api.get(`/settings/enrichment/models/${modelId}/progress`);
  return response.data;
};

// History
export const getHistory = async (
  limit?: number,
  offset?: number,
  status?: string
): Promise<HistoryResponse> => {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit.toString());
  if (offset) params.append('offset', offset.toString());
  if (status) params.append('status', status);

  const response = await api.get(`/history?${params.toString()}`);
  return response.data;
};

export const getRecentHistory = async (limit?: number): Promise<{ entries: HistoryEntry[]; count: number }> => {
  const params = limit ? `?limit=${limit}` : '';
  const response = await api.get(`/history/recent${params}`);
  return response.data;
};

export const getHistoryEntry = async (jobId: string): Promise<HistoryEntry> => {
  const response = await api.get(`/history/${jobId}`);
  return response.data;
};

export const deleteHistoryEntry = async (jobId: string): Promise<void> => {
  await api.delete(`/history/${jobId}`);
};

export const clearHistory = async (): Promise<{ message: string; deleted_count: number }> => {
  const response = await api.delete('/history');
  return response.data;
};

export const getHistoryStats = async (): Promise<HistoryStats> => {
  const response = await api.get('/history/stats');
  return response.data;
};

export const searchHistory = async (
  query: string,
  limit?: number
): Promise<{ entries: HistoryEntry[]; count: number; query: string }> => {
  const params = new URLSearchParams({ q: query });
  if (limit) params.append('limit', limit.toString());

  const response = await api.get(`/history/search?${params.toString()}`);
  return response.data;
};

export const cleanupHistory = async (
  days?: number,
  maxAgeHours?: number
): Promise<{
  message: string;
  results: {
    history_entries_deleted: number;
    upload_files_deleted: number;
    output_folders_deleted: number;
  };
}> => {
  const response = await api.post('/history/cleanup', {
    days,
    max_age_hours: maxAgeHours,
  });
  return response.data;
};

export const exportHistory = async (): Promise<{
  exported_at: string;
  total_entries: number;
  statistics: HistoryStats['conversions'];
  entries: HistoryEntry[];
}> => {
  const response = await api.get('/history/export');
  return response.data;
};

export default api;


import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getSettings,
  updateSettings,
  resetSettings,
  getOcrSettings,
  updateOcrSettings,
  getTableSettings,
  updateTableSettings,
  getImageSettings,
  updateImageSettings,
  getOutputSettings,
  updateOutputSettings,
  getPerformanceSettings,
  updatePerformanceSettings,
  getChunkingSettings,
  updateChunkingSettings,
  getEnrichmentSettings,
  updateEnrichmentSettings,
  getFormats,
  getOcrBackendsStatus,
  installOcrBackend,
  getEnrichmentModelsStatus,
  downloadEnrichmentModel,
  type OcrBackendStatus,
  type EnrichmentModelInfo,
  type ModelDownloadProgress,
} from '../services/api';
// ConversionSettings type is used in the settings API responses

// Main settings hook
export function useSettings() {
  const queryClient = useQueryClient();

  const settingsQuery = useQuery({
    queryKey: ['settings'],
    queryFn: getSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  const resetMutation = useMutation({
    mutationFn: resetSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    settings: settingsQuery.data?.settings,
    defaults: settingsQuery.data?.defaults,
    isLoading: settingsQuery.isLoading,
    error: settingsQuery.error,
    updateSettings: updateMutation.mutate,
    resetSettings: resetMutation.mutate,
    isUpdating: updateMutation.isPending,
    isResetting: resetMutation.isPending,
  };
}

// OCR settings hook
export function useOcrSettings() {
  const queryClient = useQueryClient();
  const [installError, setInstallError] = useState<string | null>(null);

  const ocrQuery = useQuery({
    queryKey: ['settings', 'ocr'],
    queryFn: getOcrSettings,
  });

  const backendsQuery = useQuery({
    queryKey: ['settings', 'ocr', 'backends'],
    queryFn: getOcrBackendsStatus,
  });

  const updateMutation = useMutation({
    mutationFn: ({ settings, autoInstall }: { settings: Parameters<typeof updateOcrSettings>[0]; autoInstall?: boolean }) =>
      updateOcrSettings(settings, autoInstall),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['settings', 'ocr', 'backends'] });
      setInstallError(null);
    },
    onError: (error: unknown) => {
      // Check if it's a backend not installed error
      const axiosError = error as { response?: { data?: { pip_installable?: boolean; error?: string } } };
      if (axiosError.response?.data?.pip_installable) {
        setInstallError(axiosError.response.data.error || 'Installation error');
      }
    },
  });

  const installMutation = useMutation({
    mutationFn: installOcrBackend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'ocr', 'backends'] });
      setInstallError(null);
    },
  });

  // Enhanced updateOcr that can auto-install
  const updateOcr = (settings: Parameters<typeof updateOcrSettings>[0], autoInstall = false) => {
    updateMutation.mutate({ settings, autoInstall });
  };

  return {
    ocr: ocrQuery.data?.ocr,
    availableLanguages: ocrQuery.data?.available_languages || [],
    availableBackends: ocrQuery.data?.available_backends || [],
    backendsStatus: backendsQuery.data?.backends || [] as OcrBackendStatus[],
    currentPlatform: backendsQuery.data?.current_platform || '',
    options: ocrQuery.data?.options || {},
    isLoading: ocrQuery.isLoading || backendsQuery.isLoading,
    error: ocrQuery.error,
    updateOcr,
    isUpdating: updateMutation.isPending,
    installBackend: installMutation.mutate,
    isInstalling: installMutation.isPending,
    installError,
    clearInstallError: () => setInstallError(null),
  };
}

// Table settings hook
export function useTableSettings() {
  const queryClient = useQueryClient();

  const tableQuery = useQuery({
    queryKey: ['settings', 'tables'],
    queryFn: getTableSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateTableSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    tables: tableQuery.data?.tables,
    availableModes: tableQuery.data?.available_modes || [],
    options: tableQuery.data?.options || {},
    isLoading: tableQuery.isLoading,
    error: tableQuery.error,
    updateTables: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}

// Image settings hook
export function useImageSettings() {
  const queryClient = useQueryClient();

  const imageQuery = useQuery({
    queryKey: ['settings', 'images'],
    queryFn: getImageSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateImageSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    images: imageQuery.data?.images,
    options: imageQuery.data?.options || {},
    isLoading: imageQuery.isLoading,
    error: imageQuery.error,
    updateImages: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}

// Output settings hook
export function useOutputSettings() {
  const queryClient = useQueryClient();

  const outputQuery = useQuery({
    queryKey: ['settings', 'output'],
    queryFn: getOutputSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateOutputSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    output: outputQuery.data?.output,
    availableFormats: outputQuery.data?.available_formats || [],
    isLoading: outputQuery.isLoading,
    error: outputQuery.error,
    updateOutput: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}

// Performance settings hook
export function usePerformanceSettings() {
  const queryClient = useQueryClient();

  const perfQuery = useQuery({
    queryKey: ['settings', 'performance'],
    queryFn: getPerformanceSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updatePerformanceSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    performance: perfQuery.data?.performance,
    availableDevices: perfQuery.data?.available_devices || [],
    options: perfQuery.data?.options || {},
    isLoading: perfQuery.isLoading,
    error: perfQuery.error,
    updatePerformance: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}

// Chunking settings hook
export function useChunkingSettings() {
  const queryClient = useQueryClient();

  const chunkingQuery = useQuery({
    queryKey: ['settings', 'chunking'],
    queryFn: getChunkingSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateChunkingSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    chunking: chunkingQuery.data?.chunking,
    options: chunkingQuery.data?.options || {},
    isLoading: chunkingQuery.isLoading,
    error: chunkingQuery.error,
    updateChunking: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}

// Enrichment settings hook
export function useEnrichmentSettings() {
  const queryClient = useQueryClient();
  const [downloadingModels, setDownloadingModels] = useState<Record<string, boolean>>({});
  const [downloadProgress, setDownloadProgress] = useState<Record<string, ModelDownloadProgress>>({});

  const enrichmentQuery = useQuery({
    queryKey: ['settings', 'enrichment'],
    queryFn: getEnrichmentSettings,
  });

  const modelsQuery = useQuery({
    queryKey: ['settings', 'enrichment', 'models'],
    queryFn: getEnrichmentModelsStatus,
  });

  const updateMutation = useMutation({
    mutationFn: updateEnrichmentSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  const downloadModelMutation = useMutation({
    mutationFn: async (modelId: string) => {
      setDownloadingModels(prev => ({ ...prev, [modelId]: true }));
      setDownloadProgress(prev => ({
        ...prev,
        [modelId]: { model_id: modelId, status: 'downloading', progress: 0, message: 'Starting download...' }
      }));

      try {
        const result = await downloadEnrichmentModel(modelId);

        // Update progress based on result
        if (result.success) {
          setDownloadProgress(prev => ({
            ...prev,
            [modelId]: { model_id: modelId, status: 'completed', progress: 100, message: result.message || 'Download complete!' }
          }));
        } else {
          setDownloadProgress(prev => ({
            ...prev,
            [modelId]: { model_id: modelId, status: 'error', progress: 0, message: result.error || 'Download failed' }
          }));
        }

        return result;
      } catch (error) {
        setDownloadProgress(prev => ({
          ...prev,
          [modelId]: { model_id: modelId, status: 'error', progress: 0, message: String(error) }
        }));
        throw error;
      } finally {
        // Small delay before clearing the loading state so user sees the result
        setTimeout(() => {
          setDownloadingModels(prev => ({ ...prev, [modelId]: false }));
        }, 1500);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'enrichment'] });
      queryClient.invalidateQueries({ queryKey: ['settings', 'enrichment', 'models'] });
    },
    onError: (error, modelId) => {
      console.error('Download failed:', modelId, error);
      setDownloadProgress(prev => ({
        ...prev,
        [modelId]: { model_id: modelId, status: 'error', progress: 0, message: String(error) }
      }));
    },
  });

  return {
    enrichment: enrichmentQuery.data?.enrichment,
    modelsStatus: enrichmentQuery.data?.models_status || {},
    options: enrichmentQuery.data?.options || {},
    models: modelsQuery.data?.models || [] as EnrichmentModelInfo[],
    isLoading: enrichmentQuery.isLoading,
    isLoadingModels: modelsQuery.isLoading,
    error: enrichmentQuery.error,
    updateEnrichment: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
    downloadModel: downloadModelMutation.mutate,
    downloadingModels,
    downloadProgress,
    downloadError: downloadModelMutation.error,
  };
}

// Formats hook
export function useFormats() {
  const formatsQuery = useQuery({
    queryKey: ['formats'],
    queryFn: getFormats,
  });

  return {
    inputFormats: formatsQuery.data?.input_formats || [],
    outputFormats: formatsQuery.data?.output_formats || [],
    isLoading: formatsQuery.isLoading,
    error: formatsQuery.error,
  };
}

// Combined hook for all settings
export function useAllSettings() {
  const settings = useSettings();
  const ocr = useOcrSettings();
  const tables = useTableSettings();
  const images = useImageSettings();
  const enrichment = useEnrichmentSettings();
  const output = useOutputSettings();
  const performance = usePerformanceSettings();
  const chunking = useChunkingSettings();

  return {
    settings,
    ocr,
    tables,
    images,
    enrichment,
    output,
    performance,
    chunking,
    isLoading:
      settings.isLoading ||
      ocr.isLoading ||
      tables.isLoading ||
      images.isLoading ||
      enrichment.isLoading ||
      output.isLoading ||
      performance.isLoading ||
      chunking.isLoading,
  };
}


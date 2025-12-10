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
  getFormats,
} from '../services/api';
import type { ConversionSettings } from '../types';

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

  const ocrQuery = useQuery({
    queryKey: ['settings', 'ocr'],
    queryFn: getOcrSettings,
  });

  const updateMutation = useMutation({
    mutationFn: updateOcrSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  return {
    ocr: ocrQuery.data?.ocr,
    availableLanguages: ocrQuery.data?.available_languages || [],
    availableBackends: ocrQuery.data?.available_backends || [],
    options: ocrQuery.data?.options || {},
    isLoading: ocrQuery.isLoading,
    error: ocrQuery.error,
    updateOcr: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
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
  const output = useOutputSettings();
  const performance = usePerformanceSettings();
  const chunking = useChunkingSettings();

  return {
    settings,
    ocr,
    tables,
    images,
    output,
    performance,
    chunking,
    isLoading:
      settings.isLoading ||
      ocr.isLoading ||
      tables.isLoading ||
      images.isLoading ||
      output.isLoading ||
      performance.isLoading ||
      chunking.isLoading,
  };
}


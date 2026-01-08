import { useState, useCallback, useEffect, useRef } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  uploadAndConvert,
  uploadAndConvertBatch,
  getConversionStatus,
  getConversionResult,
  downloadExport,
  getExportContent,
} from '../services/api';
import type {
  ConversionJob,
  ConversionStatus,
  ConversionResult,
  ConversionSettings,
  AppState,
  BatchJob,
} from '../types';

interface UseConversionOptions {
  onComplete?: (result: ConversionResult) => void;
  onError?: (error: string) => void;
  pollInterval?: number;
}

interface BatchJobStatus {
  job: BatchJob;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'rejected';
  progress: number;
  result?: ConversionResult;
  error?: string;
}

export function useConversion(options: UseConversionOptions = {}) {
  const { onComplete, onError, pollInterval = 1000 } = options;

  const [state, setState] = useState<AppState>('idle');
  const [currentJob, setCurrentJob] = useState<ConversionJob | null>(null);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  // Batch processing state
  const [batchJobs, setBatchJobs] = useState<BatchJobStatus[]>([]);
  const [batchMode, setBatchMode] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ completed: 0, total: 0 });

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const batchPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Upload mutation (single file)
  const uploadMutation = useMutation({
    mutationFn: async ({
      file,
      settings,
    }: {
      file: File;
      settings?: Partial<ConversionSettings>;
    }) => {
      return uploadAndConvert(file, settings);
    },
    onSuccess: (data) => {
      setCurrentJob(data);
      setState('processing');
      setProgress(0);
      setStatusMessage('Starting conversion...');
      startPolling(data.job_id);
    },
    onError: (err: Error) => {
      setError(err.message);
      setState('error');
      onError?.(err.message);
    },
  });

  // Batch upload mutation
  const batchUploadMutation = useMutation({
    mutationFn: async ({
      files,
      settings,
    }: {
      files: File[];
      settings?: Partial<ConversionSettings>;
    }) => {
      return uploadAndConvertBatch(files, settings);
    },
    onSuccess: (data) => {
      // Initialize batch job statuses
      const initialStatuses: BatchJobStatus[] = data.jobs.map((job) => ({
        job,
        status: job.status === 'rejected' ? 'rejected' : 'processing',
        progress: job.status === 'rejected' ? 0 : 10,
        error: job.error,
      }));

      setBatchJobs(initialStatuses);
      setBatchProgress({ completed: 0, total: data.jobs.filter(j => j.status !== 'rejected').length });
      setState('processing');
      setStatusMessage(`Processing ${data.jobs.length} files...`);

      // Start polling for each job
      startBatchPolling(initialStatuses);
    },
    onError: (err: Error) => {
      setError(err.message);
      setState('error');
      onError?.(err.message);
    },
  });

  // Status polling for single job
  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const status = await getConversionStatus(jobId);
      setProgress(status.progress);
      setStatusMessage(status.message);

      if (status.status === 'completed') {
        stopPolling();
        const fullResult = await getConversionResult(jobId);
        setResult(fullResult);
        setState('complete');
        onComplete?.(fullResult);
      } else if (status.status === 'failed') {
        stopPolling();
        setError(status.error || 'Conversion failed');
        setState('error');
        onError?.(status.error || 'Conversion failed');
      }
    } catch (err) {
      // Continue polling even if one request fails
      console.error('Status poll error:', err);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- stopPolling is intentionally excluded to avoid infinite re-renders
  }, [onComplete, onError]);

  // Batch polling
  const pollBatchStatus = useCallback(async (jobs: BatchJobStatus[]) => {
    const updatedJobs = await Promise.all(
      jobs.map(async (jobStatus) => {
        // Skip rejected or already completed/failed jobs
        if (jobStatus.status === 'rejected' || jobStatus.status === 'completed' || jobStatus.status === 'failed') {
          return jobStatus;
        }

        if (!jobStatus.job.job_id) {
          return { ...jobStatus, status: 'failed' as const, error: 'No job ID' };
        }

        try {
          const status = await getConversionStatus(jobStatus.job.job_id);

          if (status.status === 'completed') {
            const fullResult = await getConversionResult(jobStatus.job.job_id);
            return {
              ...jobStatus,
              status: 'completed' as const,
              progress: 100,
              result: fullResult,
            };
          } else if (status.status === 'failed') {
            return {
              ...jobStatus,
              status: 'failed' as const,
              progress: 0,
              error: status.error || 'Conversion failed',
            };
          } else {
            return {
              ...jobStatus,
              status: 'processing' as const,
              progress: status.progress,
            };
          }
        } catch (err) {
          console.error('Batch poll error for job:', jobStatus.job.job_id, err);
          return jobStatus;
        }
      })
    );

    setBatchJobs(updatedJobs);

    // Calculate overall progress
    const completed = updatedJobs.filter(j => j.status === 'completed' || j.status === 'failed').length;
    const total = updatedJobs.filter(j => j.status !== 'rejected').length;
    const avgProgress = updatedJobs.reduce((sum, j) => sum + j.progress, 0) / Math.max(updatedJobs.length, 1);

    setBatchProgress({ completed, total });
    setProgress(avgProgress);
    setStatusMessage(`Processed ${completed}/${total} files`);

    // Check if all jobs are done
    const allDone = updatedJobs.every(j =>
      j.status === 'completed' || j.status === 'failed' || j.status === 'rejected'
    );

    if (allDone) {
      stopBatchPolling();

      const successfulJobs = updatedJobs.filter(j => j.status === 'completed');
      const failedJobs = updatedJobs.filter(j => j.status === 'failed');

      if (successfulJobs.length > 0) {
        // Set the first successful result as the main result for viewing
        setResult(successfulJobs[0].result || null);
        setState('complete');
        setStatusMessage(`Completed: ${successfulJobs.length} succeeded, ${failedJobs.length} failed`);
      } else {
        setState('error');
        setError(`All ${failedJobs.length} conversions failed`);
      }
    }

    return updatedJobs;
  // eslint-disable-next-line react-hooks/exhaustive-deps -- stopBatchPolling is intentionally excluded to avoid infinite re-renders
  }, []);

  const startPolling = useCallback(
    (jobId: string) => {
      stopPolling();
      pollIntervalRef.current = setInterval(() => {
        pollStatus(jobId);
      }, pollInterval);
      // Initial poll
      pollStatus(jobId);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stopPolling is intentionally excluded to avoid infinite re-renders
    [pollStatus, pollInterval]
  );

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const startBatchPolling = useCallback(
    (initialJobs: BatchJobStatus[]) => {
      stopBatchPolling();
      let currentJobs = initialJobs;

      batchPollRef.current = setInterval(async () => {
        currentJobs = await pollBatchStatus(currentJobs);
      }, pollInterval);

      // Initial poll
      pollBatchStatus(initialJobs);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stopBatchPolling is intentionally excluded to avoid infinite re-renders
    [pollBatchStatus, pollInterval]
  );

  const stopBatchPolling = useCallback(() => {
    if (batchPollRef.current) {
      clearInterval(batchPollRef.current);
      batchPollRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
      stopBatchPolling();
    };
  }, [stopPolling, stopBatchPolling]);

  // Upload single file or start tracking an existing job (for URL conversions)
  const uploadFile = useCallback(
    (file: File, existingJobId?: string, settings?: Partial<ConversionSettings>) => {
      setBatchMode(false);
      setError(null);
      setResult(null);
      setBatchJobs([]);

      if (existingJobId) {
        // URL conversion - job already started, just poll for status
        setCurrentJob({
          job_id: existingJobId,
          filename: file.name || 'url-document',
          input_format: 'unknown',
          status: 'processing',
          message: 'Processing URL...'
        });
        setState('processing');
        setProgress(0);
        setStatusMessage('Processing document from URL...');
        startPolling(existingJobId);
      } else {
        // Regular file upload
        setState('uploading');
        uploadMutation.mutate({ file, settings });
      }
    },
    [uploadMutation, startPolling]
  );

  // Upload multiple files
  const uploadFiles = useCallback(
    (files: File[], settings?: Partial<ConversionSettings>) => {
      if (files.length === 0) return;

      if (files.length === 1) {
        // Single file, use regular upload
        uploadFile(files[0], undefined, settings);
        return;
      }

      setBatchMode(true);
      setState('uploading');
      setError(null);
      setResult(null);
      setBatchJobs([]);
      setStatusMessage(`Uploading ${files.length} files...`);
      batchUploadMutation.mutate({ files, settings });
    },
    [uploadFile, batchUploadMutation]
  );

  // Download export
  const downloadFormat = useCallback(
    async (format: string) => {
      if (!currentJob && !result) return;

      const jobId = result?.job_id || currentJob?.job_id;
      if (!jobId) return;

      try {
        const blob = await downloadExport(jobId, format);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = currentJob?.filename || 'document';
        a.download = `${filename.replace(/\.[^/.]+$/, '')}.${getExtension(format)}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        console.error('Download error:', err);
      }
    },
    [currentJob, result]
  );

  // Get content for preview
  const getContent = useCallback(
    async (format: string) => {
      if (!currentJob) return null;

      try {
        const response = await getExportContent(currentJob.job_id, format);
        return response.content;
      } catch (err) {
        console.error('Get content error:', err);
        return null;
      }
    },
    [currentJob]
  );

  // Reset state
  const reset = useCallback(() => {
    stopPolling();
    stopBatchPolling();
    setState('idle');
    setCurrentJob(null);
    setResult(null);
    setError(null);
    setProgress(0);
    setStatusMessage('');
    setBatchJobs([]);
    setBatchMode(false);
    setBatchProgress({ completed: 0, total: 0 });
  }, [stopPolling, stopBatchPolling]);

  // Select a batch job result to view
  const selectBatchResult = useCallback((index: number) => {
    const job = batchJobs[index];
    if (job?.result) {
      setResult(job.result);
    }
  }, [batchJobs]);

  return {
    state,
    currentJob,
    result,
    error,
    progress,
    statusMessage,
    isUploading: uploadMutation.isPending || batchUploadMutation.isPending,
    uploadFile,
    uploadFiles,
    downloadFormat,
    getContent,
    reset,
    // Batch-specific
    batchMode,
    batchJobs,
    batchProgress,
    selectBatchResult,
  };
}

function getExtension(format: string): string {
  const extensions: Record<string, string> = {
    markdown: 'md',
    html: 'html',
    json: 'json',
    doctags: 'doctags',
    text: 'txt',
    document_tokens: 'tokens.json',
    chunks: 'chunks.json',
  };
  return extensions[format] || format;
}

// Hook for fetching conversion status
export function useConversionStatus(jobId: string | null, enabled = true) {
  return useQuery({
    queryKey: ['conversionStatus', jobId],
    queryFn: () => (jobId ? getConversionStatus(jobId) : null),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      const data = query.state.data as ConversionStatus | null;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 1000;
    },
  });
}


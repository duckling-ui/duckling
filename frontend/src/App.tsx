import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConversion } from './hooks/useConversion';
import DropZone from './components/DropZone';
import ConversionProgress from './components/ConversionProgress';
import ExportOptions from './components/ExportOptions';
import SettingsPanel from './components/SettingsPanel';
import HistoryPanel from './components/HistoryPanel';
import DocsPanel from './components/DocsPanel';
import type { HistoryEntry, ConversionResult } from './types';

export default function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [docsOpen, setDocsOpen] = useState(false);
  const [batchModeEnabled, setBatchModeEnabled] = useState(false);

  const {
    state,
    currentJob,
    result,
    error,
    progress,
    statusMessage,
    isUploading,
    uploadFile,
    uploadFiles,
    downloadFormat,
    reset,
    batchMode,
    batchJobs,
    batchProgress,
    selectBatchResult,
  } = useConversion({
    onComplete: (result: ConversionResult) => {
      console.log('Conversion complete:', result);
    },
    onError: (error: string) => {
      console.error('Conversion error:', error);
    },
  });

  const handleFileAccepted = useCallback(
    (file: File) => {
      uploadFile(file);
    },
    [uploadFile]
  );

  const handleFilesAccepted = useCallback(
    (files: File[]) => {
      uploadFiles(files);
    },
    [uploadFiles]
  );

  const handleHistorySelect = useCallback(
    (entry: HistoryEntry) => {
      setHistoryOpen(false);
      console.log('Selected history entry:', entry);
    },
    []
  );

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-dark-950/80 backdrop-blur-xl border-b border-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-dark-950" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 2a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6H6zm7 1.5L18.5 9H13V3.5zM8 12h8v2H8v-2zm0 4h8v2H8v-2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-dark-100">Duckling</h1>
                <p className="text-xs text-dark-500">Document Conversion</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              {/* Batch mode toggle */}
              <button
                onClick={() => setBatchModeEnabled(!batchModeEnabled)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  batchModeEnabled
                    ? 'bg-primary-500 text-dark-950'
                    : 'bg-dark-800 text-dark-400 hover:text-dark-200'
                }`}
                title="Toggle batch mode for multiple file uploads"
              >
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                  </svg>
                  Batch
                </span>
              </button>
              <button
                onClick={() => setDocsOpen(true)}
                className="p-2.5 hover:bg-dark-800 rounded-lg transition-colors group"
                title="Documentation"
              >
                <svg
                  className="w-5 h-5 text-dark-400 group-hover:text-dark-200"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
                  />
                </svg>
              </button>
              <button
                onClick={() => setHistoryOpen(true)}
                className="p-2.5 hover:bg-dark-800 rounded-lg transition-colors group"
                title="History"
              >
                <svg
                  className="w-5 h-5 text-dark-400 group-hover:text-dark-200"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </button>
              <button
                onClick={() => setSettingsOpen(true)}
                className="p-2.5 hover:bg-dark-800 rounded-lg transition-colors group"
                title="Settings"
              >
                <svg
                  className="w-5 h-5 text-dark-400 group-hover:text-dark-200"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"
                  />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-5xl">
          <AnimatePresence mode="wait">
            {/* Idle state - show dropzone */}
            {state === 'idle' && (
              <motion.div
                key="idle"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-8"
              >
                <div className="text-center">
                  <motion.h2
                    className="text-3xl sm:text-4xl font-bold text-dark-100 mb-3"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    Convert Any Document
                  </motion.h2>
                  <motion.p
                    className="text-dark-400 text-lg max-w-xl mx-auto"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    Transform PDFs, Word documents, presentations, images, and more into
                    structured formats ready for AI processing.
                  </motion.p>
                </div>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <DropZone
                    onFileAccepted={handleFileAccepted}
                    onFilesAccepted={handleFilesAccepted}
                    isUploading={isUploading}
                    multiple={batchModeEnabled}
                  />
                </motion.div>

                {/* Feature highlights */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8"
                >
                  {[
                    { icon: '👁️', label: 'OCR', desc: 'Extract text from images' },
                    { icon: '📊', label: 'Tables', desc: 'Export to CSV' },
                    { icon: '🖼️', label: 'Images', desc: 'Extract figures' },
                    { icon: '🧩', label: 'RAG', desc: 'Document chunks' },
                  ].map((feature) => (
                    <div
                      key={feature.label}
                      className="glass rounded-xl p-4 text-center"
                    >
                      <span className="text-2xl">{feature.icon}</span>
                      <p className="font-medium text-dark-200 mt-2">{feature.label}</p>
                      <p className="text-xs text-dark-500">{feature.desc}</p>
                    </div>
                  ))}
                </motion.div>
              </motion.div>
            )}

            {/* Uploading state */}
            {state === 'uploading' && (
              <motion.div
                key="uploading"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ConversionProgress
                  progress={5}
                  message={batchModeEnabled ? `Uploading files...` : "Uploading file..."}
                  filename={currentJob?.filename}
                />
              </motion.div>
            )}

            {/* Processing state */}
            {state === 'processing' && (
              <motion.div
                key="processing"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {batchMode && batchJobs.length > 0 ? (
                  <BatchProgress
                    jobs={batchJobs}
                    progress={progress}
                    batchProgress={batchProgress}
                    statusMessage={statusMessage}
                  />
                ) : (
                  <ConversionProgress
                    progress={progress}
                    message={statusMessage}
                    filename={currentJob?.filename}
                  />
                )}
              </motion.div>
            )}

            {/* Complete state */}
            {state === 'complete' && result && (
              <motion.div
                key="complete"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {batchMode && batchJobs.length > 1 ? (
                  <BatchResults
                    jobs={batchJobs}
                    selectedResult={result}
                    onSelectResult={selectBatchResult}
                    onDownload={downloadFormat}
                    onNewConversion={reset}
                  />
                ) : (
                  <ExportOptions
                    jobId={result.job_id}
                    formatsAvailable={result.formats_available || result.result?.formats_available || ['markdown']}
                    preview={result.result?.markdown_preview}
                    onDownload={downloadFormat}
                    onNewConversion={reset}
                    confidence={result.confidence}
                    imagesCount={result.images_count || result.result?.images_count || 0}
                    tablesCount={result.tables_count || result.result?.tables_count || 0}
                    chunksCount={result.chunks_count || result.result?.chunks_count || 0}
                  />
                )}
              </motion.div>
            )}

            {/* Error state */}
            {state === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="text-center"
              >
                <div className="glass rounded-2xl p-8 max-w-md mx-auto">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                    <svg
                      className="w-8 h-8 text-red-400"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-dark-100 mb-2">Conversion Failed</h3>
                  <p className="text-dark-400 mb-6">{error || 'An unexpected error occurred'}</p>
                  <button
                    onClick={reset}
                    className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-dark-950 font-semibold rounded-xl transition-colors duration-200"
                  >
                    Try Again
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-dark-500 text-sm">
        <p>
          Powered by{' '}
          <a
            href="https://github.com/docling-project/docling"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-400 hover:text-primary-300 transition-colors"
          >
            Docling
          </a>
        </p>
      </footer>

      {/* Panels */}
      <SettingsPanel isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <HistoryPanel
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelectEntry={handleHistorySelect}
      />
      <DocsPanel isOpen={docsOpen} onClose={() => setDocsOpen(false)} />
    </div>
  );
}

// Batch Progress Component
interface BatchProgressProps {
  jobs: Array<{
    job: { filename: string; job_id?: string };
    status: string;
    progress: number;
    error?: string;
  }>;
  progress: number;
  batchProgress: { completed: number; total: number };
  statusMessage: string;
}

function BatchProgress({ jobs, progress, batchProgress, statusMessage }: BatchProgressProps) {
  return (
    <div className="glass rounded-2xl p-8 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold text-dark-100 mb-2">Processing Files</h3>
        <p className="text-dark-400">{statusMessage}</p>
      </div>

      {/* Overall progress */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-dark-400 mb-2">
          <span>Overall Progress</span>
          <span>{batchProgress.completed}/{batchProgress.total} files</span>
        </div>
        <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary-500 to-primary-400"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Individual file progress */}
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {jobs.map((job, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg ${
              job.status === 'completed' ? 'bg-green-500/10' :
              job.status === 'failed' || job.status === 'rejected' ? 'bg-red-500/10' :
              'bg-dark-800/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                job.status === 'completed' ? 'bg-green-500' :
                job.status === 'failed' || job.status === 'rejected' ? 'bg-red-500' :
                'bg-dark-600'
              }`}>
                {job.status === 'completed' ? (
                  <svg className="w-4 h-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : job.status === 'failed' || job.status === 'rejected' ? (
                  <svg className="w-4 h-4 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <div className="w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-dark-200 truncate">{job.job.filename}</p>
                {job.error && (
                  <p className="text-xs text-red-400 truncate">{job.error}</p>
                )}
              </div>
              <span className="text-xs text-dark-500">{job.progress}%</span>
            </div>
            {job.status === 'processing' && (
              <div className="mt-2 h-1 bg-dark-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-primary-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${job.progress}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Batch Results Component
interface BatchResultsProps {
  jobs: Array<{
    job: { filename: string; job_id?: string };
    status: string;
    result?: ConversionResult;
    error?: string;
  }>;
  selectedResult: ConversionResult;
  onSelectResult: (index: number) => void;
  onDownload: (format: string) => void;
  onNewConversion: () => void;
}

function BatchResults({ jobs, selectedResult, onSelectResult, onDownload, onNewConversion }: BatchResultsProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleSelect = (index: number) => {
    setSelectedIndex(index);
    onSelectResult(index);
  };

  const successfulJobs = jobs.filter(j => j.status === 'completed');
  const failedJobs = jobs.filter(j => j.status === 'failed' || j.status === 'rejected');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto"
    >
      {/* Summary header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-500/20 flex items-center justify-center"
        >
          <svg
            className="w-8 h-8 text-primary-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </motion.div>
        <h2 className="text-2xl font-bold text-dark-100 mb-2">Batch Conversion Complete!</h2>
        <p className="text-dark-400">
          <span className="text-green-400">{successfulJobs.length} succeeded</span>
          {failedJobs.length > 0 && (
            <>, <span className="text-red-400">{failedJobs.length} failed</span></>
          )}
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* File list */}
        <div className="glass rounded-2xl p-4">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Converted Files</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {jobs.map((job, index) => (
              <button
                key={index}
                onClick={() => job.status === 'completed' && handleSelect(index)}
                disabled={job.status !== 'completed'}
                className={`w-full p-3 rounded-lg text-left transition-colors ${
                  job.status === 'completed'
                    ? selectedIndex === index
                      ? 'bg-primary-500/20 border border-primary-500/50'
                      : 'bg-dark-800/50 hover:bg-dark-700/50'
                    : 'bg-dark-800/30 opacity-50 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {job.status === 'completed' ? (
                      <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-dark-200 truncate">{job.job.filename}</p>
                    {job.error && (
                      <p className="text-xs text-red-400 truncate">{job.error}</p>
                    )}
                    {job.result?.confidence && (
                      <p className="text-xs text-dark-500">
                        Confidence: {(job.result.confidence * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Selected file details */}
        <div className="lg:col-span-2 glass rounded-2xl p-6">
          {selectedResult ? (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">
                {jobs[selectedIndex]?.job.filename}
              </h3>

              {/* Export formats */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-6">
                {(selectedResult.formats_available || []).map((format) => (
                  <button
                    key={format}
                    onClick={() => onDownload(format)}
                    className="p-3 bg-dark-800/50 hover:bg-dark-700/50 rounded-lg text-sm font-medium text-dark-200 transition-colors flex items-center gap-2"
                  >
                    <svg className="w-4 h-4 text-dark-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    {format.toUpperCase()}
                  </button>
                ))}
              </div>

              {/* Preview */}
              {selectedResult.result?.markdown_preview && (
                <div className="bg-dark-950 rounded-xl p-4 max-h-64 overflow-y-auto">
                  <pre className="text-sm text-dark-300 font-mono whitespace-pre-wrap break-words">
                    {selectedResult.result.markdown_preview.slice(0, 1000)}
                    {selectedResult.result.markdown_preview.length > 1000 && '...'}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 text-dark-500">
              Select a file to view details
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={onNewConversion}
          className="px-6 py-3 bg-dark-800 hover:bg-dark-700 text-dark-200 font-medium rounded-xl transition-colors"
        >
          Convert More Documents
        </button>
      </div>
    </motion.div>
  );
}


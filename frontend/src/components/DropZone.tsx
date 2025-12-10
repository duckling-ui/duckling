import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';

interface DropZoneProps {
  onFileAccepted: (file: File) => void;
  onFilesAccepted?: (files: File[]) => void;
  isUploading: boolean;
  disabled?: boolean;
  multiple?: boolean;
}

// Supported file extensions
const ACCEPTED_EXTENSIONS = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'text/html': ['.html', '.htm'],
  'text/markdown': ['.md', '.markdown'],
  'text/csv': ['.csv'],
  'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.gif', '.webp', '.bmp'],
  'audio/*': ['.wav', '.mp3'],
  'text/vtt': ['.vtt'],
  'application/xml': ['.xml'],
  'text/plain': ['.txt', '.asciidoc', '.adoc'],
};

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

const FORMAT_CATEGORIES = [
  { name: 'Documents', formats: ['PDF', 'DOCX', 'PPTX', 'XLSX'], color: 'primary' },
  { name: 'Web', formats: ['HTML', 'Markdown'], color: 'blue' },
  { name: 'Images', formats: ['PNG', 'JPG', 'TIFF', 'WebP'], color: 'purple' },
  { name: 'Data', formats: ['XML', 'AsciiDoc'], color: 'green' },
];

export default function DropZone({
  onFileAccepted,
  onFilesAccepted,
  isUploading,
  disabled,
  multiple = false
}: DropZoneProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: { file: File; errors: { message: string }[] }[]) => {
      setError(null);

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        const errorMessage = rejection.errors.map((e) => e.message).join(', ');
        setError(errorMessage);
        return;
      }

      if (acceptedFiles.length > 0) {
        if (multiple && onFilesAccepted) {
          onFilesAccepted(acceptedFiles);
        } else {
          onFileAccepted(acceptedFiles[0]);
        }
      }
    },
    [onFileAccepted, onFilesAccepted, multiple]
  );

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_EXTENSIONS,
    maxSize: MAX_FILE_SIZE,
    multiple,
    disabled: disabled || isUploading,
  });

  return (
    <div className="w-full">
      <motion.div
        {...getRootProps()}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed p-12
          transition-all duration-300 cursor-pointer
          ${isDragActive ? 'border-primary-500 bg-primary-500/10' : 'border-dark-600 hover:border-dark-500'}
          ${isDragAccept ? 'border-primary-400 bg-primary-500/15' : ''}
          ${isDragReject ? 'border-red-500 bg-red-500/10' : ''}
          ${disabled || isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        whileHover={!disabled && !isUploading ? { scale: 1.01 } : {}}
        whileTap={!disabled && !isUploading ? { scale: 0.99 } : {}}
      >
        <input {...getInputProps()} />

        {/* Background gradient effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-primary-500/5 pointer-events-none" />

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-center text-center">
          <AnimatePresence mode="wait">
            {isUploading ? (
              <motion.div
                key="uploading"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col items-center"
              >
                <div className="w-16 h-16 mb-4">
                  <svg className="animate-spin w-full h-full text-primary-500" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                </div>
                <p className="text-lg font-medium text-dark-200">Uploading...</p>
              </motion.div>
            ) : isDragActive ? (
              <motion.div
                key="drag-active"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="flex flex-col items-center"
              >
                <div className="w-16 h-16 mb-4 text-primary-400">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"
                    />
                  </svg>
                </div>
                <p className="text-lg font-medium text-primary-400">
                  {isDragReject ? 'File type not supported' : `Drop your file${multiple ? 's' : ''} here`}
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="idle"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col items-center"
              >
                <div className="w-16 h-16 mb-4 text-dark-400">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                  </svg>
                </div>
                <p className="text-lg font-medium text-dark-200 mb-2">
                  Drag and drop your document{multiple ? 's' : ''} here
                </p>
                <p className="text-sm text-dark-400 mb-4">or click to browse</p>

                {/* Format categories */}
                <div className="flex flex-wrap justify-center gap-3 max-w-lg">
                  {FORMAT_CATEGORIES.map((category) => (
                    <div key={category.name} className="flex items-center gap-1.5">
                      <span className="text-xs text-dark-500">{category.name}:</span>
                      <div className="flex gap-1">
                        {category.formats.map((format) => (
                          <span
                            key={format}
                            className="px-1.5 py-0.5 text-xs font-medium bg-dark-800 text-dark-300 rounded"
                          >
                            {format}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {multiple && (
                  <p className="mt-4 text-xs text-primary-400">
                    ✨ Multiple file upload enabled - select or drop multiple files
                  </p>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Animated border glow on drag */}
        {isDragActive && (
          <motion.div
            className="absolute inset-0 rounded-2xl pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              boxShadow: isDragReject
                ? '0 0 30px rgba(239, 68, 68, 0.3)'
                : '0 0 30px rgba(20, 184, 166, 0.3)',
            }}
          />
        )}
      </motion.div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
          >
            <p className="text-sm text-red-400">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* File size info */}
      <p className="mt-3 text-xs text-dark-500 text-center">Maximum file size: 100MB per file</p>
    </div>
  );
}


import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getExtractedImages, getExtractedTables, getDocumentChunks, downloadExtractedImage, downloadTableCsv } from '../services/api';
import type { ExtractedImage, ExtractedTable, DocumentChunk } from '../types';

interface ExportOptionsProps {
  jobId: string;
  formatsAvailable: string[];
  preview?: string;
  onDownload: (format: string) => void;
  onNewConversion: () => void;
  confidence?: number;
  imagesCount?: number;
  tablesCount?: number;
  chunksCount?: number;
}

const FORMAT_INFO: Record<string, { name: string; icon: string; description: string }> = {
  markdown: {
    name: 'Markdown',
    icon: 'M',
    description: 'Formatted text with headers, lists, and links',
  },
  html: {
    name: 'HTML',
    icon: '</>',
    description: 'Web-ready format with full styling',
  },
  json: {
    name: 'JSON',
    icon: '{}',
    description: 'Structured data with document hierarchy',
  },
  doctags: {
    name: 'DocTags',
    icon: '#',
    description: 'Tagged document tokens for AI processing',
  },
  text: {
    name: 'Plain Text',
    icon: 'Aa',
    description: 'Simple text without formatting',
  },
  document_tokens: {
    name: 'Document Tokens',
    icon: '[]',
    description: 'Token-level document representation',
  },
  chunks: {
    name: 'RAG Chunks',
    icon: '◫',
    description: 'Document chunks for RAG applications',
  },
};

type TabType = 'formats' | 'images' | 'tables' | 'chunks';

export default function ExportOptions({
  jobId,
  formatsAvailable,
  preview,
  onDownload,
  onNewConversion,
  confidence,
  imagesCount = 0,
  tablesCount = 0,
  chunksCount = 0,
}: ExportOptionsProps) {
  const [selectedFormat, setSelectedFormat] = useState<string>('markdown');
  const [showPreview, setShowPreview] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('formats');

  // Extracted content state
  const [images, setImages] = useState<ExtractedImage[]>([]);
  const [tables, setTables] = useState<ExtractedTable[]>([]);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loadingContent, setLoadingContent] = useState(false);

  // Load extracted content when tab changes
  useEffect(() => {
    const loadContent = async () => {
      setLoadingContent(true);
      try {
        if (activeTab === 'images' && images.length === 0 && imagesCount > 0) {
          const response = await getExtractedImages(jobId);
          setImages(response.images);
        } else if (activeTab === 'tables' && tables.length === 0 && tablesCount > 0) {
          const response = await getExtractedTables(jobId);
          setTables(response.tables);
        } else if (activeTab === 'chunks' && chunks.length === 0 && chunksCount > 0) {
          const response = await getDocumentChunks(jobId);
          setChunks(response.chunks);
        }
      } catch (error) {
        console.error('Error loading content:', error);
      } finally {
        setLoadingContent(false);
      }
    };
    loadContent();
  }, [activeTab, jobId, images.length, tables.length, chunks.length, imagesCount, tablesCount, chunksCount]);

  const handleDownloadImage = async (imageId: number, filename: string) => {
    try {
      const blob = await downloadExtractedImage(jobId, imageId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  const handleDownloadTableCsv = async (tableId: number) => {
    try {
      const blob = await downloadTableCsv(jobId, tableId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `table_${tableId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading CSV:', error);
    }
  };

  const tabs: { id: TabType; label: string; count?: number }[] = [
    { id: 'formats', label: 'Export Formats' },
    { id: 'images', label: 'Images', count: imagesCount },
    { id: 'tables', label: 'Tables', count: tablesCount },
    { id: 'chunks', label: 'RAG Chunks', count: chunksCount },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto"
    >
      {/* Success header */}
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
        <h2 className="text-2xl font-bold text-dark-100 mb-2">Conversion Complete!</h2>
        <div className="flex items-center justify-center gap-4 text-dark-400">
          {confidence !== undefined && (
            <span>
              Confidence: <span className="text-primary-400 font-medium">{(confidence * 100).toFixed(1)}%</span>
            </span>
          )}
          {imagesCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">{imagesCount}</span> images
            </span>
          )}
          {tablesCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">{tablesCount}</span> tables
            </span>
          )}
          {chunksCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">{chunksCount}</span> chunks
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors
              ${activeTab === tab.id
                ? 'bg-primary-500 text-dark-950'
                : 'bg-dark-800 text-dark-300 hover:bg-dark-700'
              }
            `}
          >
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span className={`ml-2 px-1.5 py-0.5 rounded text-xs ${
                activeTab === tab.id ? 'bg-dark-950/30' : 'bg-dark-700'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left panel - content based on tab */}
        <div className="glass rounded-2xl p-6">
          {activeTab === 'formats' && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">Export Format</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {formatsAvailable.map((format) => {
                  const info = FORMAT_INFO[format];
                  if (!info) return null;

                  return (
                    <motion.button
                      key={format}
                      onClick={() => setSelectedFormat(format)}
                      className={`
                        w-full p-4 rounded-xl text-left transition-all duration-200
                        ${
                          selectedFormat === format
                            ? 'bg-primary-500/20 border-2 border-primary-500/50'
                            : 'bg-dark-800/50 border-2 border-transparent hover:bg-dark-700/50'
                        }
                      `}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`
                            w-10 h-10 rounded-lg flex items-center justify-center font-mono font-bold text-sm
                            ${selectedFormat === format ? 'bg-primary-500 text-dark-950' : 'bg-dark-700 text-dark-300'}
                          `}
                        >
                          {info.icon}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-dark-100">{info.name}</p>
                          <p className="text-sm text-dark-400">{info.description}</p>
                        </div>
                        {selectedFormat === format && (
                          <svg className="w-5 h-5 text-primary-400" viewBox="0 0 20 20" fill="currentColor">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                    </motion.button>
                  );
                })}
              </div>

              {/* Download button */}
              <motion.button
                onClick={() => onDownload(selectedFormat)}
                className="w-full mt-6 py-3 px-6 bg-primary-500 hover:bg-primary-600 text-dark-950 font-semibold rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
                Download {FORMAT_INFO[selectedFormat]?.name || selectedFormat}
              </motion.button>
            </>
          )}

          {activeTab === 'images' && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">Extracted Images</h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : images.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  No images extracted from this document
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {images.map((image) => (
                    <div
                      key={image.id}
                      className="bg-dark-800/50 rounded-xl p-4 flex items-center gap-4"
                    >
                      <div className="w-12 h-12 bg-dark-700 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-dark-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-dark-200 truncate">{image.filename}</p>
                        {image.caption && (
                          <p className="text-sm text-dark-400 truncate">{image.caption}</p>
                        )}
                      </div>
                      <button
                        onClick={() => handleDownloadImage(image.id, image.filename)}
                        className="p-2 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
                      >
                        <svg className="w-5 h-5 text-dark-300" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'tables' && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">Extracted Tables</h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : tables.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  No tables extracted from this document
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {tables.map((table) => (
                    <div
                      key={table.id}
                      className="bg-dark-800/50 rounded-xl p-4"
                    >
                      <div className="flex items-center gap-4 mb-3">
                        <div className="w-10 h-10 bg-dark-700 rounded-lg flex items-center justify-center">
                          <svg className="w-5 h-5 text-dark-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-dark-200">Table {table.id}</p>
                          {table.caption && (
                            <p className="text-sm text-dark-400 truncate">{table.caption}</p>
                          )}
                          <p className="text-xs text-dark-500">{table.rows.length} rows</p>
                        </div>
                        <button
                          onClick={() => handleDownloadTableCsv(table.id)}
                          className="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors text-sm text-dark-300 flex items-center gap-1"
                        >
                          <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                          CSV
                        </button>
                      </div>
                      {/* Table preview */}
                      {table.rows.length > 0 && (
                        <div className="overflow-x-auto">
                          <table className="w-full text-xs">
                            <tbody>
                              {table.rows.slice(0, 3).map((row, i) => (
                                <tr key={i} className={i === 0 ? 'bg-dark-700/50' : ''}>
                                  {row.slice(0, 4).map((cell, j) => (
                                    <td key={j} className="px-2 py-1 border border-dark-600 text-dark-300 truncate max-w-[100px]">
                                      {cell}
                                    </td>
                                  ))}
                                  {row.length > 4 && (
                                    <td className="px-2 py-1 border border-dark-600 text-dark-500">...</td>
                                  )}
                                </tr>
                              ))}
                              {table.rows.length > 3 && (
                                <tr>
                                  <td colSpan={5} className="px-2 py-1 text-center text-dark-500">
                                    ... {table.rows.length - 3} more rows
                                  </td>
                                </tr>
                              )}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === 'chunks' && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">RAG Chunks</h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : chunks.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  <p>No chunks generated</p>
                  <p className="text-sm mt-2">Enable chunking in Settings to generate RAG chunks</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {chunks.map((chunk) => (
                    <div
                      key={chunk.id}
                      className="bg-dark-800/50 rounded-xl p-4"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 bg-primary-500/20 text-primary-400 text-xs font-medium rounded">
                          Chunk {chunk.id}
                        </span>
                        {chunk.meta?.page && (
                          <span className="px-2 py-0.5 bg-dark-700 text-dark-400 text-xs rounded">
                            Page {chunk.meta.page}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-dark-300 line-clamp-3">{chunk.text}</p>
                    </div>
                  ))}
                </div>
              )}
              {chunks.length > 0 && (
                <motion.button
                  onClick={() => onDownload('chunks')}
                  className="w-full mt-4 py-2 px-4 bg-dark-700 hover:bg-dark-600 text-dark-200 font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Download All Chunks (JSON)
                </motion.button>
              )}
            </>
          )}

          {/* New conversion button */}
          <button
            onClick={onNewConversion}
            className="w-full mt-4 py-3 px-6 bg-dark-800 hover:bg-dark-700 text-dark-200 font-medium rounded-xl transition-colors duration-200"
          >
            Convert Another Document
          </button>
        </div>

        {/* Preview */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-dark-100">Preview</h3>
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="text-sm text-dark-400 hover:text-dark-200 transition-colors"
            >
              {showPreview ? 'Hide' : 'Show'}
            </button>
          </div>
          <AnimatePresence>
            {showPreview && preview && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="bg-dark-950 rounded-xl p-4 max-h-[500px] overflow-y-auto">
                  <pre className="text-sm text-dark-300 font-mono whitespace-pre-wrap break-words">
                    {preview}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          {!preview && (
            <div className="bg-dark-950 rounded-xl p-8 text-center">
              <p className="text-dark-500">No preview available</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}


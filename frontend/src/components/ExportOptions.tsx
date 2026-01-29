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

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { marked } from "marked";
import { useTranslation } from "react-i18next";
import {
  getExtractedImages,
  getExtractedTables,
  getDocumentChunks,
  downloadExtractedImage,
  downloadTableCsv,
  getExportContent,
} from "../services/api";
import type { ExtractedImage, ExtractedTable, DocumentChunk } from "../types";

// Configure marked for GFM (GitHub Flavored Markdown) with tables
marked.setOptions({
  gfm: true,
  breaks: true,
});

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

type PreviewMode = "rendered" | "raw";

const FORMAT_INFO: Record<
  string,
  { name: string; icon: string; description: string }
> = {
  markdown: {
    name: "Markdown",
    icon: "M",
    description: "Formatted text with headers, lists, and links",
  },
  html: {
    name: "HTML",
    icon: "</>",
    description: "Web-ready format with full styling",
  },
  json: {
    name: "JSON",
    icon: "{}",
    description: "Structured data with document hierarchy",
  },
  doctags: {
    name: "DocTags",
    icon: "#",
    description: "Tagged document tokens for AI processing",
  },
  text: {
    name: "Plain Text",
    icon: "Aa",
    description: "Simple text without formatting",
  },
  document_tokens: {
    name: "Document Tokens",
    icon: "[]",
    description: "Token-level document representation",
  },
  chunks: {
    name: "RAG Chunks",
    icon: "◫",
    description: "Document chunks for RAG applications",
  },
};

type TabType = "formats" | "images" | "tables" | "chunks";

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
  const { t } = useTranslation();
  const [selectedFormat, setSelectedFormat] = useState<string>("markdown");
  const [showPreview, setShowPreview] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>("formats");
  const [previewMode, setPreviewMode] = useState<PreviewMode>("rendered");

  // Extracted content state
  const [images, setImages] = useState<ExtractedImage[]>([]);
  const [tables, setTables] = useState<ExtractedTable[]>([]);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loadingContent, setLoadingContent] = useState(false);

  // Format-specific content cache
  const [formatContent, setFormatContent] = useState<Record<string, string>>(
    {}
  );
  const [loadingFormat, setLoadingFormat] = useState(false);

  // Image preview state
  const [imageUrls, setImageUrls] = useState<Record<number, string>>({});
  const [selectedImage, setSelectedImage] = useState<ExtractedImage | null>(
    null
  );

  // Load extracted content when tab changes
  useEffect(() => {
    const loadContent = async () => {
      setLoadingContent(true);
      try {
        if (activeTab === "images" && images.length === 0 && imagesCount > 0) {
          const response = await getExtractedImages(jobId);
          setImages(response.images);

          // Load image previews
          const urls: Record<number, string> = {};
          for (const image of response.images) {
            try {
              const blob = await downloadExtractedImage(jobId, image.id);
              urls[image.id] = URL.createObjectURL(blob);
            } catch (err) {
              console.error(`Error loading image ${image.id}:`, err);
            }
          }
          setImageUrls(urls);
        } else if (
          activeTab === "tables" &&
          tables.length === 0 &&
          tablesCount > 0
        ) {
          const response = await getExtractedTables(jobId);
          setTables(response.tables);
        } else if (
          activeTab === "chunks" &&
          chunks.length === 0 &&
          chunksCount > 0
        ) {
          const response = await getDocumentChunks(jobId);
          setChunks(response.chunks);
        }
      } catch (error) {
        console.error("Error loading content:", error);
      } finally {
        setLoadingContent(false);
      }
    };
    loadContent();
  }, [
    activeTab,
    jobId,
    images.length,
    tables.length,
    chunks.length,
    imagesCount,
    tablesCount,
    chunksCount,
  ]);

  // Cleanup image URLs on unmount
  useEffect(() => {
    return () => {
      Object.values(imageUrls).forEach((url) => URL.revokeObjectURL(url));
    };
  }, [imageUrls]);

  // Load content for selected format
  useEffect(() => {
    const loadFormatContent = async () => {
      // Skip if we already have this format's content cached
      if (formatContent[selectedFormat]) return;

      // Use the initial preview for markdown if available
      if (selectedFormat === "markdown" && preview) {
        setFormatContent((prev) => ({ ...prev, markdown: preview }));
        return;
      }

      setLoadingFormat(true);
      try {
        const response = await getExportContent(jobId, selectedFormat);
        setFormatContent((prev) => ({
          ...prev,
          [selectedFormat]: response.content,
        }));
      } catch (error) {
        console.error(`Error loading ${selectedFormat} content:`, error);
      } finally {
        setLoadingFormat(false);
      }
    };

    if (activeTab === "formats") {
      loadFormatContent();
    }
  }, [selectedFormat, jobId, activeTab, formatContent, preview]);

  // Check if current format supports rendered view
  const supportsRenderedView = useMemo(() => {
    return ["markdown", "html"].includes(selectedFormat);
  }, [selectedFormat]);

  // Get the current preview content
  const currentPreviewContent = useMemo(() => {
    return formatContent[selectedFormat] || preview || "";
  }, [formatContent, selectedFormat, preview]);

  // Render markdown to HTML using marked library
  const renderMarkdown = (md: string): string => {
    try {
      return marked.parse(md) as string;
    } catch (error) {
      console.error("Error parsing markdown:", error);
      return `<pre>${md}</pre>`;
    }
  };

  const handleDownloadImage = async (imageId: number, filename: string) => {
    try {
      const blob = await downloadExtractedImage(jobId, imageId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading image:", error);
    }
  };

  const handleDownloadTableCsv = async (tableId: number) => {
    try {
      const blob = await downloadTableCsv(jobId, tableId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `table_${tableId}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading CSV:", error);
    }
  };

  const tabs: { id: TabType; label: string; count?: number }[] = [
    { id: "formats", label: t("export.tabExportFormats") },
    { id: "images", label: t("export.tabImages"), count: imagesCount },
    { id: "tables", label: t("export.tabTables"), count: tablesCount },
    { id: "chunks", label: t("export.tabChunks"), count: chunksCount },
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
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-500/20 flex items-center justify-center"
        >
          <svg
            className="w-8 h-8 text-primary-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </motion.div>
        <h2 className="text-2xl font-bold text-dark-100 mb-2">
          {t("export.completeTitle")}
        </h2>
        <div className="flex items-center justify-center gap-4 text-dark-400">
          {confidence != null && confidence > 0 && (
            <span>
              {t("export.confidence")}{" "}
              <span className="text-primary-400 font-medium">
                {(confidence * 100).toFixed(1)}%
              </span>
            </span>
          )}
          {imagesCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">
                {imagesCount}
              </span>{" "}
              {t("export.images")}
            </span>
          )}
          {tablesCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">
                {tablesCount}
              </span>{" "}
              {t("export.tables")}
            </span>
          )}
          {chunksCount > 0 && (
            <span>
              <span className="text-primary-400 font-medium">
                {chunksCount}
              </span>{" "}
              {t("export.chunks")}
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
              ${
                activeTab === tab.id
                  ? "bg-primary-500 text-dark-950"
                  : "bg-dark-800 text-dark-300 hover:bg-dark-700"
              }
            `}
          >
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span
                className={`ml-2 px-1.5 py-0.5 rounded text-xs ${
                  activeTab === tab.id ? "bg-dark-950/30" : "bg-dark-700"
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left panel - content based on tab */}
        <div className="glass rounded-2xl p-6">
          {activeTab === "formats" && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">
                {t("export.exportFormatTitle")}
              </h3>
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
                            ? "bg-primary-500/20 border-2 border-primary-500/50"
                            : "bg-dark-800/50 border-2 border-transparent hover:bg-dark-700/50"
                        }
                      `}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`
                            w-10 h-10 rounded-lg flex items-center justify-center font-mono font-bold text-sm
                            ${
                              selectedFormat === format
                                ? "bg-primary-500 text-dark-950"
                                : "bg-dark-700 text-dark-300"
                            }
                          `}
                        >
                          {info.icon}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-dark-100">
                            {info.name}
                          </p>
                          <p className="text-sm text-dark-400">
                            {info.description}
                          </p>
                        </div>
                        {selectedFormat === format && (
                          <svg
                            className="w-5 h-5 text-primary-400"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
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
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
                {t("export.download")}{" "}
                {FORMAT_INFO[selectedFormat]?.name || selectedFormat}
              </motion.button>
            </>
          )}

          {activeTab === "images" && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">
                {t("export.extractedImagesTitle")}
              </h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : images.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  {t("export.noImages")}
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-[500px] overflow-y-auto">
                  {images.map((image) => (
                    <motion.div
                      key={image.id}
                      className="bg-dark-800/50 rounded-xl overflow-hidden group cursor-pointer"
                      whileHover={{ scale: 1.02 }}
                      onClick={() => setSelectedImage(image)}
                    >
                      {/* Image thumbnail */}
                      <div className="aspect-square relative bg-dark-900">
                        {imageUrls[image.id] ? (
                          <img
                            src={imageUrls[image.id]}
                            alt={image.caption || image.filename}
                            className="w-full h-full object-contain"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <svg
                              className="w-8 h-8 text-dark-600"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.5"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
                              />
                            </svg>
                          </div>
                        )}
                        {/* Hover overlay */}
                        <div className="absolute inset-0 bg-dark-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedImage(image);
                            }}
                            className="p-2 bg-dark-800/80 hover:bg-dark-700 rounded-lg transition-colors"
                            title={t("export.viewFullSize")}
                          >
                            <svg
                              className="w-5 h-5 text-dark-200"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7"
                              />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDownloadImage(image.id, image.filename);
                            }}
                            className="p-2 bg-dark-800/80 hover:bg-dark-700 rounded-lg transition-colors"
                            title={t("export.download")}
                          >
                            <svg
                              className="w-5 h-5 text-dark-200"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                fillRule="evenodd"
                                d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                                clipRule="evenodd"
                              />
                            </svg>
                          </button>
                        </div>
                      </div>
                      {/* Image info */}
                      <div className="p-2">
                        <p className="text-xs text-dark-300 truncate font-medium">
                          {image.filename}
                        </p>
                        {image.caption && (
                          <p className="text-xs text-dark-500 truncate">
                            {image.caption}
                          </p>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </>
          )}

          {activeTab === "tables" && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">
                {t("export.extractedTablesTitle")}
              </h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : tables.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  {t("export.noTables")}
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
                          <svg
                            className="w-5 h-5 text-dark-400"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.5"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125"
                            />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-dark-200">
                            Table {table.id}
                          </p>
                          {table.caption && (
                            <p className="text-sm text-dark-400 truncate">
                              {table.caption}
                            </p>
                          )}
                          <p className="text-xs text-dark-500">
                            {t("export.rows", { count: table.rows.length })}
                          </p>
                        </div>
                        <button
                          onClick={() => handleDownloadTableCsv(table.id)}
                          className="px-3 py-1.5 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors text-sm text-dark-300 flex items-center gap-1"
                        >
                          <svg
                            className="w-4 h-4"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path
                              fillRule="evenodd"
                              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                              clipRule="evenodd"
                            />
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
                                <tr
                                  key={i}
                                  className={i === 0 ? "bg-dark-700/50" : ""}
                                >
                                  {row.slice(0, 4).map((cell, j) => (
                                    <td
                                      key={j}
                                      className="px-2 py-1 border border-dark-600 text-dark-300 truncate max-w-[100px]"
                                    >
                                      {cell}
                                    </td>
                                  ))}
                                  {row.length > 4 && (
                                    <td className="px-2 py-1 border border-dark-600 text-dark-500">
                                      ...
                                    </td>
                                  )}
                                </tr>
                              ))}
                              {table.rows.length > 3 && (
                                <tr>
                                  <td
                                    colSpan={5}
                                    className="px-2 py-1 text-center text-dark-500"
                                  >
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

          {activeTab === "chunks" && (
            <>
              <h3 className="text-lg font-semibold text-dark-100 mb-4">
                {t("export.ragChunksTitle")}
              </h3>
              {loadingContent ? (
                <div className="flex items-center justify-center py-8">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : chunks.length === 0 ? (
                <div className="text-center py-8 text-dark-400">
                  <p>{t("export.noChunks")}</p>
                  <p className="text-sm mt-2">
                    {t("export.enableChunkingHint")}
                  </p>
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
                      <p className="text-sm text-dark-300 line-clamp-3">
                        {chunk.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
              {chunks.length > 0 && (
                <motion.button
                  onClick={() => onDownload("chunks")}
                  className="w-full mt-4 py-2 px-4 bg-dark-700 hover:bg-dark-600 text-dark-200 font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <svg
                    className="w-4 h-4"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                  {t("export.downloadAllChunks")}
                </motion.button>
              )}
            </>
          )}

          {/* New conversion button */}
          <button
            onClick={onNewConversion}
            className="w-full mt-4 py-3 px-6 bg-dark-800 hover:bg-dark-700 text-dark-200 font-medium rounded-xl transition-colors duration-200"
          >
            {t("export.convertAnother")}
          </button>
        </div>

        {/* Preview */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-dark-100">
                {t("export.previewTitle")}
              </h3>
              <span className="text-xs text-dark-500 bg-dark-800 px-2 py-1 rounded">
                {FORMAT_INFO[selectedFormat]?.name || selectedFormat}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {/* Rendered/Raw toggle for HTML and Markdown */}
              {supportsRenderedView && (
                <div className="flex items-center bg-dark-800 rounded-lg p-0.5">
                  <button
                    onClick={() => setPreviewMode("rendered")}
                    className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                      previewMode === "rendered"
                        ? "bg-primary-500 text-dark-950"
                        : "text-dark-400 hover:text-dark-200"
                    }`}
                  >
                    {t("export.rendered")}
                  </button>
                  <button
                    onClick={() => setPreviewMode("raw")}
                    className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                      previewMode === "raw"
                        ? "bg-primary-500 text-dark-950"
                        : "text-dark-400 hover:text-dark-200"
                    }`}
                  >
                    {t("export.raw")}
                  </button>
                </div>
              )}
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="text-sm text-dark-400 hover:text-dark-200 transition-colors"
              >
                {showPreview ? t("export.hide") : t("export.show")}
              </button>
            </div>
          </div>
          <AnimatePresence mode="wait">
            {showPreview && (
              <motion.div
                key={`${selectedFormat}-${previewMode}`}
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                {loadingFormat ? (
                  <div className="bg-dark-950 rounded-xl p-8 flex items-center justify-center">
                    <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : currentPreviewContent ? (
                  <div className="bg-dark-950 rounded-xl p-4 max-h-[500px] overflow-y-auto">
                    {/* Rendered HTML view - use iframe to isolate styles */}
                    {selectedFormat === "html" && previewMode === "rendered" ? (
                      <iframe
                        srcDoc={currentPreviewContent}
                        className="w-full min-h-[400px] rounded-lg border border-dark-700 bg-white"
                        sandbox="allow-same-origin"
                        title="HTML Preview"
                      />
                    ) : /* Rendered Markdown view */
                    selectedFormat === "markdown" &&
                      previewMode === "rendered" ? (
                      <div
                        className="prose prose-invert prose-sm max-w-none
                          prose-headings:text-dark-100 prose-p:text-dark-300
                          prose-a:text-primary-400 prose-strong:text-dark-200
                          prose-code:text-primary-300 prose-code:bg-dark-800 prose-code:px-1 prose-code:rounded
                          prose-pre:bg-dark-900 prose-pre:border prose-pre:border-dark-700"
                        dangerouslySetInnerHTML={{
                          __html: renderMarkdown(currentPreviewContent),
                        }}
                      />
                    ) : /* JSON formatted view */
                    selectedFormat === "json" ? (
                      <pre className="text-sm text-dark-300 font-mono whitespace-pre-wrap break-words">
                        {(() => {
                          try {
                            return JSON.stringify(
                              JSON.parse(currentPreviewContent),
                              null,
                              2
                            );
                          } catch {
                            return currentPreviewContent;
                          }
                        })()}
                      </pre>
                    ) : (
                      /* Raw view for all other formats */
                      <pre className="text-sm text-dark-300 font-mono whitespace-pre-wrap break-words">
                        {currentPreviewContent}
                      </pre>
                    )}
                  </div>
                ) : (
                  <div className="bg-dark-950 rounded-xl p-8 text-center">
                    <p className="text-dark-500">{t("export.noPreview")}</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
          {!showPreview && (
            <div className="bg-dark-950 rounded-xl p-4 text-center">
              <p className="text-dark-500 text-sm">{t("export.clickShow")}</p>
            </div>
          )}
        </div>
      </div>

      {/* Image lightbox modal */}
      <AnimatePresence>
        {selectedImage && imageUrls[selectedImage.id] && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-dark-950/90 backdrop-blur-sm p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative max-w-4xl max-h-[90vh] w-full"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute -top-12 right-0 p-2 text-dark-400 hover:text-dark-200 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>

              {/* Image container */}
              <div className="bg-dark-900 rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src={imageUrls[selectedImage.id]}
                  alt={selectedImage.caption || selectedImage.filename}
                  className="w-full h-auto max-h-[70vh] object-contain"
                />

                {/* Image info bar */}
                <div className="p-4 bg-dark-800 flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-dark-200">
                      {selectedImage.filename}
                    </p>
                    {selectedImage.caption && (
                      <p className="text-sm text-dark-400 truncate">
                        {selectedImage.caption}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() =>
                      handleDownloadImage(
                        selectedImage.id,
                        selectedImage.filename
                      )
                    }
                    className="ml-4 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-dark-950 font-medium rounded-lg transition-colors flex items-center gap-2"
                  >
                    <svg
                      className="w-4 h-4"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Download
                  </button>
                </div>
              </div>

              {/* Navigation arrows if multiple images */}
              {images.length > 1 && (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const currentIndex = images.findIndex(
                        (img) => img.id === selectedImage.id
                      );
                      const prevIndex =
                        currentIndex > 0 ? currentIndex - 1 : images.length - 1;
                      setSelectedImage(images[prevIndex]);
                    }}
                    className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-12 p-2 bg-dark-800/80 hover:bg-dark-700 rounded-full transition-colors"
                  >
                    <svg
                      className="w-6 h-6 text-dark-200"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M15 19l-7-7 7-7"
                      />
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const currentIndex = images.findIndex(
                        (img) => img.id === selectedImage.id
                      );
                      const nextIndex =
                        currentIndex < images.length - 1 ? currentIndex + 1 : 0;
                      setSelectedImage(images[nextIndex]);
                    }}
                    className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-12 p-2 bg-dark-800/80 hover:bg-dark-700 rounded-full transition-colors"
                  >
                    <svg
                      className="w-6 h-6 text-dark-200"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </button>
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

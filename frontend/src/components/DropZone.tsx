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

import {
  useCallback,
  useState,
  useRef,
  type ChangeEvent,
  type InputHTMLAttributes,
  type KeyboardEvent,
} from "react";
import { useDropzone, FileRejection, ErrorCode } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { DROPZONE_ACCEPT } from "../utils/supportedUploadFormats";
import { filterSupportedFiles, MAX_UPLOAD_BYTES } from "../utils/fileFilter";

interface DropZoneProps {
  onFilesAccepted: (files: File[]) => void;
  onUrlsSubmitted?: (urls: string[]) => void;
  isUploading: boolean;
  disabled?: boolean;
}

const FORMAT_CATEGORIES = [
  {
    nameKey: "documents",
    formats: ["PDF", "DOCX", "PPTX", "XLSX"],
    color: "primary",
  },
  { nameKey: "web", formats: ["HTML", "Markdown"], color: "blue" },
  {
    nameKey: "images",
    formats: ["PNG", "JPG", "TIFF", "WebP"],
    color: "purple",
  },
  { nameKey: "data", formats: ["XML", "AsciiDoc"], color: "green" },
];

// URL validation regex
const URL_REGEX = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;

/** Folder picker + multi-file drop zone always accepts multiple files. */
const FILE_DROPZONE_MULTIPLE = true;

export default function DropZone({
  onFilesAccepted,
  onUrlsSubmitted,
  isUploading,
  disabled,
}: DropZoneProps) {
  const { t } = useTranslation();
  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const filesOnlyInputRef = useRef<HTMLInputElement>(null);
  const [inputMode, setInputMode] = useState<"file" | "url">("file");
  const [urlsInput, setUrlsInput] = useState("");

  const onInputModeTabsKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      setInputMode((m) => (m === "file" ? "url" : "file"));
    },
    [],
  );

  const processBatchFileList = useCallback(
    (
      rawFiles: File[],
      opts?: {
        /** Files react-dropzone rejected (e.g. wrong type) while others in the same folder were accepted */
        pickerSkippedCount?: number;
      },
    ) => {
      setError(null);
      setInfoMessage(null);
      const pickerSkipped = opts?.pickerSkippedCount ?? 0;
      const { accepted, skipped } = filterSupportedFiles(rawFiles);

      const infoParts: string[] = [];
      if (pickerSkipped > 0) {
        infoParts.push(
          t("dropzone.pickerSkippedUnsupported", { count: pickerSkipped }),
        );
      }
      if (skipped.length > 0 && accepted.length > 0) {
        infoParts.push(
          t("dropzone.filesSkippedSummary", {
            skipped: skipped.length,
            accepted: accepted.length,
          }),
        );
      }
      if (infoParts.length > 0) {
        setInfoMessage(infoParts.join(" "));
      }

      if (accepted.length === 0) {
        const onlyLarge =
          skipped.length > 0 &&
          skipped.every((s) => s.reason === "too_large");
        setError(
          onlyLarge
            ? t("dropzone.allSkippedTooLarge")
            : t("dropzone.noSupportedFiles"),
        );
        return;
      }
      onFilesAccepted(accepted);
    },
    [onFilesAccepted, t],
  );

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      setError(null);
      setInfoMessage(null);

      const allTooManyNoAccepts =
        acceptedFiles.length === 0 &&
        rejectedFiles.length > 0 &&
        rejectedFiles.every((r) =>
          r.errors.some((e) => e.code === ErrorCode.TooManyFiles),
        );
      if (allTooManyNoAccepts) {
        setError(t("dropzone.tooManyFilesUnexpected"));
        return;
      }

      if (acceptedFiles.length > 0) {
        processBatchFileList(acceptedFiles, {
          pickerSkippedCount: rejectedFiles.length,
        });
        return;
      }

      if (rejectedFiles.length > 0) {
        const anyInvalidType = rejectedFiles.some((r) =>
          r.errors.some((e) => e.code === ErrorCode.FileInvalidType),
        );
        setError(
          anyInvalidType
            ? t("dropzone.allFilesUnsupportedByPicker")
            : rejectedFiles[0].errors.map((e) => e.message).join(", "),
        );
      }
    },
    [processBatchFileList, t],
  );

  const handleNativeMultiFileInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const list = e.target.files ? Array.from(e.target.files) : [];
      e.target.value = "";
      if (list.length === 0) return;
      processBatchFileList(list);
    },
    [processBatchFileList],
  );

  const directoryInputProps: InputHTMLAttributes<HTMLInputElement> = {
    webkitdirectory: "",
    directory: "",
  } as InputHTMLAttributes<HTMLInputElement>;

  const handleUrlsSubmit = useCallback(() => {
    setError(null);
    const lines = urlsInput
      .trim()
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length === 0) {
      setError(t("dropzone.errorEnterAtLeastOneUrl"));
      return;
    }

    const invalidUrls = lines.filter((url) => !URL_REGEX.test(url));
    if (invalidUrls.length > 0) {
      const shown = invalidUrls.slice(0, 3).join(", ");
      setError(
        t("dropzone.errorInvalidUrls", {
          urls: `${shown}${invalidUrls.length > 3 ? "..." : ""}`,
        }),
      );
      return;
    }

    if (onUrlsSubmitted) {
      onUrlsSubmitted(lines);
      setUrlsInput("");
    }
  }, [urlsInput, onUrlsSubmitted, t]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept: DROPZONE_ACCEPT,
    maxSize: MAX_UPLOAD_BYTES,
    multiple: FILE_DROPZONE_MULTIPLE,
    disabled: disabled || isUploading || inputMode === "url",
  });

  return (
    <div className="w-full">
      {/* Mode Toggle */}
      <div className="flex justify-center mb-3">
        <div
          role="tablist"
          aria-label={t("dropzone.inputModeLabel")}
          className="inline-flex rounded-lg bg-dark-800 p-1"
          onKeyDown={onInputModeTabsKeyDown}
        >
          <button
            type="button"
            role="tab"
            id="dropzone-tab-files"
            aria-selected={inputMode === "file"}
            aria-controls="dropzone-panel-files"
            tabIndex={inputMode === "file" ? 0 : -1}
            onClick={() => setInputMode("file")}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              inputMode === "file"
                ? "bg-primary-500 text-white"
                : "text-dark-300 hover:text-dark-100"
            }`}
            disabled={isUploading}
          >
            <span className="flex items-center gap-2">
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              {t("dropzone.localFiles")}
            </span>
          </button>
          <button
            type="button"
            role="tab"
            id="dropzone-tab-urls"
            aria-selected={inputMode === "url"}
            aria-controls="dropzone-panel-urls"
            tabIndex={inputMode === "url" ? 0 : -1}
            onClick={() => setInputMode("url")}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              inputMode === "url"
                ? "bg-primary-500 text-white"
                : "text-dark-300 hover:text-dark-100"
            }`}
            disabled={isUploading}
          >
            <span className="flex items-center gap-2">
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
              </svg>
              {t("dropzone.urls")}
            </span>
          </button>
        </div>
      </div>

      <div
        id="dropzone-panel-files"
        role="tabpanel"
        aria-labelledby="dropzone-tab-files"
        hidden={inputMode !== "file"}
      >
        <div {...getRootProps()}>
          <motion.div
            className={`
              relative overflow-hidden rounded-2xl border-2 border-dashed p-8
              transition-all duration-300 cursor-pointer
              ${
                isDragActive
                  ? "border-primary-500 bg-primary-500/10"
                  : "border-dark-600 hover:border-dark-500"
              }
              ${isDragAccept ? "border-primary-400 bg-primary-500/15" : ""}
              ${isDragReject ? "border-red-500 bg-red-500/10" : ""}
              ${disabled || isUploading ? "opacity-50 cursor-not-allowed" : ""}
            `}
            whileHover={!disabled && !isUploading ? { scale: 1.01 } : undefined}
            whileTap={!disabled && !isUploading ? { scale: 0.99 } : undefined}
          >
            <input {...getInputProps(directoryInputProps)} />
            <input
              ref={filesOnlyInputRef}
              type="file"
              className="hidden"
              multiple
              onChange={handleNativeMultiFileInputChange}
              disabled={disabled || isUploading}
            />

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
                      <svg
                        className="animate-spin w-full h-full text-primary-500"
                        viewBox="0 0 24 24"
                      >
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
                    <p className="text-lg font-medium text-dark-200">
                      {t("dropzone.uploading")}
                    </p>
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
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"
                        />
                      </svg>
                    </div>
                    <p className="text-lg font-medium text-primary-400">
                      {isDragReject
                        ? t("dropzone.fileTypeNotSupported")
                        : t("dropzone.dropHereMultiple")}
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
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                        />
                      </svg>
                    </div>
                    <p className="text-lg font-medium text-dark-200 mb-1.5">
                      {t("dropzone.dragAndDropMultiple")}
                    </p>
                    <p className="text-sm text-dark-400 mb-3">
                      {t("dropzone.orClickToChooseFolder")}
                    </p>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        filesOnlyInputRef.current?.click();
                      }}
                      disabled={disabled || isUploading}
                      className="mb-3 px-4 py-2 text-sm font-medium rounded-lg border border-dark-600 text-dark-200 hover:border-primary-500 hover:text-primary-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {t("dropzone.chooseFiles")}
                    </button>

                    {/* Format categories */}
                    <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                      {FORMAT_CATEGORIES.map((category) => (
                        <div
                          key={category.nameKey}
                          className="flex items-center gap-1.5"
                        >
                          <span className="text-xs text-dark-500">
                            {t(`dropzone.categories.${category.nameKey}`)}:
                          </span>
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

                    <p className="mt-4 text-xs text-primary-400">
                      {t("dropzone.unifiedUploadHint")}
                    </p>
                    <p className="mt-2 text-xs text-dark-500 max-w-md mx-auto">
                      {t("dropzone.folderHint")}
                    </p>
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
                    ? "0 0 30px rgba(239, 68, 68, 0.3)"
                    : "0 0 30px rgba(20, 184, 166, 0.3)",
                }}
              />
            )}
          </motion.div>
        </div>
      </div>

      <div
        id="dropzone-panel-urls"
        role="tabpanel"
        aria-labelledby="dropzone-tab-urls"
        hidden={inputMode !== "url"}
      >
        {/* URL Input */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border-2 border-dashed border-dark-600 p-6 bg-dark-900/50"
        >
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 mb-4 text-primary-400">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
              </svg>
            </div>

            <h3 className="text-lg font-medium text-dark-200 mb-1.5">
              {t("dropzone.enterUrlTitleMultiple")}
            </h3>
            <p className="text-sm text-dark-400 mb-4">
              {t("dropzone.enterUrlBodyMultiple")}
            </p>

            <div className="w-full max-w-xl">
              <textarea
                value={urlsInput}
                onChange={(e) => setUrlsInput(e.target.value)}
                placeholder={t("dropzone.multipleUrlsPlaceholder")}
                className="w-full h-40 px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 placeholder-dark-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none font-mono text-sm"
                disabled={isUploading}
              />
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-dark-500">
                  {t("dropzone.urlsEntered", {
                    count: urlsInput.trim().split("\n").filter(Boolean).length,
                  })}
                </span>
                <button
                  onClick={handleUrlsSubmit}
                  disabled={
                    isUploading ||
                    !urlsInput.trim() ||
                    !onUrlsSubmitted
                  }
                  className="px-6 py-2 bg-primary-500 hover:bg-primary-600 disabled:bg-primary-500/50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <svg
                        className="animate-spin w-4 h-4"
                        viewBox="0 0 24 24"
                      >
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
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                      </svg>
                      {t("dropzone.processing")}
                    </>
                  ) : (
                    <>
                      <svg
                        className="w-4 h-4"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                        />
                      </svg>
                      {t("dropzone.convertAll")}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Supported formats hint */}
            <div className="mt-6 text-xs text-dark-500">
              <span>{t("dropzone.supportedHint")}</span>
            </div>
          </div>
        </motion.div>
      </div>

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

      <AnimatePresence>
        {infoMessage && !error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-3 p-3 bg-primary-500/10 border border-primary-500/30 rounded-lg"
          >
            <p className="text-sm text-primary-300">{infoMessage}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* File size info */}
      <p className="mt-3 text-xs text-dark-500 text-center">
        {inputMode === "file"
          ? t("dropzone.maxFileSize")
          : t("dropzone.maxDownloadSize")}
      </p>
    </div>
  );
}

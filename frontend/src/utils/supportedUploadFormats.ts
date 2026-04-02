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

import type { Accept } from "react-dropzone";

/**
 * Lowercase extensions accepted for conversion.
 * Keep in sync with backend `Config.ALLOWED_EXTENSIONS` in backend/config.py.
 */
export const CONVERT_ALLOWED_EXTENSIONS: ReadonlySet<string> = new Set([
  "pdf",
  "docx",
  "pptx",
  "xlsx",
  "html",
  "htm",
  "md",
  "markdown",
  "MD",
  "csv",
  "png",
  "jpg",
  "jpeg",
  "tiff",
  "tif",
  "gif",
  "webp",
  "bmp",
  "wav",
  "mp3",
  "vtt",
  "xml",
  "json",
  "txt",
  "asciidoc",
  "adoc",
]);

/**
 * react-dropzone `accept` map (MIME keys + extension list).
 * Used by the file picker and attr-accept (extension fallback when MIME is missing).
 */
export const DROPZONE_ACCEPT: Accept = {
  "application/pdf": [".pdf", ".PDF"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
    ".docx",
    ".DOCX",
  ],
  "application/vnd.openxmlformats-officedocument.presentationml.presentation": [
    ".pptx",
    ".PPTX",
  ],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
    ".xlsx",
    ".XLSX",
  ],
  "text/html": [".html", ".htm", ".HTML", ".HTM"],
  "text/markdown": [".md", ".markdown", ".MD", ".MARKDOWN"],
  "text/csv": [".csv", ".CSV"],
  "image/*": [
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
    ".gif",
    ".webp",
    ".bmp",
    ".PNG",
    ".JPG",
    ".JPEG",
    ".TIFF",
    ".TIF",
    ".GIF",
    ".WEBP",
    ".BMP",
  ],
  "audio/*": [".wav", ".mp3", ".WAV", ".MP3"],
  "text/vtt": [".vtt", ".VTT"],
  "application/xml": [".xml", ".XML"],
  "application/json": [".json", ".JSON"],
  "text/plain": [".txt", ".asciidoc", ".adoc", ".TXT", ".ASCIIDOC", ".ADOC"],
};

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

import { CONVERT_ALLOWED_EXTENSIONS } from "./supportedUploadFormats";

/** Default matches DropZone / backend per-file limit (100MB). */
export const MAX_UPLOAD_BYTES = 100 * 1024 * 1024;

export type SkipReason = "unsupported_type" | "too_large";

export interface SkippedFile {
  name: string;
  reason: SkipReason;
}

/**
 * Extension after the last dot, lowercase (matches backend `allowed_file` logic for normal names).
 */
export function getExtensionLower(filename: string): string | null {
  if (!filename || !filename.includes(".")) return null;
  const base = filename.replace(/^.*[/\\]/, "");
  const ext = base.includes(".") ? base.split(".").pop() : null;
  return ext ? ext.toLowerCase() : null;
}

export function isAllowedExtension(ext: string | null): boolean {
  if (!ext) return false;
  return CONVERT_ALLOWED_EXTENSIONS.has(ext);
}

export function filterSupportedFiles(
  files: File[],
  maxBytes: number = MAX_UPLOAD_BYTES,
): { accepted: File[]; skipped: SkippedFile[] } {
  const accepted: File[] = [];
  const skipped: SkippedFile[] = [];

  for (const file of files) {
    const ext = getExtensionLower(file.name);
    if (!isAllowedExtension(ext)) {
      skipped.push({ name: file.name, reason: "unsupported_type" });
      continue;
    }
    if (file.size > maxBytes) {
      skipped.push({ name: file.name, reason: "too_large" });
      continue;
    }
    accepted.push(file);
  }

  return { accepted, skipped };
}

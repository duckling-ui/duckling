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

import { describe, it, expect } from "vitest";
import {
  filterSupportedFiles,
  getExtensionLower,
  isAllowedExtension,
  MAX_UPLOAD_BYTES,
} from "../../utils/fileFilter";

describe("fileFilter", () => {
  it("getExtensionLower handles nested paths and casing", () => {
    expect(getExtensionLower("folder/doc.PDF")).toBe("pdf");
    expect(getExtensionLower("a.b.docx")).toBe("docx");
    expect(getExtensionLower("nope")).toBeNull();
    expect(getExtensionLower(".hidden")).toBe("hidden");
  });

  it("isAllowedExtension mirrors allowed set", () => {
    expect(isAllowedExtension("pdf")).toBe(true);
    expect(isAllowedExtension("txt")).toBe(true);
    expect(isAllowedExtension("json")).toBe(true);
    expect(isAllowedExtension("exe")).toBe(false);
    expect(isAllowedExtension(null)).toBe(false);
  });

  it("filterSupportedFiles accepts supported types and skips unknown", () => {
    const files = [
      new File(["a"], "a.pdf", { type: "application/pdf" }),
      new File(["b"], "b.exe", { type: "application/octet-stream" }),
      new File(["c"], "readme.md", { type: "text/markdown" }),
    ];
    const { accepted, skipped } = filterSupportedFiles(files);
    expect(accepted.map((f) => f.name).sort()).toEqual(["a.pdf", "readme.md"]);
    expect(skipped).toEqual([{ name: "b.exe", reason: "unsupported_type" }]);
  });

  it("filterSupportedFiles skips oversize files", () => {
    const big = new File([new Uint8Array(MAX_UPLOAD_BYTES + 1)], "huge.pdf", {
      type: "application/pdf",
    });
    const { accepted, skipped } = filterSupportedFiles([big]);
    expect(accepted).toEqual([]);
    expect(skipped).toEqual([{ name: "huge.pdf", reason: "too_large" }]);
  });

  it("filterSupportedFiles empty input", () => {
    expect(filterSupportedFiles([])).toEqual({ accepted: [], skipped: [] });
  });
});

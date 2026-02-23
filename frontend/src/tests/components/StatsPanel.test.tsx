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

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import StatsPanel from "../../components/StatsPanel";
import type { HistoryStats } from "../../types";

const mockStats: HistoryStats = {
  conversions: {
    total: 150,
    completed: 142,
    failed: 5,
    pending: 2,
    processing: 1,
    success_rate: 94.7,
    format_breakdown: { pdf: 100, docx: 30, image: 20 },
    avg_processing_seconds: 12.5,
    ocr_backend_breakdown: { easyocr: 80, ocrmac: 50 },
    output_format_breakdown: { markdown: 150 },
    performance_device_breakdown: { auto: 120, cpu: 30 },
    source_type_breakdown: { upload: 100, url: 30, batch: 20 },
    chunking_enabled_count: 25,
  },
  storage: {
    uploads: { count: 10, size_bytes: 1048576, size_mb: 1.0 },
    outputs: { count: 140, size_bytes: 52428800, size_mb: 50.0 },
    total_size_mb: 51.0,
  },
  queue_depth: 2,
};

vi.mock("../../services/api", () => ({
  getHistoryStats: vi.fn(() => Promise.resolve(mockStats)),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe("StatsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders overview stats when open with data", async () => {
    renderWithProviders(
      <StatsPanel isOpen={true} onClose={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText("Overview")).toBeInTheDocument();
      expect(screen.getByText("Total")).toBeInTheDocument();
      expect(screen.getByText("Success")).toBeInTheDocument();
      expect(screen.getByText("Failed")).toBeInTheDocument();
      expect(screen.getByText("94.7%")).toBeInTheDocument();
    });
  });

  it("renders storage section", async () => {
    renderWithProviders(
      <StatsPanel isOpen={true} onClose={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText("Storage")).toBeInTheDocument();
      expect(screen.getByText("Uploads")).toBeInTheDocument();
      expect(screen.getByText("Total storage")).toBeInTheDocument();
    });
  });

  it("renders breakdown sections", async () => {
    renderWithProviders(
      <StatsPanel isOpen={true} onClose={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText("Input formats")).toBeInTheDocument();
      expect(screen.getByText("OCR backends")).toBeInTheDocument();
      expect(screen.getByText("Source types")).toBeInTheDocument();
    });
  });

  it("calls onClose when backdrop is clicked", async () => {
    const onClose = vi.fn();
    renderWithProviders(
      <StatsPanel isOpen={true} onClose={onClose} />
    );

    await waitFor(() => {
      expect(screen.getByText("Statistics")).toBeInTheDocument();
    });

    const backdrop = document.querySelector(".fixed.inset-0.bg-dark-950");
    if (backdrop) {
      fireEvent.click(backdrop as HTMLElement);
      expect(onClose).toHaveBeenCalled();
    }
  });

  it("does not render when isOpen is false", () => {
    renderWithProviders(
      <StatsPanel isOpen={false} onClose={() => {}} />
    );

    expect(screen.queryByText("Statistics")).not.toBeInTheDocument();
  });
});

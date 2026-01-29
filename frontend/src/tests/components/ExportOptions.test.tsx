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

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExportOptions from '../../components/ExportOptions';
import * as api from '../../services/api';

// Mock the API module
vi.mock('../../services/api', () => ({
  getExportContent: vi.fn(),
  getExtractedImages: vi.fn(),
  getExtractedTables: vi.fn(),
  getDocumentChunks: vi.fn(),
  downloadExtractedImage: vi.fn(),
  downloadTableCsv: vi.fn(),
}));

describe('ExportOptions', () => {
  const mockOnDownload = vi.fn();
  const mockOnNewConversion = vi.fn();

  const defaultProps = {
    jobId: 'test-job-123',
    formatsAvailable: ['markdown', 'html', 'json'],
    preview: '# Test Document\n\nThis is a preview.',
    onDownload: mockOnDownload,
    onNewConversion: mockOnNewConversion,
    confidence: 0.95,
  };

  beforeEach(() => {
    mockOnDownload.mockClear();
    mockOnNewConversion.mockClear();
    // Mock API responses
    vi.mocked(api.getExportContent).mockResolvedValue({
      job_id: 'test-job-123',
      format: 'html',
      content: '<html>Test content</html>',
    });
    vi.mocked(api.getExtractedImages).mockResolvedValue({
      job_id: 'test-job-123',
      images: [],
      count: 0,
    });
    vi.mocked(api.getExtractedTables).mockResolvedValue({
      job_id: 'test-job-123',
      tables: [],
      count: 0,
    });
    vi.mocked(api.getDocumentChunks).mockResolvedValue({
      job_id: 'test-job-123',
      chunks: [],
      count: 0,
    });
  });

  it('renders success message', async () => {
    render(<ExportOptions {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('Conversion Complete!')).toBeInTheDocument();
    });
  });

  it('shows confidence score', async () => {
    render(<ExportOptions {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('95.0%')).toBeInTheDocument();
    });
  });

  it('renders available formats', async () => {
    render(<ExportOptions {...defaultProps} />);

    await waitFor(() => {
      // Use getAllByText since format names may appear multiple times (in cards and preview badge)
      expect(screen.getAllByText('Markdown').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('HTML').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('JSON').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('calls onDownload when download button is clicked', () => {
    render(<ExportOptions {...defaultProps} />);

    const downloadButton = screen.getByRole('button', { name: /download markdown/i });
    fireEvent.click(downloadButton);

    expect(mockOnDownload).toHaveBeenCalledWith('markdown');
  });

  it('calls onNewConversion when new conversion button is clicked', () => {
    render(<ExportOptions {...defaultProps} />);

    const newButton = screen.getByRole('button', { name: /convert another document/i });
    fireEvent.click(newButton);

    expect(mockOnNewConversion).toHaveBeenCalled();
  });

  it('has preview panel visible by default', async () => {
    render(<ExportOptions {...defaultProps} />);

    await waitFor(() => {
      // Preview is shown by default - check for Hide button
      expect(screen.getByRole('button', { name: /hide/i })).toBeInTheDocument();
    });
  });

  it('allows selecting different formats', () => {
    render(<ExportOptions {...defaultProps} />);

    // Find the HTML format card button (not the preview badge)
    // The format cards have a specific structure with font-medium class
    const htmlElements = screen.getAllByText('HTML');
    const htmlButton = htmlElements[0].closest('button');
    if (htmlButton) {
      fireEvent.click(htmlButton);
    }

    const downloadButton = screen.getByRole('button', { name: /download html/i });
    fireEvent.click(downloadButton);

    expect(mockOnDownload).toHaveBeenCalledWith('html');
  });

  it('can toggle preview visibility', () => {
    render(<ExportOptions {...defaultProps} />);

    // Preview is shown by default
    const hideButton = screen.getByRole('button', { name: /hide/i });
    expect(hideButton).toBeInTheDocument();

    // Click to hide
    fireEvent.click(hideButton);

    // Now should show "Show" button
    expect(screen.getByRole('button', { name: /show/i })).toBeInTheDocument();
  });
});


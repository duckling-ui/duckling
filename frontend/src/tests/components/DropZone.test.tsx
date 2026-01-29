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
import { render, screen } from '@testing-library/react';
import DropZone from '../../components/DropZone';

describe('DropZone', () => {
  const mockOnFileAccepted = vi.fn();

  beforeEach(() => {
    mockOnFileAccepted.mockClear();
  });

  it('renders correctly', () => {
    render(<DropZone onFileAccepted={mockOnFileAccepted} isUploading={false} />);

    expect(screen.getByText(/drag and drop your document here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('shows uploading state', () => {
    render(<DropZone onFileAccepted={mockOnFileAccepted} isUploading={true} />);

    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
  });

  it('shows supported formats', () => {
    render(<DropZone onFileAccepted={mockOnFileAccepted} isUploading={false} />);

    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('DOCX')).toBeInTheDocument();
    expect(screen.getByText('Markdown')).toBeInTheDocument();
  });

  it('shows file size limit', () => {
    render(<DropZone onFileAccepted={mockOnFileAccepted} isUploading={false} />);

    expect(screen.getByText(/maximum file size: 100mb/i)).toBeInTheDocument();
  });

  it('is disabled when uploading', () => {
    const { container } = render(
      <DropZone onFileAccepted={mockOnFileAccepted} isUploading={true} />
    );

    const dropzone = container.querySelector('[class*="cursor-not-allowed"]');
    expect(dropzone).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    const { container } = render(
      <DropZone onFileAccepted={mockOnFileAccepted} isUploading={false} disabled={true} />
    );

    const dropzone = container.querySelector('[class*="cursor-not-allowed"]');
    expect(dropzone).toBeInTheDocument();
  });
});


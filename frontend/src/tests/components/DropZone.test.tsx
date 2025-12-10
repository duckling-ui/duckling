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


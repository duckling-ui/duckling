import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ExportOptions from '../../components/ExportOptions';

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
  });

  it('renders success message', () => {
    render(<ExportOptions {...defaultProps} />);

    expect(screen.getByText('Conversion Complete!')).toBeInTheDocument();
  });

  it('shows confidence score', () => {
    render(<ExportOptions {...defaultProps} />);

    expect(screen.getByText('95.0%')).toBeInTheDocument();
  });

  it('renders available formats', () => {
    render(<ExportOptions {...defaultProps} />);

    expect(screen.getByText('Markdown')).toBeInTheDocument();
    expect(screen.getByText('HTML')).toBeInTheDocument();
    expect(screen.getByText('JSON')).toBeInTheDocument();
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

  it('shows preview content', () => {
    render(<ExportOptions {...defaultProps} />);

    expect(screen.getByText(/# Test Document/)).toBeInTheDocument();
  });

  it('allows selecting different formats', () => {
    render(<ExportOptions {...defaultProps} />);

    // Click on HTML format
    const htmlButton = screen.getByText('HTML').closest('button');
    if (htmlButton) {
      fireEvent.click(htmlButton);
    }

    const downloadButton = screen.getByRole('button', { name: /download html/i });
    fireEvent.click(downloadButton);

    expect(mockOnDownload).toHaveBeenCalledWith('html');
  });

  it('shows no preview message when preview is empty', () => {
    render(<ExportOptions {...defaultProps} preview={undefined} />);

    expect(screen.getByText('No preview available')).toBeInTheDocument();
  });
});


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

    // Use getAllByText since format names may appear multiple times (in cards and preview badge)
    expect(screen.getAllByText('Markdown').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('HTML').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('JSON').length).toBeGreaterThanOrEqual(1);
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

  it('has preview panel visible by default', () => {
    render(<ExportOptions {...defaultProps} />);

    // Preview is shown by default - check for Hide button
    expect(screen.getByRole('button', { name: /hide/i })).toBeInTheDocument();
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


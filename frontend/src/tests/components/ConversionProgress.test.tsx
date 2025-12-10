import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ConversionProgress from '../../components/ConversionProgress';

describe('ConversionProgress', () => {
  it('renders with progress and message', () => {
    render(
      <ConversionProgress
        progress={50}
        message="Analyzing document..."
        filename="test.pdf"
      />
    );

    expect(screen.getByText('Converting Document')).toBeInTheDocument();
    expect(screen.getByText('Analyzing document...')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  it('shows correct step states based on progress', () => {
    render(
      <ConversionProgress
        progress={50}
        message="Processing..."
      />
    );

    // Upload complete should be checked at 50%
    expect(screen.getByText('Upload complete')).toBeInTheDocument();
    expect(screen.getByText('Analyzing document structure')).toBeInTheDocument();
  });

  it('shows all steps completed at 100%', () => {
    render(
      <ConversionProgress
        progress={100}
        message="Complete!"
      />
    );

    expect(screen.getByText('Finalizing')).toBeInTheDocument();
  });

  it('renders without filename', () => {
    render(
      <ConversionProgress
        progress={25}
        message="Processing..."
      />
    );

    expect(screen.getByText('Converting Document')).toBeInTheDocument();
    expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
  });
});


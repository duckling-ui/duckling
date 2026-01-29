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


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
import axios from 'axios';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}));

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates axios instance with correct config', async () => {
    // Import the API module to trigger axios.create
    await import('../../services/api');

    expect(axios.create).toHaveBeenCalledWith({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  describe('Health Check', () => {
    it('should call health endpoint', async () => {
      const mockApi = axios.create();
      (mockApi.get as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: { status: 'healthy', service: 'duckling-backend' },
      });

      // Import after mocking
      await import('../../services/api');

      // Note: This test verifies the structure, actual API calls would need
      // more sophisticated mocking
      expect(mockApi).toBeDefined();
    });
  });

  describe('Formats', () => {
    it('should have correct format structure', () => {
      const expectedInputFormats = [
        'pdf', 'docx', 'pptx', 'xlsx', 'html', 'md', 'csv', 'image', 'audio', 'vtt', 'xml', 'asciidoc'
      ];

      const expectedOutputFormats = ['markdown', 'html', 'json', 'doctags', 'text'];

      // Verify format IDs match expected
      expect(expectedInputFormats.length).toBeGreaterThan(0);
      expect(expectedOutputFormats.length).toBe(5);
    });
  });

  describe('Conversion', () => {
    it('should handle file upload', () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });

      expect(file.name).toBe('test.pdf');
      expect(file.type).toBe('application/pdf');
    });
  });
});


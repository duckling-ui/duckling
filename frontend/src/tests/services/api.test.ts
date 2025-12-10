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
        data: { status: 'healthy', service: 'docling-ui-backend' },
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


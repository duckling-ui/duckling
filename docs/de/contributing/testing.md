# Tests

Anleitung zum Schreiben und Ausführen von Tests in Duckling.

## Überblick

- **Backend**: pytest mit Coverage
- **Frontend**: Vitest mit React Testing Library

## Tests ausführen

### Backend-Tests

```bash
cd backend
source venv/bin/activate
pytest
```

Mit Coverage:

```bash
pytest --cov=. --cov-report=html
```

### Frontend-Tests

```bash
cd frontend
npm test
```

Mit Coverage:

```bash
npm run test:coverage
```

Watch-Modus:

```bash
npm run test:watch
```

---

## Backend-Tests

### Teststruktur

```
backend/tests/
├── __init__.py
├── conftest.py         # Gemeinsame Fixtures
├── test_api.py         # API-Endpunkt-Tests
├── test_converter.py   # Converter-Service-Tests
├── test_content_store.py # Content-addressed Storage Utilities
├── test_history.py     # History-Service-Tests
└── test_migration.py   # Datenbank-Migrationsskripte
```

### Fixtures

```python
# conftest.py
import pytest
from duckling import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    # Return a file-like object
    pass
```

### Beispieltests

```python
def test_convert_pdf_success(client, sample_pdf):
    """Test successful PDF conversion."""
    response = client.post(
        '/api/convert',
        data={'file': sample_pdf},
        content_type='multipart/form-data'
    )

    assert response.status_code == 202
    assert 'job_id' in response.json

def test_convert_invalid_file(client):
    """Test conversion with invalid file type."""
    response = client.post(
        '/api/convert',
        data={'file': (io.BytesIO(b'invalid'), 'test.exe')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert 'error' in response.json

def test_get_settings(client):
    """Test getting current settings."""
    response = client.get('/api/settings')

    assert response.status_code == 200
    assert 'ocr' in response.json
    assert 'tables' in response.json
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_conversion_with_mock(client):
    """Test conversion with mocked Docling."""
    with patch('services.converter.DocumentConverter') as mock:
        mock_instance = MagicMock()
        mock_instance.convert.return_value = {'content': 'test'}
        mock.return_value = mock_instance

        response = client.post('/api/convert', ...)

        assert response.status_code == 202
```

---

## Frontend-Tests

### Teststruktur

```
frontend/src/tests/
├── setup.ts         # Test-Setup
├── App.test.tsx     # App-Komponenten-Tests
├── DropZone.test.tsx
├── useConversion.test.ts
└── api.test.ts
```

### Setup

```typescript
// setup.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock fetch
global.fetch = vi.fn();
```

### Komponenten-Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DropZone } from '@/components/DropZone';

describe('DropZone', () => {
  it('should render drop zone', () => {
    render(<DropZone onFileAccepted={vi.fn()} />);

    expect(screen.getByText(/drag.*drop/i)).toBeInTheDocument();
  });

  it('should call onFileAccepted when file is dropped', async () => {
    const onFileAccepted = vi.fn();
    render(<DropZone onFileAccepted={onFileAccepted} />);

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    const dropzone = screen.getByRole('button');

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });

    expect(onFileAccepted).toHaveBeenCalledWith(file);
  });

  it('should reject invalid file types', async () => {
    const onFileAccepted = vi.fn();
    render(<DropZone onFileAccepted={onFileAccepted} />);

    const file = new File(['content'], 'test.exe', { type: 'application/x-msdownload' });
    const dropzone = screen.getByRole('button');

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });

    expect(onFileAccepted).not.toHaveBeenCalled();
  });
});
```

### Hook-Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useConversion } from '@/hooks/useConversion';

describe('useConversion', () => {
  it('should start with idle status', () => {
    const { result } = renderHook(() => useConversion());

    expect(result.current.status).toBe('idle');
  });

  it('should update status during conversion', async () => {
    const { result } = renderHook(() => useConversion());

    await act(async () => {
      await result.current.startConversion(mockFile);
    });

    expect(result.current.status).toBe('completed');
  });
});
```

### API-Mocking

```typescript
import { vi } from 'vitest';
import { api } from '@/services/api';

vi.mock('@/services/api', () => ({
  api: {
    uploadFile: vi.fn(),
    getStatus: vi.fn(),
    getResult: vi.fn(),
  }
}));

describe('conversion flow', () => {
  beforeEach(() => {
    vi.mocked(api.uploadFile).mockResolvedValue({ job_id: '123' });
    vi.mocked(api.getStatus).mockResolvedValue({ status: 'completed' });
  });

  // ... tests
});
```

---

## Testrichtlinien

### Backend

- pytest für Tests verwenden
- Ziel: >80 % Code-Abdeckung
- Erfolgs- und Fehlerfälle testen
- Fixtures für gemeinsames Setup
- Externe Dienste mocken (Docling, Dateisystem)

### Frontend

- Vitest und React Testing Library verwenden
- Komponenten-Rendering und Interaktionen testen
- Globale Events (z. B. `window` `message`), die von einem `useEffect` verarbeitet werden und von asynchron geladenen Daten abhängen, erst auslösen, nachdem die Effekte gelaufen sind (z. B. `await act(async () => { await new Promise((r) => setTimeout(r, 0)); })`), damit in der CI nicht vor dem Registrieren der Listener gefeuert wird
- API-Aufrufe angemessen mocken
- Fehler- und Ladezustände testen
- `userEvent` für realistische Interaktionen

### Allgemein

- Aussagekräftige Testnamen
- Eine Assertion pro Test wenn möglich
- Randfälle testen
- Tests unabhängig halten
- Nach Tests aufräumen

---

## Continuous Integration

Tests laufen automatisch bei:

- Erstellung eines Pull Requests
- Push auf den main-Branch

### CI-Konfiguration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm ci
          npm test
```

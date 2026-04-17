# Tests

Leitfaden zum Schreiben und Ausführen von Tests in Duckling.

## Überblick

- **Backend**: pytest mit Abdeckung
- **Frontend**: Vitest mit React Testing Library

## Tests ausführen

### Backend-Tests

```bash
cd backend
source venv/bin/activate
pytest
```

Mit Abdeckung:

```bash
pytest --cov=. --cov-report=html
```

### Frontend-Tests

```bash
cd frontend
npm test
```

Mit Abdeckung:

```bash
npm run test:coverage
```

Watch-Modus:

```bash
npm run test:watch
```

---

## Backend-Tests

### Struktur

```
backend/tests/
├── __init__.py
├── conftest.py         # Gemeinsame Fixtures
├── test_api.py        # API-Endpunkt-Tests
├── test_converter.py  # Converter-Service-Tests
├── test_content_store.py # inhaltsadressierter Speicher
├── test_history.py    # History-Service-Tests
└── test_migration.py  # Datenbank-Migrationsskripte
```

### Fixtures

```python
# conftest.py
import pytest
from duckling import create_app

@pytest.fixture
def app():
    """Erstellt die Anwendung für Tests."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Erstellt den Test-Client."""
    return app.test_client()

@pytest.fixture
def sample_pdf():
    """Erstellt eine Beispiel-PDF-Datei für Tests."""
    # Dateiähnliches Objekt zurückgeben
    pass
```

### Beispieltests

```python
def test_convert_pdf_success(client, sample_pdf):
    """Erfolgreiche PDF-Konvertierung testen."""
    response = client.post(
        '/api/convert',
        data={'file': sample_pdf},
        content_type='multipart/form-data'
    )

    assert response.status_code == 202
    assert 'job_id' in response.json

def test_convert_invalid_file(client):
    """Konvertierung mit ungültigem Dateityp testen."""
    response = client.post(
        '/api/convert',
        data={'file': (io.BytesIO(b'invalid'), 'test.exe')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert 'error' in response.json

def test_get_settings(client):
    """Aktuelle Einstellungen abrufen testen."""
    response = client.get('/api/settings')

    assert response.status_code == 200
    assert 'ocr' in response.json
    assert 'tables' in response.json
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_conversion_with_mock(client):
    """Konvertierung mit gemocktem Docling testen."""
    with patch('services.converter.DocumentConverter') as mock:
        mock_instance = MagicMock()
        mock_instance.convert.return_value = {'content': 'test'}
        mock.return_value = mock_instance

        response = client.post('/api/convert', ...)

        assert response.status_code == 202
```

---

## Frontend-Tests

### Struktur

```
frontend/src/tests/
├── setup.ts         # Test-Setup
├── App.test.tsx     # App-Komponententests
├── DropZone.test.tsx
├── useConversion.test.ts
└── api.test.ts
```

### Setup

```typescript
// setup.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// fetch mocken
global.fetch = vi.fn();
```

### Komponententests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DropZone } from '@/components/DropZone';

describe('DropZone', () => {
  it('should render drop zone', () => {
    render(<DropZone onFilesAccepted={vi.fn()} isUploading={false} />);

    expect(screen.getByText(/drag.*drop/i)).toBeInTheDocument();
  });

  it('should call onFilesAccepted when file is dropped', async () => {
    const onFilesAccepted = vi.fn();
    render(<DropZone onFilesAccepted={onFilesAccepted} isUploading={false} />);

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    const dropzone = screen.getByRole('button');

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });

    expect(onFilesAccepted).toHaveBeenCalledWith([file]);
  });

  it('should reject invalid file types', async () => {
    const onFilesAccepted = vi.fn();
    render(<DropZone onFilesAccepted={onFilesAccepted} isUploading={false} />);

    const file = new File(['content'], 'test.exe', { type: 'application/x-msdownload' });
    const dropzone = screen.getByRole('button');

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] }
    });

    expect(onFilesAccepted).not.toHaveBeenCalled();
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

  // ... Tests
});
```

---

## Testrichtlinien

### Backend

- pytest für Tests verwenden
- Über 80 % Code-Abdeckung anstreben
- Erfolgs- und Fehlerfälle testen
- Fixtures für gemeinsames Setup nutzen
- Externe Dienste mocken (Docling, Dateisystem)

### Frontend

- Vitest und React Testing Library verwenden
- Rendering und Interaktionen der Komponenten testen
- Bei globalen Events (z. B. `window` `message`), die von einem `useEffect` verarbeitet werden, der von asynchron geladenen Daten abhängt, auf die Ausführung der Effects nach dem Erscheinen der Daten warten (z. B. `await act(async () => { await new Promise((r) => setTimeout(r, 0)); })`), damit die CI nicht auslöst, bevor Listener registriert sind
- API-Aufrufe angemessen mocken
- Fehler- und Ladezustände testen
- `userEvent` für realistische Interaktionen verwenden

### Allgemein

- Aussagekräftige Testnamen
- Wenn möglich eine Assertion pro Test
- Grenzfälle testen
- Tests unabhängig halten
- Nach Tests aufräumen

---

## Continuous Integration

Tests laufen automatisch bei:

- Erstellung eines Pull Requests
- Push auf den Branch `main`

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

# Pruebas

Guía para escribir y ejecutar pruebas en Duckling.

## Descripción general

- **Backend**: pytest con cobertura
- **Frontend**: Vitest con React Testing Library

## Ejecutar pruebas

### Pruebas del backend

```bash
cd backend
source venv/bin/activate
pytest
```

Con cobertura:

```bash
pytest --cov=. --cov-report=html
```

### Pruebas del frontend

```bash
cd frontend
npm test
```

Con cobertura:

```bash
npm run test:coverage
```

Modo observación:

```bash
npm run test:watch
```

---

## Pruebas del backend

### Estructura

```
backend/tests/
├── __init__.py
├── conftest.py         # Fixtures compartidas
├── test_api.py        # Pruebas de endpoints API
├── test_converter.py  # Pruebas del servicio converter
├── test_content_store.py # Almacenamiento direccionado por contenido
├── test_history.py    # Pruebas del servicio de historial
└── test_migration.py  # Scripts de migración de base de datos
```

### Fixtures

```python
# conftest.py
import pytest
from duckling import create_app

@pytest.fixture
def app():
    """Crea la aplicación para pruebas."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Crea el cliente de prueba."""
    return app.test_client()

@pytest.fixture
def sample_pdf():
    """Crea un PDF de ejemplo para pruebas."""
    # Devolver un objeto tipo archivo
    pass
```

### Ejemplos de pruebas

```python
def test_convert_pdf_success(client, sample_pdf):
    """Prueba conversión PDF exitosa."""
    response = client.post(
        '/api/convert',
        data={'file': sample_pdf},
        content_type='multipart/form-data'
    )

    assert response.status_code == 202
    assert 'job_id' in response.json

def test_convert_invalid_file(client):
    """Prueba conversión con tipo de archivo no válido."""
    response = client.post(
        '/api/convert',
        data={'file': (io.BytesIO(b'invalid'), 'test.exe')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert 'error' in response.json

def test_get_settings(client):
    """Prueba obtención de ajustes actuales."""
    response = client.get('/api/settings')

    assert response.status_code == 200
    assert 'ocr' in response.json
    assert 'tables' in response.json
```

### Simulación (mocking)

```python
from unittest.mock import patch, MagicMock

def test_conversion_with_mock(client):
    """Prueba conversión con Docling simulado."""
    with patch('services.converter.DocumentConverter') as mock:
        mock_instance = MagicMock()
        mock_instance.convert.return_value = {'content': 'test'}
        mock.return_value = mock_instance

        response = client.post('/api/convert', ...)

        assert response.status_code == 202
```

---

## Pruebas del frontend

### Estructura

```
frontend/src/tests/
├── setup.ts         # Configuración de pruebas
├── App.test.tsx     # Pruebas del componente App
├── DropZone.test.tsx
├── useConversion.test.ts
└── api.test.ts
```

### Configuración

```typescript
// setup.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Simular fetch
global.fetch = vi.fn();
```

### Pruebas de componentes

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

### Pruebas de hooks

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

### Simulación de API

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

  // ... pruebas
});
```

---

## Directrices de pruebas

### Backend

- Usar pytest
- Apuntar a más del 80 % de cobertura
- Probar casos de éxito y de error
- Usar fixtures para configuración común
- Simular servicios externos (Docling, sistema de archivos)

### Frontend

- Usar Vitest y React Testing Library
- Probar renderizado e interacciones de componentes
- Al disparar eventos globales (por ejemplo `message` en `window`) manejados por un `useEffect` que depende de datos cargados de forma asíncrona, espere a que los efectos se ejecuten tras aparecer los datos (por ejemplo `await act(async () => { await new Promise((r) => setTimeout(r, 0)); })`) para que la CI no dispare antes de que se registren los escuchas
- Simular llamadas API de forma adecuada
- Probar estados de error y de carga
- Usar `userEvent` para interacciones realistas

### General

- Nombres de prueba descriptivos
- Una aserción por prueba cuando sea posible
- Probar casos límite
- Mantener pruebas independientes
- Limpiar tras las pruebas

---

## Integración continua

Las pruebas se ejecutan automáticamente en:

- Creación de un pull request
- Push a la rama `main`

### Configuración de CI

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

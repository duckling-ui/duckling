# Tests

Guide pour rédiger et exécuter les tests dans Duckling.

## Aperçu

- **Backend** : pytest avec couverture
- **Frontend** : Vitest avec React Testing Library

## Exécuter les tests

### Tests backend

```bash
cd backend
source venv/bin/activate
pytest
```

Avec couverture :

```bash
pytest --cov=. --cov-report=html
```

### Tests frontend

```bash
cd frontend
npm test
```

Avec couverture :

```bash
npm run test:coverage
```

Mode surveillance :

```bash
npm run test:watch
```

---

## Tests backend

### Structure

```
backend/tests/
├── __init__.py
├── conftest.py         # Fixtures partagées
├── test_api.py        # Tests des points de terminaison API
├── test_converter.py  # Tests du service converter
├── test_content_store.py # Stockage adressé par contenu
├── test_history.py    # Tests du service d’historique
└── test_migration.py  # Scripts de migration de base de données
```

### Fixtures

```python
# conftest.py
import pytest
from duckling import create_app

@pytest.fixture
def app():
    """Crée l'application pour les tests."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Crée le client de test."""
    return app.test_client()

@pytest.fixture
def sample_pdf():
    """Crée un fichier PDF d'exemple pour les tests."""
    # Retourner un objet de type fichier
    pass
```

### Exemples de tests

```python
def test_convert_pdf_success(client, sample_pdf):
    """Teste la conversion PDF réussie."""
    response = client.post(
        '/api/convert',
        data={'file': sample_pdf},
        content_type='multipart/form-data'
    )

    assert response.status_code == 202
    assert 'job_id' in response.json

def test_convert_invalid_file(client):
    """Teste la conversion avec un type de fichier invalide."""
    response = client.post(
        '/api/convert',
        data={'file': (io.BytesIO(b'invalid'), 'test.exe')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    assert 'error' in response.json

def test_get_settings(client):
    """Teste la récupération des paramètres actuels."""
    response = client.get('/api/settings')

    assert response.status_code == 200
    assert 'ocr' in response.json
    assert 'tables' in response.json
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_conversion_with_mock(client):
    """Teste la conversion avec Docling mocké."""
    with patch('services.converter.DocumentConverter') as mock:
        mock_instance = MagicMock()
        mock_instance.convert.return_value = {'content': 'test'}
        mock.return_value = mock_instance

        response = client.post('/api/convert', ...)

        assert response.status_code == 202
```

---

## Tests frontend

### Structure

```
frontend/src/tests/
├── setup.ts         # Configuration des tests
├── App.test.tsx     # Tests du composant App
├── DropZone.test.tsx
├── useConversion.test.ts
└── api.test.ts
```

### Configuration

```typescript
// setup.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock de fetch
global.fetch = vi.fn();
```

### Tests de composants

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

### Tests de hooks

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

### Mock de l’API

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

## Lignes directrices des tests

### Backend

- Utiliser pytest
- Viser plus de 80 % de couverture
- Tester les cas de succès et d’erreur
- Utiliser des fixtures pour la configuration commune
- Mocker les services externes (Docling, système de fichiers)

### Frontend

- Utiliser Vitest et React Testing Library
- Tester le rendu et les interactions des composants
- Lorsque vous déclenchez des événements globaux (par ex. `message` sur `window`) gérés par un `useEffect` dépendant de données chargées de façon asynchrone, attendez que les effets s’exécutent après l’apparition des données (par ex. `await act(async () => { await new Promise((r) => setTimeout(r, 0)); })`) pour que la CI n’envoie pas avant l’attachement des écouteurs
- Mocker les appels API de façon appropriée
- Tester les états d’erreur et de chargement
- Utiliser `userEvent` pour des interactions réalistes

### Général

- Noms de tests descriptifs
- Une assertion par test lorsque c’est possible
- Tester les cas limites
- Garder les tests indépendants
- Nettoyer après les tests

---

## Intégration continue

Les tests s’exécutent automatiquement sur :

- Création d’une pull request
- Push sur la branche `main`

### Configuration CI

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

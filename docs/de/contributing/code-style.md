# Code-Stil

Codierungsstandards und Konventionen für Duckling.

## Python (Backend)

### Allgemeine Richtlinien

- PEP-8-Richtlinien befolgen
- Type Hints verwenden
- Maximale Zeilenlänge: 100 Zeichen
- Docstrings für Funktionen und Klassen verwenden

### Funktionsdokumentation

```python
def convert_document(file_path: str, settings: dict) -> ConversionResult:
    """
    Convert a document using Docling.

    Args:
        file_path: Path to the document file
        settings: Conversion settings dictionary

    Returns:
        ConversionResult object with converted content

    Raises:
        ValueError: If file format is not supported
        IOError: If file cannot be read
    """
    pass
```

### Klassendokumentation

```python
class ConverterService:
    """
    Service for document conversion operations.

    This service manages the conversion pipeline, job queue,
    and interaction with the Docling library.

    Attributes:
        _job_queue: Queue for pending conversion jobs
        _max_concurrent_jobs: Maximum parallel conversions
    """
    pass
```

### Imports

Imports in folgender Reihenfolge:

1. Standardbibliothek
2. Drittanbieter-Pakete
3. Lokale Module

```python
import os
import json
from typing import Optional, Dict, List

from flask import Flask, request
from sqlalchemy import Column, String

from models.database import Conversion
from services.converter import ConverterService
```

### Formatierung

Black für automatische Formatierung verwenden:

```bash
pip install black
black backend/
```

---

## TypeScript/React (Frontend)

### Allgemeine Richtlinien

- Funktionskomponenten mit Hooks verwenden
- TypeScript für Typsicherheit
- ESLint-Konfiguration befolgen
- Aussagekräftige Komponenten- und Variablennamen

### Komponentenstruktur

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

export function Button({
  label,
  onClick,
  disabled = false,
  variant = 'primary'
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {label}
    </button>
  );
}
```

### Hooks

```typescript
export function useConversion() {
  const [status, setStatus] = useState<ConversionStatus>('idle');
  const [result, setResult] = useState<ConversionResult | null>(null);

  const startConversion = useCallback(async (file: File) => {
    setStatus('uploading');
    // ...
  }, []);

  return { status, result, startConversion };
}
```

### Dateiorganisation

```
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.test.tsx
│   └── index.ts
├── DropZone/
│   ├── DropZone.tsx
│   ├── DropZone.test.tsx
│   └── index.ts
```

### Imports

```typescript
// React and hooks first
import { useState, useCallback, useEffect } from 'react';

// Third-party libraries
import { motion } from 'framer-motion';
import axios from 'axios';

// Local components
import { Button } from '@/components/Button';
import { useConversion } from '@/hooks/useConversion';

// Types
import type { ConversionResult } from '@/types';
```

### Formatierung

Prettier für automatische Formatierung:

```bash
npm run format
```

---

## Commit-Nachrichten {#commit-messages}

[Conventional Commits](https://www.conventionalcommits.org/) befolgen:

```
type(scope): description

[optional body]

[optional footer]
```

### Typen

| Typ | Beschreibung |
|-----|--------------|
| `feat` | Neue Funktion |
| `fix` | Fehlerbehebung |
| `docs` | Dokumentationsänderungen |
| `style` | Code-Stiländerungen (Formatierung) |
| `refactor` | Code-Refaktorierung |
| `test` | Tests hinzufügen/aktualisieren |
| `chore` | Wartungsaufgaben |

### Beispiele

```
feat(upload): add drag-and-drop file upload

Implemented drag-and-drop functionality using react-dropzone.
Supports multiple file selection and folder upload in the default drop zone.

Closes #123

Signed-off-by: Your Name <your.email@example.com>
```

```
fix(converter): handle large PDF files correctly

Fixed memory issue when processing PDFs > 50MB by streaming
the file instead of loading entirely into memory.
```

```
docs(readme): update installation instructions

Added Docker setup instructions and troubleshooting section.
```

### DCO-Signatur {#dco-sign-off}

Alle Commits **MÜSSEN** mit dem [Developer Certificate of Origin (DCO)](https://developercertificate.org/) signiert werden. Dies bestätigt, dass Sie das Recht haben, den Beitrag unter der Projektlizenz einzureichen.

Fügen Sie die Signatur zu jedem Commit mit `git commit -s` hinzu:

```bash
git commit -s -m "feat(upload): add drag-and-drop file upload"
```

Dies fügt eine `Signed-off-by:`-Zeile mit Ihrem Namen und Ihrer E-Mail aus Ihrer Git-Konfiguration hinzu. Sie können sie auch manuell am Ende Ihrer Commit-Nachricht hinzufügen:

```
Signed-off-by: Your Name <your.email@example.com>
```

PRs mit unsignierten Commits werden nicht gemergt.

---

## CSS/Tailwind

### Klassenorganisation

Tailwind-Klassen konsistent anordnen:

1. Layout (flex, grid, position)
2. Abstände (margin, padding)
3. Größe (width, height)
4. Typografie (font, text)
5. Visuell (background, border, shadow)
6. Interaktiv (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* content */}
</div>
```

### Benutzerdefinierte Klassen

`@apply` sparsam verwenden, Komposition bevorzugen:

```css
/* Prefer this */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* Over inline classes everywhere */
```

---

## API-Design

### Endpoint-Benennung

- Substantive, keine Verben
- Pluralformen verwenden
- Kebab-Case für mehrteilige Ressourcen

```
GET    /api/conversions
POST   /api/conversions
GET    /api/conversions/{id}
DELETE /api/conversions/{id}
GET    /api/conversions/{id}/status
```

### Antwortformat

```json
{
  "data": { ... },
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

### Fehlerformat

```json
{
  "error": "ValidationError",
  "message": "File type not supported",
  "details": {
    "field": "file",
    "allowed": ["pdf", "docx", "png"]
  }
}
```

# Code-Stil

Kodierungsstandards und Konventionen für Duckling.

## Python (Backend)

### Allgemeine Richtlinien

- PEP 8 befolgen
- Typannotationen verwenden
- Maximale Zeilenlänge: 100 Zeichen
- Docstrings für Funktionen und Klassen verwenden

### Funktionsdokumentation

```python
def convert_document(file_path: str, settings: dict) -> ConversionResult:
    """
    Konvertiert ein Dokument mit Docling.

    Args:
        file_path: Pfad zur Dokumentdatei
        settings: Wörterbuch mit Konvertierungseinstellungen

    Returns:
        ConversionResult-Objekt mit konvertiertem Inhalt

    Raises:
        ValueError: Wenn das Dateiformat nicht unterstützt wird
        IOError: Wenn die Datei nicht gelesen werden kann
    """
    pass
```

### Klassendokumentation

```python
class ConverterService:
    """
    Dienst für Dokumentkonvertierungen.

    Dieser Dienst verwaltet die Konvertierungs-Pipeline, die Job-Warteschlange
    und die Interaktion mit der Docling-Bibliothek.

    Attributes:
        _job_queue: Warteschlange für ausstehende Konvertierungsjobs
        _max_concurrent_jobs: Maximale parallele Konvertierungen
    """
    pass
```

### Importe

Importe in dieser Reihenfolge:

1. Standardbibliothek
2. Pakete von Drittanbietern
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

- Funktionale Komponenten mit Hooks verwenden
- TypeScript für Typsicherheit nutzen
- ESLint-Konfiguration befolgen
- Aussagekräftige Komponenten- und Variablennamen verwenden

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

### Importe

```typescript
// Zuerst React und Hooks
import { useState, useCallback, useEffect } from 'react';

// Bibliotheken von Drittanbietern
import { motion } from 'framer-motion';
import axios from 'axios';

// Lokale Komponenten
import { Button } from '@/components/Button';
import { useConversion } from '@/hooks/useConversion';

// Typen
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
type(scope): Beschreibung

[optionaler Textkörper]

[optionaler Footer]
```

### Typen

| Typ | Beschreibung |
|------|-------------|
| `feat` | Neue Funktion |
| `fix` | Fehlerbehebung |
| `docs` | Dokumentationsänderungen |
| `style` | Code-Stil (Formatierung) |
| `refactor` | Refaktorierung |
| `test` | Tests hinzufügen/aktualisieren |
| `chore` | Wartungsaufgaben |

### Beispiele

```
feat(upload): Drag-and-Drop-Dateiupload hinzufügen

Drag-and-Drop mit react-dropzone implementiert.
Mehrfachauswahl und Ordner-Upload in der Standard-Dropzone unterstützt.

Closes #123

Signed-off-by: Ihr Name <ihre.email@beispiel.de>
```

```
fix(converter): große PDF-Dateien korrekt verarbeiten

Speicherproblem bei PDFs > 50 MB behoben durch Streaming
statt vollständigem Laden in den Speicher.
```

```
docs(readme): Installationsanweisungen aktualisieren

Docker-Setup und Abschnitt zur Fehlerbehebung ergänzt.
```

### DCO-Sign-off {#dco-sign-off}

Alle Commits **MÜSSEN** mit dem [Developer Certificate of Origin (DCO)](https://developercertificate.org/) signiert werden. Damit bestätigen Sie, dass Sie das Recht haben, den Beitrag unter der Projektlizenz einzureichen.

Fügen Sie bei jedem Commit die Signatur mit `git commit -s` hinzu:

```bash
git commit -s -m "feat(upload): Drag-and-Drop-Dateiupload hinzufügen"
```

Damit wird eine Zeile `Signed-off-by:` mit Ihrem Namen und Ihrer E-Mail aus der Git-Konfiguration angehängt. Sie können sie auch manuell am Ende der Commit-Nachricht ergänzen:

```
Signed-off-by: Ihr Name <ihre.email@beispiel.de>
```

Pull Requests mit nicht signierten Commits werden nicht zusammengeführt.

---

## CSS/Tailwind

### Klassen-Reihenfolge

Tailwind-Klassen einheitlich sortieren:

1. Layout (flex, grid, position)
2. Abstände (margin, padding)
3. Größe (width, height)
4. Typografie (font, text)
5. Darstellung (background, border, shadow)
6. Interaktion (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* Inhalt */}
</div>
```

### Eigene Klassen

`@apply` sparsam verwenden, Komposition bevorzugen:

```css
/* So bevorzugen */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* Statt überall Inline-Klassen */
```

---

## API-Design

### Endpunktbenennung

- Substantive statt Verben
- Pluralformen
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
  "message": "Dateityp nicht unterstützt",
  "details": {
    "field": "file",
    "allowed": ["pdf", "docx", "png"]
  }
}
```

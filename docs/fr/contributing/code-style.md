# Style de code

Normes et conventions de codage pour Duckling.

## Python (Backend)

### Directives générales

- Suivre les directives PEP 8
- Utiliser les type hints
- Longueur maximale de ligne : 100 caractères
- Utiliser des docstrings pour les fonctions et classes

### Documentation des fonctions

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

### Documentation des classes

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

Ordre des imports :

1. Bibliothèque standard
2. Paquets tiers
3. Modules locaux

```python
import os
import json
from typing import Optional, Dict, List

from flask import Flask, request
from sqlalchemy import Column, String

from models.database import Conversion
from services.converter import ConverterService
```

### Formatage

Utiliser Black pour le formatage automatique :

```bash
pip install black
black backend/
```

---

## TypeScript/React (Frontend)

### Directives générales

- Utiliser des composants fonctionnels avec des hooks
- Utiliser TypeScript pour la sécurité des types
- Suivre la configuration ESLint
- Utiliser des noms significatifs pour les composants et variables

### Structure des composants

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

### Organisation des fichiers

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

### Formatage

Utiliser Prettier pour le formatage automatique :

```bash
npm run format
```

---

## Messages de commit {#commit-messages}

Suivre les [Conventional Commits](https://www.conventionalcommits.org/) :

```
type(scope): description

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `style` | Style de code (formatage) |
| `refactor` | Refactorisation |
| `test` | Ajout/mise à jour de tests |
| `chore` | Maintenance |

### Exemples

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

### Signature DCO {#dco-sign-off}

Tous les commits **DOIVENT** être signés avec le [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Cela certifie que vous avez le droit de soumettre la contribution sous la licence du projet.

Ajoutez la signature à chaque commit avec `git commit -s` :

```bash
git commit -s -m "feat(upload): add drag-and-drop file upload"
```

Cela ajoute une ligne `Signed-off-by:` avec votre nom et email de votre configuration Git. Vous pouvez aussi l'ajouter manuellement à la fin du message de commit :

```
Signed-off-by: Your Name <your.email@example.com>
```

Les PR avec des commits non signés ne seront pas fusionnées.

---

## CSS/Tailwind

### Organisation des classes

Ordre des classes Tailwind de manière cohérente :

1. Layout (flex, grid, position)
2. Espacement (margin, padding)
3. Taille (width, height)
4. Typographie (font, text)
5. Visuel (background, border, shadow)
6. Interactif (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* content */}
</div>
```

### Classes personnalisées

Utiliser `@apply` avec parcimonie, préférer la composition :

```css
/* Préférer ceci */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* Plutôt que des classes inline partout */
```

---

## Conception API

### Nommage des endpoints

- Utiliser des noms, pas des verbes
- Utiliser les formes plurielles
- Utiliser kebab-case pour les ressources multi-mots

```
GET    /api/conversions
POST   /api/conversions
GET    /api/conversions/{id}
DELETE /api/conversions/{id}
GET    /api/conversions/{id}/status
```

### Format de réponse

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

### Format d'erreur

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

# Estilo de código

Estándares y convenciones de codificación para Duckling.

## Python (Backend)

### Directrices generales

- Seguir las directrices PEP 8
- Usar type hints
- Longitud máxima de línea: 100 caracteres
- Usar docstrings para funciones y clases

### Documentación de funciones

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

### Documentación de clases

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

Ordenar los imports así:

1. Biblioteca estándar
2. Paquetes de terceros
3. Módulos locales

```python
import os
import json
from typing import Optional, Dict, List

from flask import Flask, request
from sqlalchemy import Column, String

from models.database import Conversion
from services.converter import ConverterService
```

### Formato

Usar Black para formato automático:

```bash
pip install black
black backend/
```

---

## TypeScript/React (Frontend)

### Directrices generales

- Usar componentes funcionales con hooks
- Usar TypeScript para seguridad de tipos
- Seguir la configuración de ESLint
- Usar nombres significativos para componentes y variables

### Estructura de componentes

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

### Organización de archivos

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

### Formato

Usar Prettier para formato automático:

```bash
npm run format
```

---

## Mensajes de commit {#commit-messages}

Seguir [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

### Tipos

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva función |
| `fix` | Corrección de error |
| `docs` | Cambios en documentación |
| `style` | Cambios de estilo de código (formato) |
| `refactor` | Refactorización de código |
| `test` | Añadir/actualizar pruebas |
| `chore` | Tareas de mantenimiento |

### Ejemplos

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

### Firma DCO {#dco-sign-off}

Todos los commits **DEBEN** estar firmados con el [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Esto certifica que tienes derecho a enviar la contribución bajo la licencia del proyecto.

Añade la firma a cada commit usando `git commit -s`:

```bash
git commit -s -m "feat(upload): add drag-and-drop file upload"
```

Esto añade una línea `Signed-off-by:` con tu nombre y email de tu configuración de Git. También puedes añadirla manualmente al final del mensaje de commit:

```
Signed-off-by: Your Name <your.email@example.com>
```

Los PRs con commits sin firmar no serán fusionados.

---

## CSS/Tailwind

### Organización de clases

Ordenar las clases de Tailwind de forma consistente:

1. Layout (flex, grid, position)
2. Espaciado (margin, padding)
3. Tamaño (width, height)
4. Tipografía (font, text)
5. Visual (background, border, shadow)
6. Interactivo (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* content */}
</div>
```

### Clases personalizadas

Usar `@apply` con moderación, preferir composición:

```css
/* Preferir esto */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* En lugar de clases inline en todas partes */
```

---

## Diseño de API

### Nombrado de endpoints

- Usar sustantivos, no verbos
- Usar formas plurales
- Usar kebab-case para recursos de varias palabras

```
GET    /api/conversions
POST   /api/conversions
GET    /api/conversions/{id}
DELETE /api/conversions/{id}
GET    /api/conversions/{id}/status
```

### Formato de respuesta

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

### Formato de error

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

# Estilo de código

Normas y convenciones de codificación para Duckling.

## Python (backend)

### Directrices generales

- Seguir PEP 8
- Usar anotaciones de tipo
- Longitud máxima de línea: 100 caracteres
- Usar docstrings en funciones y clases

### Documentación de funciones

```python
def convert_document(file_path: str, settings: dict) -> ConversionResult:
    """
    Convierte un documento con Docling.

    Args:
        file_path: Ruta al archivo del documento
        settings: Diccionario de opciones de conversión

    Returns:
        Objeto ConversionResult con el contenido convertido

    Raises:
        ValueError: Si el formato de archivo no está soportado
        IOError: Si no se puede leer el archivo
    """
    pass
```

### Documentación de clases

```python
class ConverterService:
    """
    Servicio para operaciones de conversión de documentos.

    Este servicio gestiona la canalización de conversión, la cola de trabajos
    y la interacción con la biblioteca Docling.

    Attributes:
        _job_queue: Cola de trabajos de conversión pendientes
        _max_concurrent_jobs: Máximo de conversiones en paralelo
    """
    pass
```

### Importaciones

Ordene las importaciones así:

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

Use Black para el formato automático:

```bash
pip install black
black backend/
```

---

## TypeScript/React (frontend)

### Directrices generales

- Componentes funcionales con hooks
- TypeScript para seguridad de tipos
- Respetar la configuración de ESLint
- Nombres de componentes y variables claros

### Estructura de componente

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

### Importaciones

```typescript
// React y hooks primero
import { useState, useCallback, useEffect } from 'react';

// Bibliotecas de terceros
import { motion } from 'framer-motion';
import axios from 'axios';

// Componentes locales
import { Button } from '@/components/Button';
import { useConversion } from '@/hooks/useConversion';

// Tipos
import type { ConversionResult } from '@/types';
```

### Formato

Use Prettier para el formato automático:

```bash
npm run format
```

---

## Mensajes de commit {#commit-messages}

Siga [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): descripción

[cuerpo opcional]

[pie opcional]
```

### Tipos

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de error |
| `docs` | Cambios en documentación |
| `style` | Estilo de código (formato) |
| `refactor` | Refactorización |
| `test` | Añadir o actualizar pruebas |
| `chore` | Tareas de mantenimiento |

### Ejemplos

```
feat(upload): añadir carga de archivos por arrastrar y soltar

Funcionalidad de arrastrar y soltar con react-dropzone.
Admite selección múltiple y carga de carpetas en la zona predeterminada.

Closes #123

Signed-off-by: Su Nombre <su.correo@ejemplo.com>
```

```
fix(converter): manejar correctamente PDF grandes

Corregido problema de memoria con PDF > 50 MB transmitiendo
el archivo en lugar de cargarlo por completo en memoria.
```

```
docs(readme): actualizar instrucciones de instalación

Añadidas instrucciones de Docker y sección de solución de problemas.
```

### Firma DCO {#dco-sign-off}

Todos los commits **DEBEN** firmarse con el [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Con ello certifica que tiene derecho a enviar la contribución bajo la licencia del proyecto.

Añada la firma en cada commit con `git commit -s`:

```bash
git commit -s -m "feat(upload): añadir carga de archivos por arrastrar y soltar"
```

Esto añade una línea `Signed-off-by:` con su nombre y correo de la configuración de Git. También puede añadirla manualmente al final del mensaje:

```
Signed-off-by: Su Nombre <su.correo@ejemplo.com>
```

No se fusionarán PR con commits sin firmar.

---

## CSS/Tailwind

### Organización de clases

Ordene las clases de Tailwind de forma coherente:

1. Diseño (flex, grid, position)
2. Espaciado (margin, padding)
3. Tamaño (width, height)
4. Tipografía (font, text)
5. Visual (background, border, shadow)
6. Interactivo (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* contenido */}
</div>
```

### Clases personalizadas

Use `@apply` con moderación, prefiera la composición:

```css
/* Preferir esto */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* En lugar de clases en línea por todas partes */
```

---

## Diseño de API

### Nombres de endpoints

- Sustantivos, no verbos
- Formas plurales
- kebab-case para recursos de varias palabras

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
  "message": "Tipo de archivo no soportado",
  "details": {
    "field": "file",
    "allowed": ["pdf", "docx", "png"]
  }
}
```

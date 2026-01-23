# Code Style

Coding standards and conventions for Duckling.

## Python (Backend)

### General Guidelines

- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

### Function Documentation

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

### Class Documentation

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

Order imports as:

1. Standard library
2. Third-party packages
3. Local modules

```python
import os
import json
from typing import Optional, Dict, List

from flask import Flask, request
from sqlalchemy import Column, String

from models.database import Conversion
from services.converter import ConverterService
```

### Formatting

Use Black for automatic formatting:

```bash
pip install black
black backend/
```

---

## TypeScript/React (Frontend)

### General Guidelines

- Use functional components with hooks
- Use TypeScript for type safety
- Follow ESLint configuration
- Use meaningful component and variable names

### Component Structure

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

### File Organization

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

### Formatting

Use Prettier for automatic formatting:

```bash
npm run format
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

### Examples

```
feat(upload): add drag-and-drop file upload

Implemented drag-and-drop functionality using react-dropzone.
Supports multiple file selection in batch mode.

Closes #123
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

---

## CSS/Tailwind

### Class Organization

Order Tailwind classes consistently:

1. Layout (flex, grid, position)
2. Spacing (margin, padding)
3. Sizing (width, height)
4. Typography (font, text)
5. Visual (background, border, shadow)
6. Interactive (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* content */}
</div>
```

### Custom Classes

Use `@apply` sparingly, prefer composition:

```css
/* Prefer this */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* Over inline classes everywhere */
```

---

## API Design

### Endpoint Naming

- Use nouns, not verbs
- Use plural forms
- Use kebab-case for multi-word resources

```
GET    /api/conversions
POST   /api/conversions
GET    /api/conversions/{id}
DELETE /api/conversions/{id}
GET    /api/conversions/{id}/status
```

### Response Format

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

### Error Format

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


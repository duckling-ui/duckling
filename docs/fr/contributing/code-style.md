# Style de code

Normes et conventions de codage pour Duckling.

## Python (backend)

### Lignes directrices générales

- Suivre PEP 8
- Utiliser les annotations de type
- Longueur de ligne maximale : 100 caractères
- Utiliser des docstrings pour les fonctions et les classes

### Documentation des fonctions

```python
def convert_document(file_path: str, settings: dict) -> ConversionResult:
    """
    Convertit un document avec Docling.

    Args:
        file_path: Chemin vers le fichier document
        settings: Dictionnaire des paramètres de conversion

    Returns:
        Objet ConversionResult avec le contenu converti

    Raises:
        ValueError: Si le format de fichier n'est pas pris en charge
        IOError: Si le fichier ne peut pas être lu
    """
    pass
```

### Documentation des classes

```python
class ConverterService:
    """
    Service pour les opérations de conversion de documents.

    Ce service gère le pipeline de conversion, la file d'attente des tâches
    et l'interaction avec la bibliothèque Docling.

    Attributes:
        _job_queue: File des tâches de conversion en attente
        _max_concurrent_jobs: Nombre maximal de conversions parallèles
    """
    pass
```

### Imports

Ordonner les imports ainsi :

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

Utiliser Black pour le formatage automatique :

```bash
pip install black
black backend/
```

---

## TypeScript/React (frontend)

### Lignes directrices générales

- Composants fonctionnels avec hooks
- TypeScript pour la sûreté des types
- Respecter la configuration ESLint
- Noms de composants et de variables explicites

### Structure d’un composant

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
// React et hooks en premier
import { useState, useCallback, useEffect } from 'react';

// Bibliothèques tierces
import { motion } from 'framer-motion';
import axios from 'axios';

// Composants locaux
import { Button } from '@/components/Button';
import { useConversion } from '@/hooks/useConversion';

// Types
import type { ConversionResult } from '@/types';
```

### Formatage

Utiliser Prettier pour le formatage automatique :

```bash
npm run format
```

---

## Messages de commit {#commit-messages}

Suivre [Conventional Commits](https://www.conventionalcommits.org/) :

```
type(scope): description

[corps optionnel]

[pied de page optionnel]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bogue |
| `docs` | Modifications de documentation |
| `style` | Style de code (formatage) |
| `refactor` | Refactorisation |
| `test` | Ajout ou mise à jour de tests |
| `chore` | Tâches de maintenance |

### Exemples

```
feat(upload): ajouter le dépôt de fichiers par glisser-déposer

Fonctionnalité glisser-déposer implémentée avec react-dropzone.
Prise en charge de la sélection multiple et du dépôt de dossier dans la zone par défaut.

Closes #123

Signed-off-by: Votre Nom <votre.email@exemple.com>
```

```
fix(converter): traiter correctement les gros fichiers PDF

Problème de mémoire corrigé pour les PDF > 50 Mo en diffusant
le fichier au lieu de le charger entièrement en mémoire.
```

```
docs(readme): mettre à jour les instructions d'installation

Ajout des instructions Docker et d'une section dépannage.
```

### Signature DCO {#dco-sign-off}

Tous les commits **DOIVENT** être signés avec le [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Cela atteste que vous avez le droit de soumettre la contribution sous la licence du projet.

Ajoutez la signature à chaque commit avec `git commit -s` :

```bash
git commit -s -m "feat(upload): ajouter le dépôt de fichiers par glisser-déposer"
```

Cela ajoute une ligne `Signed-off-by:` avec votre nom et votre e-mail issus de la configuration Git. Vous pouvez aussi l’ajouter manuellement à la fin du message de commit :

```
Signed-off-by: Votre Nom <votre.email@exemple.com>
```

Les PR avec des commits non signés ne seront pas fusionnées.

---

## CSS/Tailwind

### Organisation des classes

Ordonner les classes Tailwind de façon cohérente :

1. Mise en page (flex, grid, position)
2. Espacement (margin, padding)
3. Dimensions (width, height)
4. Typographie (font, text)
5. Visuel (background, border, shadow)
6. Interactif (hover, focus)

```tsx
<div className="flex items-center gap-4 p-4 w-full text-sm bg-gray-800 rounded-lg hover:bg-gray-700">
  {/* contenu */}
</div>
```

### Classes personnalisées

Utiliser `@apply` avec parcimonie, préférer la composition :

```css
/* Préférer ceci */
.btn-primary {
  @apply px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600;
}

/* Plutôt que des classes en ligne partout */
```

---

## Conception d’API

### Nommage des points de terminaison

- Utiliser des noms, pas des verbes
- Formes plurielles
- kebab-case pour les ressources multi-mots

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

### Format d’erreur

```json
{
  "error": "ValidationError",
  "message": "Type de fichier non pris en charge",
  "details": {
    "field": "file",
    "allowed": ["pdf", "docx", "png"]
  }
}
```

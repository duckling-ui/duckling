# Installation

Ce guide couvre la configuration de Duckling pour le développement local.

## Prérequis

- Python 3.10+ (3.13 recommandé)
- Node.js 18+
- npm ou yarn
- Git

## Installation étape par étape

### 1. Cloner le dépôt

```bash
git clone https://github.com/duckling-ui/duckling.git
cd duckling
```

### 2. Configuration du backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration du frontend

```bash
cd ../frontend
npm install
```

### 4. Compiler la documentation (optionnel)

L'installation du backend inclut déjà MkDocs (`backend/requirements.txt`). Depuis la **racine du dépôt** :

```bash
cd ..  # racine du projet (où se trouve mkdocs.yml)
# Avec le venv du backend : source backend/venv/bin/activate
mkdocs build
```

La documentation utilise le même fichier **`backend/requirements.txt`** que l'API (la pile MkDocs est en tête de ce fichier).

!!! tip "Compilation automatique"
    Si MkDocs est installé (via `backend/requirements.txt`), le backend peut compiler la documentation depuis le panneau Docs de l'interface.

## Configuration de l'environnement

### Variables d'environnement du backend

Créez un fichier `.env` dans le répertoire `backend` :

```env
# Configuration Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Gestion des fichiers
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Sécurité en production"
    En production, définissez toujours une `SECRET_KEY` robuste et `DEBUG=False`.

## Vérifier l'installation

### Vérifier le backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Vous devriez voir :

```
 * Running on http://127.0.0.1:5001
```

### Vérifier le frontend

```bash
cd frontend
npm run dev
```

Vous devriez voir :

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Dépannage

### Problèmes de version Python

En cas de problèmes de version Python :

```bash
# Vérifier la version de Python
python --version

# Utiliser une version spécifique de Python
python3.13 -m venv venv
```

### Problèmes de version Node.js

```bash
# Vérifier la version de Node
node --version

# Utiliser nvm pour changer de version
nvm install 18
nvm use 18
```

### Échecs d'installation des dépendances

```bash
# Backend - mettre à jour pip
pip install --upgrade pip
pip install -r requirements.txt

# Frontend - vider le cache
rm -rf node_modules package-lock.json
npm install
```

## Prochaines étapes

- [Démarrage rapide](quickstart.md) - Apprendre les bases
- [Configuration](../user-guide/configuration.md) - Personnaliser les paramètres

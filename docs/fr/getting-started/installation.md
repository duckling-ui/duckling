# Installation

Ce guide explique comment configurer Duckling pour le développement local.

## Prérequis

- Python 3.10+ (3.13 recommandé)
- Node.js 18+
- npm ou yarn
- Git

## Installation pas à pas

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

### 4. Construire la documentation (facultatif)

L’installation du backend inclut déjà MkDocs (même `backend/requirements.txt`). Depuis la **racine du dépôt** :

```bash
cd ..  # racine du projet (où se trouve mkdocs.yml)
# Utiliser le venv du backend si vous l’avez créé : source backend/venv/bin/activate
mkdocs build
```

Les builds de documentation utilisent le même fichier **`backend/requirements.txt`** que l’API (les plugins MkDocs sont listés en haut de ce fichier).

!!! tip "Construction automatique"
    Si MkDocs est installé (via `backend/requirements.txt`), le backend peut construire la documentation lorsque vous utilisez le panneau documentation dans l’interface.

## Configuration de l’environnement

### Variables d’environnement du backend

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
    En production, définissez toujours une `SECRET_KEY` forte et `DEBUG=False`.

## Vérifier l’installation

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

### Problèmes de version de Python

En cas de problème de version de Python :

```bash
# Vérifier la version de Python
python --version

# Utiliser une version précise de Python
python3.13 -m venv venv
```

### Problèmes de version de Node.js

```bash
# Vérifier la version de Node
node --version

# Changer de version avec nvm
nvm install 18
nvm use 18
```

### Échecs d’installation des dépendances

```bash
# Backend – mettre pip à jour
pip install --upgrade pip
pip install -r requirements.txt

# Frontend – vider le cache
rm -rf node_modules package-lock.json
npm install
```

## Étapes suivantes

- [Démarrage rapide](quickstart.md) – Apprendre les bases
- [Configuration](../user-guide/configuration.md) – Personnaliser les paramètres


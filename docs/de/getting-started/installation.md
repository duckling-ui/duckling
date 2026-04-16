# Installation

Diese Anleitung beschreibt die Einrichtung von Duckling für die lokale Entwicklung.

## Voraussetzungen

- Python 3.10+ (3.13 empfohlen)
- Node.js 18+
- npm oder yarn
- Git

## Schritt-für-Schritt-Installation

### 1. Repository klonen

```bash
git clone https://github.com/duckling-ui/duckling.git
cd duckling
```

### 2. Backend-Einrichtung

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend-Einrichtung

```bash
cd ../frontend
npm install
```

### 4. Dokumentation bauen (optional)

Die Backend-Installation enthält bereits MkDocs (`backend/requirements.txt`). Vom **Repository-Stamm** aus:

```bash
cd ..  # Projektstamm (mkdocs.yml liegt hier)
# Mit Backend-venv: source backend/venv/bin/activate
mkdocs build
```

Die Dokumentation nutzt dieselbe **`backend/requirements.txt`** wie die API (MkDocs-Pakete stehen oben in der Datei).

!!! tip "Auto-Build"
    Ist MkDocs installiert (über `backend/requirements.txt`), kann das Backend die Dokumentation über das Docs-Panel in der UI bauen.

## Umgebungskonfiguration

### Backend-Umgebungsvariablen

Erstellen Sie eine `.env`-Datei im Verzeichnis `backend`:

```env
# Flask-Konfiguration
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Dateiverarbeitung
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Produktionssicherheit"
    In der Produktion immer eine starke `SECRET_KEY` setzen und `DEBUG=False`.

## Installation überprüfen

### Backend prüfen

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Sie sollten sehen:

```
 * Running on http://127.0.0.1:5001
```

### Frontend prüfen

```bash
cd frontend
npm run dev
```

Sie sollten sehen:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Fehlerbehebung

### Python-Versionsprobleme

Bei Python-Versionsproblemen:

```bash
# Python-Version prüfen
python --version

# Bestimmte Python-Version verwenden
python3.13 -m venv venv
```

### Node.js-Versionsprobleme

```bash
# Node-Version prüfen
node --version

# nvm zum Wechseln der Versionen verwenden
nvm install 18
nvm use 18
```

### Abhängigkeitsinstallationsfehler

```bash
# Backend - pip aktualisieren
pip install --upgrade pip
pip install -r requirements.txt

# Frontend - Cache leeren
rm -rf node_modules package-lock.json
npm install
```

## Nächste Schritte

- [Schnellstart](quickstart.md) - Grundlagen lernen
- [Konfiguration](../user-guide/configuration.md) - Einstellungen anpassen

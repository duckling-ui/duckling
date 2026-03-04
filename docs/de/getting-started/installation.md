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
git clone https://github.com/davidgs/duckling.git
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

Um die Dokumentation in der Duckling-UI anzuzeigen, bauen Sie die MkDocs-Site:

```bash
cd ..  # Zurück zum Projektstammverzeichnis
pip install -r requirements-docs.txt
mkdocs build
```

!!! tip "Auto-Build"
    Wenn MkDocs installiert ist, baut das Backend die Dokumentation automatisch, wenn Sie zum ersten Mal den Dokumentationsbereich in der UI öffnen.

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

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

### 2. Backend einrichten

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend einrichten

```bash
cd ../frontend
npm install
```

### 4. Dokumentation bauen (optional)

Die Backend-Installation enthält bereits MkDocs (gleiche `backend/requirements.txt`). Vom **Repository-Stamm** aus:

```bash
cd ..  # Projektstamm (hier liegt mkdocs.yml)
# Backend-venv nutzen, falls angelegt: source backend/venv/bin/activate
mkdocs build
```

Für Dokumentations-Builds gilt dieselbe **`backend/requirements.txt`** wie für die API (MkDocs-Plugins stehen oben in dieser Datei).

!!! tip "Automatischer Build"
    Ist MkDocs installiert (über `backend/requirements.txt`), kann das Backend die Dokumentation bauen, wenn Sie das Dokumentationspanel in der Benutzeroberfläche nutzen.

## Umgebungskonfiguration

### Umgebungsvariablen Backend

Legen Sie eine `.env`-Datei im Verzeichnis `backend` an:

```env
# Flask-Konfiguration
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Dateiverarbeitung
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Sicherheit in Produktion"
    In Produktion immer einen starken `SECRET_KEY` setzen und `DEBUG=False` setzen.

## Installation prüfen

### Backend prüfen

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Sie sollten etwa Folgendes sehen:

```
 * Running on http://127.0.0.1:5001
```

### Frontend prüfen

```bash
cd frontend
npm run dev
```

Sie sollten etwa Folgendes sehen:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Fehlerbehebung

### Probleme mit der Python-Version

Bei Problemen mit der Python-Version:

```bash
# Python-Version prüfen
python --version

# Bestimmte Python-Version verwenden
python3.13 -m venv venv
```

### Probleme mit der Node.js-Version

```bash
# Node-Version prüfen
node --version

# Mit nvm die Version wechseln
nvm install 18
nvm use 18
```

### Fehler bei der Abhängigkeitsinstallation

```bash
# Backend – pip aktualisieren
pip install --upgrade pip
pip install -r requirements.txt

# Frontend – Cache leeren
rm -rf node_modules package-lock.json
npm install
```

## Nächste Schritte

- [Schnellstart](quickstart.md) – Grundlagen kennenlernen
- [Konfiguration](../user-guide/configuration.md) – Einstellungen anpassen


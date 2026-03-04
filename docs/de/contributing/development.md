# Entwicklungsumgebung

Richten Sie Ihre Entwicklungsumgebung für die Mitarbeit an Duckling ein.

## Voraussetzungen

- Python 3.10+
- Node.js 18+
- Git

## Backend-Einrichtung

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Frontend-Einrichtung

```bash
cd frontend
npm install
```

## Entwicklungsserver starten

### Backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Backend läuft unter: `http://localhost:5001`

### Frontend

```bash
cd frontend
npm run dev
```

Frontend läuft unter: `http://localhost:3000`

## Projektstruktur

```
duckling/
├── backend/
│   ├── duckling.py         # Flask-Anwendungseinstieg
│   ├── config.py           # Konfiguration
│   ├── models/             # Datenbankmodelle
│   ├── routes/             # API-Endpunkte
│   ├── services/           # Geschäftslogik
│   └── tests/              # Backend-Tests
├── frontend/
│   ├── src/
│   │   ├── components/     # React-Komponenten
│   │   ├── hooks/          # Benutzerdefinierte React-Hooks
│   │   ├── services/       # API-Client
│   │   └── types/          # TypeScript-Typen
│   └── tests/              # Frontend-Tests
└── docs/                   # Dokumentation
```

## IDE-Einrichtung

### VS Code

Empfohlene Erweiterungen:

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### Einstellungen

`.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Umgebungsvariablen

Erstellen Sie `.env`-Dateien für die lokale Entwicklung:

### Backend (.env)

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DEBUG=True
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:5001/api
```

## Hot Reloading

Beide Server unterstützen Hot Reloading:

- **Backend**: Flask-Debug-Modus lädt bei Dateiänderungen automatisch neu
- **Frontend**: Vite HMR aktualisiert Komponenten ohne Seitenaktualisierung

## Debugging

### Backend (VS Code)

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "duckling.py",
        "FLASK_DEBUG": "1"
      },
      "args": ["run", "--port", "5001"],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### Frontend

Browser-DevTools mit React Developer Tools-Erweiterung verwenden.

## Häufige Aufgaben

### Abhängigkeiten aktualisieren

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Typen generieren

```bash
cd frontend
npm run generate-types  # Falls verfügbar
```

### Für Produktion bauen

```bash
# Frontend
cd frontend
npm run build

# Backend (kein Build erforderlich)
```

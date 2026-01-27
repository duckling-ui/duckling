# Development Setup

Set up your development environment for contributing to Duckling.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Git

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Frontend Setup

```bash
cd frontend
npm install
```

## Running Development Servers

### Backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Backend runs at: `http://localhost:5001`

### Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Project Structure

```
duckling/
├── backend/
│   ├── duckling.py         # Flask application entry
│   ├── config.py           # Configuration
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── tests/              # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript types
│   └── tests/              # Frontend tests
└── docs/                   # Documentation
```

## IDE Setup

### VS Code

Recommended extensions:

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### Settings

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

## Environment Variables

Create `.env` files for local development:

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

Both servers support hot reloading:

- **Backend**: Flask debug mode auto-reloads on file changes
- **Frontend**: Vite HMR updates components without page refresh

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

Use browser DevTools with React Developer Tools extension.

## Common Tasks

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Generate Types

```bash
cd frontend
npm run generate-types  # If available
```

### Build for Production

```bash
# Frontend
cd frontend
npm run build

# Backend (no build needed)
```


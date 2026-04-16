# Configuration de l’environnement de développement

Configurez votre environnement de développement pour contribuer à Duckling.

## Prérequis

- Python 3.10+
- Node.js 18+
- Git

## Configuration du backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration du frontend

```bash
cd frontend
npm install
```

## Lancer les serveurs de développement

### Backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Le backend écoute sur : `http://localhost:5001`

### Frontend

```bash
cd frontend
npm run dev
```

Le frontend écoute sur : `http://localhost:3000`

## Structure du projet

```
duckling/
├── backend/
│   ├── duckling.py         # Point d’entrée Flask
│   ├── config.py           # Configuration
│   ├── models/             # Modèles de base de données
│   ├── routes/             # Points de terminaison API
│   ├── services/           # Logique métier
│   └── tests/              # Tests backend
├── frontend/
│   ├── src/
│   │   ├── components/     # Composants React
│   │   ├── hooks/          # Hooks React personnalisés
│   │   ├── services/       # Client API
│   │   └── types/          # Types TypeScript
│   └── tests/              # Tests frontend
└── docs/                   # Documentation
```

## Configuration de l’IDE

### VS Code

Extensions recommandées :

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### Paramètres

`.vscode/settings.json` :

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

## Variables d’environnement

Créez des fichiers `.env` pour le développement local :

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

## Rechargement à chaud

Les deux serveurs prennent en charge le rechargement à chaud :

- **Backend** : le mode debug Flask recharge automatiquement lors des modifications de fichiers
- **Frontend** : le HMR de Vite met à jour les composants sans recharger la page

## Débogage

### Backend (VS Code)

`.vscode/launch.json` :

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

Utilisez les outils de développement du navigateur avec l’extension React Developer Tools.

## Tâches courantes

### Mettre à jour les dépendances

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Générer les types

```bash
cd frontend
npm run generate-types  # Si disponible
```

### Build de production

```bash
# Frontend
cd frontend
npm run build

# Backend (aucun build nécessaire)
```

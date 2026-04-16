# Configuración del entorno de desarrollo

Configure su entorno de desarrollo para contribuir a Duckling.

## Requisitos previos

- Python 3.10+
- Node.js 18+
- Git

## Configuración del backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración del frontend

```bash
cd frontend
npm install
```

## Ejecutar servidores de desarrollo

### Backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

El backend escucha en: `http://localhost:5001`

### Frontend

```bash
cd frontend
npm run dev
```

El frontend escucha en: `http://localhost:3000`

## Estructura del proyecto

```
duckling/
├── backend/
│   ├── duckling.py         # Entrada de la aplicación Flask
│   ├── config.py           # Configuración
│   ├── models/             # Modelos de base de datos
│   ├── routes/             # Endpoints de la API
│   ├── services/           # Lógica de negocio
│   └── tests/              # Pruebas del backend
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Hooks personalizados de React
│   │   ├── services/       # Cliente API
│   │   └── types/          # Tipos TypeScript
│   └── tests/              # Pruebas del frontend
└── docs/                   # Documentación
```

## Configuración del IDE

### VS Code

Extensiones recomendadas:

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

### Ajustes

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

## Variables de entorno

Cree archivos `.env` para el desarrollo local:

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

## Recarga en caliente

Ambos servidores admiten recarga en caliente:

- **Backend**: el modo de depuración de Flask recarga automáticamente al cambiar archivos
- **Frontend**: el HMR de Vite actualiza componentes sin recargar la página

## Depuración

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

Use las herramientas de desarrollo del navegador con la extensión React Developer Tools.

## Tareas habituales

### Actualizar dependencias

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Generar tipos

```bash
cd frontend
npm run generate-types  # Si está disponible
```

### Compilación de producción

```bash
# Frontend
cd frontend
npm run build

# Backend (no requiere compilación)
```

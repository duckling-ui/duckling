# Instalación

Esta guía cubre la configuración de Duckling para desarrollo local.

## Requisitos previos

- Python 3.10+ (3.13 recomendado)
- Node.js 18+
- npm o yarn
- Git

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/duckling-ui/duckling.git
cd duckling
```

### 2. Configuración del backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuración del frontend

```bash
cd ../frontend
npm install
```

### 4. Compilar documentación (opcional)

La instalación del backend ya incluye MkDocs (`backend/requirements.txt`). Desde la **raíz del repositorio**:

```bash
cd ..  # raíz del proyecto (donde está mkdocs.yml)
# Con el venv del backend: source backend/venv/bin/activate
mkdocs build
```

La documentación se construye con el mismo **`backend/requirements.txt`** que la API (el stack de MkDocs está al inicio de ese archivo).

!!! tip "Compilación automática"
    Si MkDocs está instalado (vía `backend/requirements.txt`), el backend puede compilar la documentación desde el panel de documentación en la interfaz.

## Configuración del entorno

### Variables de entorno del backend

Crea un archivo `.env` en el directorio `backend`:

```env
# Configuración de Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Manejo de archivos
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Seguridad en producción"
    En producción, siempre configura una `SECRET_KEY` segura y establece `DEBUG=False`.

## Verificar la instalación

### Comprobar el backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Deberías ver:

```
 * Running on http://127.0.0.1:5001
```

### Comprobar el frontend

```bash
cd frontend
npm run dev
```

Deberías ver:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Solución de problemas

### Problemas con la versión de Python

Si encuentras problemas con la versión de Python:

```bash
# Comprobar versión de Python
python --version

# Usar versión específica de Python
python3.13 -m venv venv
```

### Problemas con la versión de Node.js

```bash
# Comprobar versión de Node
node --version

# Usar nvm para cambiar versiones
nvm install 18
nvm use 18
```

### Fallos en la instalación de dependencias

```bash
# Backend - intentar actualizar pip
pip install --upgrade pip
pip install -r requirements.txt

# Frontend - limpiar caché
rm -rf node_modules package-lock.json
npm install
```

## Próximos pasos

- [Inicio rápido](quickstart.md) - Aprende lo básico
- [Configuración](../user-guide/configuration.md) - Personaliza los ajustes

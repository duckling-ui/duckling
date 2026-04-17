# Instalación

Esta guía explica cómo configurar Duckling para desarrollo local.

## Requisitos previos

- Python 3.10+ (se recomienda 3.13)
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

### 4. Compilar la documentación (opcional)

La instalación del backend ya incluye MkDocs (mismo `backend/requirements.txt`). Desde la **raíz del repositorio**:

```bash
cd ..  # raíz del proyecto (donde está mkdocs.yml)
# Use el venv del backend si lo creó: source backend/venv/bin/activate
mkdocs build
```

Las compilaciones de documentación usan el mismo **`backend/requirements.txt`** que la API (los plugins de MkDocs están al inicio de ese archivo).

!!! tip "Compilación automática"
    Si MkDocs está instalado (mediante `backend/requirements.txt`), el backend puede compilar la documentación cuando use el panel de documentación en la interfaz.

## Configuración del entorno

### Variables de entorno del backend

Cree un archivo `.env` en el directorio `backend`:

```env
# Configuración de Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Manejo de archivos
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Seguridad en producción"
    En producción, establezca siempre una `SECRET_KEY` segura y `DEBUG=False`.

## Comprobar la instalación

### Comprobar el backend

```bash
cd backend
source venv/bin/activate
python duckling.py
```

Debería ver algo como:

```
 * Running on http://127.0.0.1:5001
```

### Comprobar el frontend

```bash
cd frontend
npm run dev
```

Debería ver algo como:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Solución de problemas

### Problemas de versión de Python

Si tiene problemas con la versión de Python:

```bash
# Comprobar la versión de Python
python --version

# Usar una versión concreta de Python
python3.13 -m venv venv
```

### Problemas de versión de Node.js

```bash
# Comprobar la versión de Node
node --version

# Cambiar de versión con nvm
nvm install 18
nvm use 18
```

### Fallos al instalar dependencias

```bash
# Backend: actualizar pip
pip install --upgrade pip
pip install -r requirements.txt

# Frontend: limpiar caché
rm -rf node_modules package-lock.json
npm install
```

## Próximos pasos

- [Inicio rápido](quickstart.md) – Aprender lo básico
- [Configuración](../user-guide/configuration.md) – Personalizar ajustes


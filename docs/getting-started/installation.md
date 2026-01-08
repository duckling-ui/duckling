# Installation

This guide covers setting up Duckling for local development.

## Prerequisites

- Python 3.10+ (3.13 recommended)
- Node.js 18+
- npm or yarn
- Git

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/davidgs/duckling.git
cd duckling
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Build Documentation (Optional)

To view documentation within the Duckling UI, build the MkDocs site:

```bash
cd ..  # Return to project root
pip install -r requirements-docs.txt
mkdocs build
```

!!! tip "Auto-Build"
    If MkDocs is installed, the backend will automatically build the documentation when you first open the docs panel in the UI.

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# File Handling
MAX_CONTENT_LENGTH=104857600  # 100MB
```

!!! warning "Production Security"
    In production, always set a strong `SECRET_KEY` and set `DEBUG=False`.

## Verifying Installation

### Check Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5001
```

### Check Frontend

```bash
cd frontend
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

## Troubleshooting

### Python Version Issues

If you encounter Python version issues:

```bash
# Check Python version
python --version

# Use specific Python version
python3.13 -m venv venv
```

### Node.js Version Issues

```bash
# Check Node version
node --version

# Use nvm to switch versions
nvm install 18
nvm use 18
```

### Dependency Installation Failures

```bash
# Backend - try upgrading pip
pip install --upgrade pip
pip install -r requirements.txt

# Frontend - clear cache
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- [Quick Start](quickstart.md) - Learn the basics
- [Configuration](../user-guide/configuration.md) - Customize settings


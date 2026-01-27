# Duckling Backend Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
# Note: libgl1-mesa-glx replaced with libgl1 for newer Debian versions
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender1 \
  libgomp1 \
  poppler-utils \
  tesseract-ocr \
  && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development

COPY requirements.txt .
RUN pip install -r requirements.txt

# Docs build tooling (needed for /api/docs/build inside the container when docs are mounted)
COPY requirements-docs.txt .
RUN pip install -r requirements-docs.txt

COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/outputs /app/data

EXPOSE 5001

CMD ["python", "duckling.py"]

# Production stage
FROM base AS production

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

# Docs build tooling (needed for /api/docs/build inside the container when docs are mounted)
COPY requirements-docs.txt .
RUN pip install -r requirements-docs.txt

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /app/uploads /app/outputs /app/data \
  && chmod -R 755 /app/uploads /app/outputs /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/api/health || exit 1

# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "300", "duckling:app"]
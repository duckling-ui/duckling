# Duckling Backend Dockerfile
# Multi-stage build for optimized production image

ARG PYTHON_BASE_IMAGE=python:3.11-slim-bookworm
FROM ${PYTHON_BASE_IMAGE} AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
# Note: libgl1-mesa-glx replaced with libgl1 for newer Debian versions
# Upgrade base image OS packages (openssl, gnutls, etc.) for Trivy publish gates.
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
  build-essential \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender1 \
  libgomp1 \
  poppler-utils \
  tesseract-ocr \
  && rm -rf /var/lib/apt/lists/*

# Python dependencies for production; drop compilers after pip to reduce CI disk use.
FROM base AS python-deps
COPY requirements.txt requirements-docling-serve.txt ./
COPY scripts/harden_python_packages.py scripts/harden_python_packages.py
RUN pip install -r requirements.txt -r requirements-docling-serve.txt \
  && python scripts/harden_python_packages.py \
  && apt-get purge -y --auto-remove build-essential \
  && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

# Development stage
FROM base AS development

COPY requirements.txt requirements-docling-serve.txt ./
COPY scripts/harden_python_packages.py scripts/harden_python_packages.py
RUN pip install -r requirements.txt -r requirements-docling-serve.txt \
  && python scripts/harden_python_packages.py

COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/outputs /app/data

EXPOSE 5001

CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "5001"]

# Production stage (reuses python-deps; no second pip install)
FROM python-deps AS production

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /app/uploads /app/outputs /app/data \
  && chmod -R 755 /app/uploads /app/outputs /app/data \
  && chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001
# Health check without extra runtime tools
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys, urllib.request; urllib.request.urlopen('http://localhost:5001/api/health', timeout=5); sys.exit(0)" || exit 1
# Entrypoint: 1 Gunicorn worker for local in-memory jobs; multi-worker for RQ/Ray (issue #67 B)
ENTRYPOINT ["/app/entrypoint.sh"]

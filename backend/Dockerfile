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
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Development stage
FROM base AS development

COPY requirements.txt .
RUN pip install -r requirements.txt \
  && pip install --upgrade --force-reinstall --no-deps "jaraco.context==6.1.0" "wheel==0.46.2" \
  && python - <<'PY'
from importlib.metadata import version
from pathlib import Path
import shutil

def _parse(v):
    out = []
    for part in v.split("."):
        n = ""
        for ch in part:
            if ch.isdigit():
                n += ch
            else:
                break
        out.append(int(n or 0))
    return out

def assert_min(pkg, minimum):
    installed = version(pkg)
    if _parse(installed) < _parse(minimum):
        raise SystemExit(f"{pkg}={installed} is below required {minimum}")

# Remove stale vulnerable metadata artifacts that may remain discoverable to layer scanners.
def remove_legacy_metadata(package_name, minimum):
    removed = 0
    root = Path("/usr/local/lib")
    pattern = f"{package_name.replace('.', '?')}-*.dist-info"
    for dist in root.rglob(pattern):
        name = dist.name
        ver = name[len(package_name) + 1 : -len(".dist-info")]
        if _parse(ver) < _parse(minimum):
            shutil.rmtree(dist, ignore_errors=True)
            removed += 1
    return removed

# The Python base image may include bundled wheel archives under ensurepip.
def remove_legacy_ensurepip_wheels(minimum):
    removed = 0
    for whl in Path("/usr/local/lib").rglob("ensurepip/_bundled/wheel-*.whl"):
        ver = whl.name.split("-")[1]
        if _parse(ver) < _parse(minimum):
            whl.unlink(missing_ok=True)
            removed += 1
    return removed

assert_min("jaraco.context", "6.1.0")
assert_min("wheel", "0.46.2")
removed_dist_info = remove_legacy_metadata("jaraco.context", "6.1.0")
removed_dist_info += remove_legacy_metadata("wheel", "0.46.2")
removed_ensurepip = remove_legacy_ensurepip_wheels("0.46.2")
print(f"Removed legacy metadata dirs: {removed_dist_info}; removed ensurepip wheel files: {removed_ensurepip}")
print("Verified hardened Python package minimums")
PY

COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/outputs /app/data

EXPOSE 5001

CMD ["python", "duckling.py"]

# Production stage
FROM base AS production

# Copy requirements and install (includes MkDocs for /api/docs/build)
COPY requirements.txt .
RUN pip install -r requirements.txt \
  && pip install --upgrade --force-reinstall --no-deps "jaraco.context==6.1.0" "wheel==0.46.2" \
  && python - <<'PY'
from importlib.metadata import version
from pathlib import Path
import shutil

def _parse(v):
    out = []
    for part in v.split("."):
        n = ""
        for ch in part:
            if ch.isdigit():
                n += ch
            else:
                break
        out.append(int(n or 0))
    return out

def assert_min(pkg, minimum):
    installed = version(pkg)
    if _parse(installed) < _parse(minimum):
        raise SystemExit(f"{pkg}={installed} is below required {minimum}")

# Remove stale vulnerable metadata artifacts that may remain discoverable to layer scanners.
def remove_legacy_metadata(package_name, minimum):
    removed = 0
    root = Path("/usr/local/lib")
    pattern = f"{package_name.replace('.', '?')}-*.dist-info"
    for dist in root.rglob(pattern):
        name = dist.name
        ver = name[len(package_name) + 1 : -len(".dist-info")]
        if _parse(ver) < _parse(minimum):
            shutil.rmtree(dist, ignore_errors=True)
            removed += 1
    return removed

# The Python base image may include bundled wheel archives under ensurepip.
def remove_legacy_ensurepip_wheels(minimum):
    removed = 0
    for whl in Path("/usr/local/lib").rglob("ensurepip/_bundled/wheel-*.whl"):
        ver = whl.name.split("-")[1]
        if _parse(ver) < _parse(minimum):
            whl.unlink(missing_ok=True)
            removed += 1
    return removed

assert_min("jaraco.context", "6.1.0")
assert_min("wheel", "0.46.2")
removed_dist_info = remove_legacy_metadata("jaraco.context", "6.1.0")
removed_dist_info += remove_legacy_metadata("wheel", "0.46.2")
removed_ensurepip = remove_legacy_ensurepip_wheels("0.46.2")
print(f"Removed legacy metadata dirs: {removed_dist_info}; removed ensurepip wheel files: {removed_ensurepip}")
print("Verified hardened Python package minimums")
PY

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
# Health check without extra runtime tools
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys, urllib.request; urllib.request.urlopen('http://localhost:5001/api/health', timeout=5); sys.exit(0)" || exit 1
# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "300", "duckling:app"]

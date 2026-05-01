#!/bin/bash

# The MIT License (MIT)
#  *
#  * Copyright (c) 2022-present David G. Simmons
#  *
#  * Permission is hereby granted, free of charge, to any person obtaining a copy
#  * of this software and associated documentation files (the "Software"), to deal
#  * in the Software without restriction, including without limitation the rights
#  * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  * copies of the Software, and to permit persons to whom the Software is
#  * furnished to do so, subject to the following conditions:
#  *
#  * The above copyright notice and this permission notice shall be included in all
#  * copies or substantial portions of the Software.
#  *
#  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  * SOFTWARE.

# Build and optionally push Duckling Docker images
#
# Usage:
#   ./scripts/docker-build.sh                    # Build only
#   ./scripts/docker-build.sh --push             # Build and push to Docker Hub
#   ./scripts/docker-build.sh --push --registry ghcr.io/username  # Push to custom registry
#   ./scripts/docker-build.sh --version 1.0.0   # Build with specific version tag
#   ./scripts/docker-build.sh --skip-docs       # Skip documentation build
#
# Local iteration (much faster than CI multi-arch): build one platform only, skip SBOM/provenance:
#   VERSION=$(node -p "require('./frontend/package.json').version")
#   ./scripts/docker-build.sh --version "$VERSION" --multi-platform --platform linux/amd64 --skip-docs
# Apple Silicon hosts often want:
#   ./scripts/docker-build.sh --version "$VERSION" --multi-platform --platform linux/arm64 --skip-docs
# Env override: DUCKLING_BUILD_PLATFORMS=linux/amd64 (comma-separated)

set -euo pipefail

# Default values
REGISTRY=""
VERSION="latest"
PUSH=false
PLATFORMS="${DUCKLING_BUILD_PLATFORMS:-linux/amd64,linux/arm64}"
BUILD_MULTI_PLATFORM=false
SKIP_DOCS=false
ENABLE_SBOM=false
ENABLE_PROVENANCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        --registry)
            REGISTRY="$2/"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --multi-platform)
            BUILD_MULTI_PLATFORM=true
            shift
            ;;
        --platform)
            PLATFORMS="$2"
            shift 2
            ;;
        --skip-docs)
            SKIP_DOCS=true
            shift
            ;;
        --sbom)
            ENABLE_SBOM=true
            shift
            ;;
        --provenance)
            ENABLE_PROVENANCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_step() {
    echo -e "${YELLOW}==> $1${NC}"
}

run_cmd() {
    echo "+ $*"
    "$@"
}

die() {
    echo -e "${RED}✗ $1${NC}" >&2
    exit 1
}

echo -e "${GREEN}=== Duckling Docker Build ===${NC}"
echo "Registry: ${REGISTRY:-local}"
echo "Version: $VERSION"
echo "Push: $PUSH"
echo "SBOM: $ENABLE_SBOM"
echo "Provenance: $ENABLE_PROVENANCE"
echo "Platforms: $PLATFORMS"
echo "Buildx progress: plain"
echo ""

# Force non-TTY step output so long builds emit continuous logs.
export BUILDKIT_PROGRESS=plain

# Navigate to project root
cd "$(dirname "$0")/.."

# Fail fast when Docker Desktop/daemon is unavailable.
if ! docker version >/dev/null 2>&1; then
    die "Docker daemon is not reachable. Start Docker Desktop and retry."
fi

# Build documentation first (unless skipped)
if [ "$SKIP_DOCS" = false ]; then
    log_step "Building documentation"

    # Update version in mkdocs.yml from package.json or GitHub
    if [ -f "scripts/get_version.py" ]; then
        if command -v python3 &> /dev/null; then
            python3 scripts/get_version.py >/dev/null 2>&1 || echo -e "${YELLOW}⚠ Could not update version, continuing with existing version${NC}"
        elif command -v python &> /dev/null; then
            python scripts/get_version.py >/dev/null 2>&1 || echo -e "${YELLOW}⚠ Could not update version, continuing with existing version${NC}"
        fi
    fi

    # Check if mkdocs is available
    if command -v mkdocs &> /dev/null; then
        # Build docs with full output for CI visibility
        if mkdocs build; then
            echo -e "${GREEN}✓ Documentation built${NC}"
        else
            # Even with warnings, check if build succeeded
            if [ -f "site/index.html" ]; then
                echo -e "${GREEN}✓ Documentation built (with warnings)${NC}"
            fi
        fi
        # Copy sitemap.xml to each language directory for SEO crawlers
        # Note: English (default locale) is at site root, not site/en/
        if [ -f "site/sitemap.xml" ]; then
            # Copy to non-default language directories (es, fr, de)
            for lang in es fr de; do
                lang_dir="site/$lang"
                if [ -d "$lang_dir" ]; then
                    cp site/sitemap.xml "$lang_dir/sitemap.xml"
                fi
            done
            # For English, ensure sitemap.xml is accessible at /en/sitemap.xml
            # Create site/en/ directory if it doesn't exist (for compatibility)
            if [ ! -d "site/en" ]; then
                mkdir -p site/en
            fi
            cp site/sitemap.xml site/en/sitemap.xml
        fi
    elif [ -f "backend/requirements.txt" ]; then
        # Try to install mkdocs (full backend stack) and build
        echo "MkDocs not found, attempting to install..."
        pip install -q -r backend/requirements.txt 2>/dev/null || {
            echo -e "${YELLOW}⚠ Could not install MkDocs. Checking for existing site...${NC}"
        }

        if command -v mkdocs &> /dev/null; then
            mkdocs build || true
            echo -e "${GREEN}✓ Documentation built${NC}"
        fi
    fi

    # Verify site directory exists
    if [ -d "site" ] && [ -f "site/index.html" ]; then
        echo -e "${GREEN}✓ Documentation site ready${NC}"
    else
        echo -e "${YELLOW}⚠ Documentation site not found. Docs may not work in Docker.${NC}"
        echo "  Run 'mkdocs build' manually or install deps: pip install -r backend/requirements.txt"
    fi
    echo ""
fi

# Build backend
log_step "Building backend image (started $(date -u +"%Y-%m-%dT%H:%M:%SZ"))"
run_cmd docker buildx inspect --bootstrap >/dev/null
BUILDX_FLAGS=()
if [ "$ENABLE_SBOM" = true ]; then
    BUILDX_FLAGS+=(--sbom=true)
fi
if [ "$ENABLE_PROVENANCE" = true ]; then
    BUILDX_FLAGS+=(--provenance=true)
fi
BUILDX_OUTPUT_FLAGS=()
if [ "$PUSH" = true ]; then
    BUILDX_OUTPUT_FLAGS+=(--push)
elif [ "${PLATFORMS#*,}" != "$PLATFORMS" ]; then
    echo -e "${YELLOW}⚠ Multi-arch build without --push will only populate build cache (no local image load).${NC}"
else
    # Buildx docker exporter (--load) cannot export attestations; avoid hard-fail in local/CI rehearsal builds.
    if [ "$ENABLE_SBOM" = true ] || [ "$ENABLE_PROVENANCE" = true ]; then
        echo -e "${YELLOW}⚠ --load is incompatible with --sbom/--provenance; disabling attestations for local image load.${NC}"
        BUILDX_FLAGS=()
    fi
    BUILDX_OUTPUT_FLAGS+=(--load)
fi
BACKEND_LABELS=(
    --label "org.opencontainers.image.source=https://github.com/duckling-ui/duckling"
    --label "org.opencontainers.image.title=duckling-backend"
    --label "org.opencontainers.image.version=${VERSION}"
)
if [ "$BUILD_MULTI_PLATFORM" = true ]; then
    run_cmd docker buildx build \
        --platform $PLATFORMS \
        --progress=plain \
        --target production \
        "${BACKEND_LABELS[@]}" \
        "${BUILDX_FLAGS[@]+"${BUILDX_FLAGS[@]}"}" \
        -t "${REGISTRY}duckling-backend:${VERSION}" \
        -t "${REGISTRY}duckling-backend:latest" \
        "${BUILDX_OUTPUT_FLAGS[@]+"${BUILDX_OUTPUT_FLAGS[@]}"}" \
        ./backend
else
    run_cmd docker build \
        --progress=plain \
        --target production \
        "${BACKEND_LABELS[@]}" \
        -t "${REGISTRY}duckling-backend:${VERSION}" \
        -t "${REGISTRY}duckling-backend:latest" \
        ./backend
fi
echo -e "${GREEN}✓ Backend image built (finished $(date -u +"%Y-%m-%dT%H:%M:%SZ"))${NC}"

# Build frontend
log_step "Building frontend image (started $(date -u +"%Y-%m-%dT%H:%M:%SZ"))"
FRONTEND_LABELS=(
    --label "org.opencontainers.image.source=https://github.com/duckling-ui/duckling"
    --label "org.opencontainers.image.title=duckling-frontend"
    --label "org.opencontainers.image.version=${VERSION}"
)
if [ "$BUILD_MULTI_PLATFORM" = true ]; then
    run_cmd docker buildx build \
        --platform $PLATFORMS \
        --progress=plain \
        --target production \
        "${FRONTEND_LABELS[@]}" \
        "${BUILDX_FLAGS[@]+"${BUILDX_FLAGS[@]}"}" \
        -t "${REGISTRY}duckling-frontend:${VERSION}" \
        -t "${REGISTRY}duckling-frontend:latest" \
        "${BUILDX_OUTPUT_FLAGS[@]+"${BUILDX_OUTPUT_FLAGS[@]}"}" \
        ./frontend
else
    run_cmd docker build \
        --progress=plain \
        --target production \
        -t "${REGISTRY}duckling-frontend:${VERSION}" \
        -t "${REGISTRY}duckling-frontend:latest" \
        ./frontend
fi
echo -e "${GREEN}✓ Frontend image built (finished $(date -u +"%Y-%m-%dT%H:%M:%SZ"))${NC}"

# Push if requested (for non-multi-platform builds)
if [ "$PUSH" = true ] && [ "$BUILD_MULTI_PLATFORM" = false ]; then
    echo -e "${YELLOW}Pushing images...${NC}"
    run_cmd docker push "${REGISTRY}duckling-backend:${VERSION}"
    run_cmd docker push "${REGISTRY}duckling-backend:latest"
    run_cmd docker push "${REGISTRY}duckling-frontend:${VERSION}"
    run_cmd docker push "${REGISTRY}duckling-frontend:latest"
    echo -e "${GREEN}✓ Images pushed${NC}"
fi

echo ""
echo -e "${GREEN}=== Build Complete ===${NC}"
echo "Images:"
echo "  - ${REGISTRY}duckling-backend:${VERSION}"
echo "  - ${REGISTRY}duckling-frontend:${VERSION}"
echo ""
echo "To run locally:"
echo "  docker-compose up -d"
echo ""
echo "To run with pre-built images:"
echo "  docker-compose -f docker-compose.prebuilt.yml up -d"

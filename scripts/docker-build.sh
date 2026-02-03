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

set -e

# Default values
REGISTRY=""
VERSION="latest"
PUSH=false
PLATFORMS="linux/amd64,linux/arm64"
BUILD_MULTI_PLATFORM=false
SKIP_DOCS=false

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
        --skip-docs)
            SKIP_DOCS=true
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

echo -e "${GREEN}=== Duckling Docker Build ===${NC}"
echo "Registry: ${REGISTRY:-local}"
echo "Version: $VERSION"
echo "Push: $PUSH"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Build documentation first (unless skipped)
if [ "$SKIP_DOCS" = false ]; then
    echo -e "${YELLOW}Building documentation...${NC}"

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
        # Build docs (ignore warnings about missing screenshots)
        if mkdocs build 2>&1 | grep -v "WARNING"; then
            echo -e "${GREEN}✓ Documentation built${NC}"
        else
            # Even with warnings, check if build succeeded
            if [ -f "site/index.html" ]; then
                echo -e "${GREEN}✓ Documentation built (with warnings)${NC}"
            fi
        fi
        # Copy versions.json to site directory if it exists
        if [ -f "docs/versions.json" ] && [ -d "site" ]; then
            cp docs/versions.json site/versions.json
        fi
        # Copy sitemap.xml to each language directory for SEO crawlers
        if [ -f "site/sitemap.xml" ]; then
            for lang_dir in site/{en,es,fr,de}; do
                if [ -d "$lang_dir" ]; then
                    cp site/sitemap.xml "$lang_dir/sitemap.xml"
                fi
            done
        fi
    elif [ -f "requirements-docs.txt" ]; then
        # Try to install mkdocs and build
        echo "MkDocs not found, attempting to install..."
        pip install -q -r requirements-docs.txt 2>/dev/null || {
            echo -e "${YELLOW}⚠ Could not install MkDocs. Checking for existing site...${NC}"
        }

        if command -v mkdocs &> /dev/null; then
            mkdocs build 2>&1 | grep -v "WARNING" || true
            echo -e "${GREEN}✓ Documentation built${NC}"
        fi
    fi

    # Verify site directory exists
    if [ -d "site" ] && [ -f "site/index.html" ]; then
        echo -e "${GREEN}✓ Documentation site ready${NC}"
    else
        echo -e "${YELLOW}⚠ Documentation site not found. Docs may not work in Docker.${NC}"
        echo "  Run 'mkdocs build' manually or install mkdocs: pip install -r requirements-docs.txt"
    fi
    echo ""
fi

# Build backend
echo -e "${YELLOW}Building backend image...${NC}"
if [ "$BUILD_MULTI_PLATFORM" = true ]; then
    docker buildx build \
        --platform $PLATFORMS \
        --target production \
        -t "${REGISTRY}duckling-backend:${VERSION}" \
        -t "${REGISTRY}duckling-backend:latest" \
        ${PUSH:+--push} \
        ./backend
else
    docker build \
        --target production \
        -t "${REGISTRY}duckling-backend:${VERSION}" \
        -t "${REGISTRY}duckling-backend:latest" \
        ./backend
fi
echo -e "${GREEN}✓ Backend image built${NC}"

# Build frontend
echo -e "${YELLOW}Building frontend image...${NC}"
if [ "$BUILD_MULTI_PLATFORM" = true ]; then
    docker buildx build \
        --platform $PLATFORMS \
        --target production \
        -t "${REGISTRY}duckling-frontend:${VERSION}" \
        -t "${REGISTRY}duckling-frontend:latest" \
        ${PUSH:+--push} \
        ./frontend
else
    docker build \
        --target production \
        -t "${REGISTRY}duckling-frontend:${VERSION}" \
        -t "${REGISTRY}duckling-frontend:latest" \
        ./frontend
fi
echo -e "${GREEN}✓ Frontend image built${NC}"

# Push if requested (for non-multi-platform builds)
if [ "$PUSH" = true ] && [ "$BUILD_MULTI_PLATFORM" = false ]; then
    echo -e "${YELLOW}Pushing images...${NC}"
    docker push "${REGISTRY}duckling-backend:${VERSION}"
    docker push "${REGISTRY}duckling-backend:latest"
    docker push "${REGISTRY}duckling-frontend:${VERSION}"
    docker push "${REGISTRY}duckling-frontend:latest"
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

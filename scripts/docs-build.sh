#!/usr/bin/env bash

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

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/venv"
MKDOCS_BIN="$VENV_DIR/bin/mkdocs"
PYTHON_BIN="$VENV_DIR/bin/python"

if [[ -x "$MKDOCS_BIN" ]]; then
  echo "Using MkDocs from: $MKDOCS_BIN"
else
  echo "MkDocs venv not found at $VENV_DIR"
  echo "Creating venv and installing docs dependencies from requirements-docs.txt..."
  python3 -m venv "$VENV_DIR"
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -r requirements-docs.txt
fi

# Update version in mkdocs.yml from package.json or GitHub
echo "Updating version in mkdocs.yml..."
"$PYTHON_BIN" "$ROOT_DIR/scripts/get_version.py" || {
  echo "Warning: Could not update version, continuing with existing version"
}

# Build docs
"$MKDOCS_BIN" build --strict

# Copy versions.json to site directory if it exists in docs
if [ -f "$ROOT_DIR/docs/versions.json" ] && [ -d "$ROOT_DIR/site" ]; then
  cp "$ROOT_DIR/docs/versions.json" "$ROOT_DIR/site/versions.json"
  echo "Copied versions.json to site directory"
fi

# Copy sitemap.xml to each language directory for SEO crawlers
if [ -f "$ROOT_DIR/site/sitemap.xml" ]; then
  for lang_dir in "$ROOT_DIR/site"/{en,es,fr,de}; do
    if [ -d "$lang_dir" ]; then
      cp "$ROOT_DIR/site/sitemap.xml" "$lang_dir/sitemap.xml"
      echo "Copied sitemap.xml to $lang_dir"
    fi
  done
fi



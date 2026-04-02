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
  echo "Creating venv and installing dependencies from backend/requirements.txt..."
  python3 -m venv "$VENV_DIR"
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -r "$ROOT_DIR/backend/requirements.txt"
fi

# Update version in mkdocs.yml from package.json or GitHub
echo "Updating version in mkdocs.yml..."
"$PYTHON_BIN" "$ROOT_DIR/scripts/get_version.py" || {
  echo "Warning: Could not update version, continuing with existing version"
}

# Build docs
"$MKDOCS_BIN" build --strict

# Copy sitemap.xml to each language directory for SEO crawlers
# Note: English (default locale) is at site root, not site/en/
if [ -f "$ROOT_DIR/site/sitemap.xml" ]; then
  # Copy to non-default language directories (es, fr, de)
  for lang in es fr de; do
    lang_dir="$ROOT_DIR/site/$lang"
    if [ -d "$lang_dir" ]; then
      cp "$ROOT_DIR/site/sitemap.xml" "$lang_dir/sitemap.xml"
      echo "Copied sitemap.xml to $lang_dir"
    fi
  done
  # For English, ensure sitemap.xml is accessible at /en/sitemap.xml
  # Create site/en/ directory if it doesn't exist (for compatibility)
  en_dir="$ROOT_DIR/site/en"
  if [ ! -d "$en_dir" ]; then
    mkdir -p "$en_dir"
    echo "Created site/en directory for compatibility"
  fi
  cp "$ROOT_DIR/site/sitemap.xml" "$en_dir/sitemap.xml"
  echo "Copied sitemap.xml to site/en (for /en/sitemap.xml requests)"
fi



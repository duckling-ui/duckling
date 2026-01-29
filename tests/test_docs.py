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

"""
Test suite for MkDocs documentation build.

This test ensures the documentation builds successfully without errors.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def test_mkdocs_config_exists():
    """Test that mkdocs.yml configuration file exists."""
    config_path = PROJECT_ROOT / "mkdocs.yml"
    assert config_path.exists(), "mkdocs.yml configuration file not found"


def test_docs_directory_exists():
    """Test that docs directory exists."""
    docs_path = PROJECT_ROOT / "docs"
    assert docs_path.exists(), "docs directory not found"
    assert docs_path.is_dir(), "docs is not a directory"


def test_docs_index_exists():
    """Test that docs/index.md exists."""
    index_path = PROJECT_ROOT / "docs" / "index.md"
    assert index_path.exists(), "docs/index.md not found"


def test_required_docs_sections_exist():
    """Test that all required documentation sections exist."""
    required_sections = [
        "docs/getting-started/index.md",
        "docs/getting-started/installation.md",
        "docs/getting-started/quickstart.md",
        "docs/getting-started/docker.md",
        "docs/user-guide/index.md",
        "docs/user-guide/features.md",
        "docs/user-guide/formats.md",
        "docs/user-guide/configuration.md",
        "docs/api/index.md",
        "docs/api/conversion.md",
        "docs/api/settings.md",
        "docs/api/history.md",
        "docs/architecture/index.md",
        "docs/architecture/overview.md",
        "docs/architecture/components.md",
        "docs/architecture/diagrams.md",
        "docs/deployment/index.md",
        "docs/deployment/production.md",
        "docs/deployment/scaling.md",
        "docs/deployment/security.md",
        "docs/contributing/index.md",
        "docs/contributing/development.md",
        "docs/contributing/code-style.md",
        "docs/contributing/testing.md",
        "docs/contributing/code-of-conduct.md",
        "docs/changelog.md",
    ]

    for section in required_sections:
        section_path = PROJECT_ROOT / section
        assert section_path.exists(), f"Required documentation section not found: {section}"

    # Spanish documentation (initial rollout)
    required_es_sections = [
        "docs/es/index.md",
        "docs/es/getting-started/index.md",
        "docs/es/getting-started/installation.md",
        "docs/es/getting-started/quickstart.md",
        "docs/es/getting-started/docker.md",
        "docs/es/user-guide/index.md",
        "docs/es/user-guide/features.md",
        "docs/es/user-guide/formats.md",
        "docs/es/user-guide/configuration.md",
        "docs/es/user-guide/screenshots.md",
        "docs/es/api/index.md",
        "docs/es/api/conversion.md",
        "docs/es/api/settings.md",
        "docs/es/api/history.md",
        "docs/es/architecture/index.md",
        "docs/es/architecture/overview.md",
        "docs/es/architecture/components.md",
        "docs/es/architecture/diagrams.md",
        "docs/es/deployment/index.md",
        "docs/es/deployment/production.md",
        "docs/es/deployment/scaling.md",
        "docs/es/deployment/security.md",
        "docs/es/contributing/index.md",
        "docs/es/contributing/development.md",
        "docs/es/contributing/code-style.md",
        "docs/es/contributing/testing.md",
        "docs/es/contributing/code-of-conduct.md",
        "docs/es/changelog.md",
    ]

    for section in required_es_sections:
        section_path = PROJECT_ROOT / section
        assert section_path.exists(), f"Required Spanish documentation section not found: {section}"

    # French documentation (scaffold)
    required_fr_sections = [
        "docs/fr/index.md",
        "docs/fr/getting-started/index.md",
        "docs/fr/getting-started/installation.md",
        "docs/fr/getting-started/quickstart.md",
        "docs/fr/getting-started/docker.md",
        "docs/fr/user-guide/index.md",
        "docs/fr/user-guide/features.md",
        "docs/fr/user-guide/formats.md",
        "docs/fr/user-guide/configuration.md",
        "docs/fr/user-guide/screenshots.md",
        "docs/fr/api/index.md",
        "docs/fr/api/conversion.md",
        "docs/fr/api/settings.md",
        "docs/fr/api/history.md",
        "docs/fr/architecture/index.md",
        "docs/fr/architecture/overview.md",
        "docs/fr/architecture/components.md",
        "docs/fr/architecture/diagrams.md",
        "docs/fr/deployment/index.md",
        "docs/fr/deployment/production.md",
        "docs/fr/deployment/scaling.md",
        "docs/fr/deployment/security.md",
        "docs/fr/contributing/index.md",
        "docs/fr/contributing/development.md",
        "docs/fr/contributing/code-style.md",
        "docs/fr/contributing/testing.md",
        "docs/fr/contributing/code-of-conduct.md",
        "docs/fr/changelog.md",
    ]

    for section in required_fr_sections:
        section_path = PROJECT_ROOT / section
        assert section_path.exists(), f"Required French documentation section not found: {section}"

    # German documentation (scaffold)
    required_de_sections = [
        "docs/de/index.md",
        "docs/de/getting-started/index.md",
        "docs/de/getting-started/installation.md",
        "docs/de/getting-started/quickstart.md",
        "docs/de/getting-started/docker.md",
        "docs/de/user-guide/index.md",
        "docs/de/user-guide/features.md",
        "docs/de/user-guide/formats.md",
        "docs/de/user-guide/configuration.md",
        "docs/de/user-guide/screenshots.md",
        "docs/de/api/index.md",
        "docs/de/api/conversion.md",
        "docs/de/api/settings.md",
        "docs/de/api/history.md",
        "docs/de/architecture/index.md",
        "docs/de/architecture/overview.md",
        "docs/de/architecture/components.md",
        "docs/de/architecture/diagrams.md",
        "docs/de/deployment/index.md",
        "docs/de/deployment/production.md",
        "docs/de/deployment/scaling.md",
        "docs/de/deployment/security.md",
        "docs/de/contributing/index.md",
        "docs/de/contributing/development.md",
        "docs/de/contributing/code-style.md",
        "docs/de/contributing/testing.md",
        "docs/de/contributing/code-of-conduct.md",
        "docs/de/changelog.md",
    ]

    for section in required_de_sections:
        section_path = PROJECT_ROOT / section
        assert section_path.exists(), f"Required German documentation section not found: {section}"


def test_docs_assets_exist():
    """Test that documentation assets exist."""
    required_assets = [
        "docs/stylesheets/extra.css",
        "docs/javascripts/mathjax.js",
        "docs/includes/abbreviations.md",
    ]

    for asset in required_assets:
        asset_path = PROJECT_ROOT / asset
        assert asset_path.exists(), f"Required asset not found: {asset}"


def test_requirements_docs_exists():
    """Test that requirements-docs.txt exists."""
    req_path = PROJECT_ROOT / "requirements-docs.txt"
    assert req_path.exists(), "requirements-docs.txt not found"


def test_requirements_docs_content():
    """Test that requirements-docs.txt contains required packages."""
    req_path = PROJECT_ROOT / "requirements-docs.txt"
    content = req_path.read_text()

    required_packages = ["mkdocs", "mkdocs-material"]
    for package in required_packages:
        assert package in content, f"Required package '{package}' not in requirements-docs.txt"


@pytest.mark.skipif(
    not os.environ.get("TEST_MKDOCS_BUILD"),
    reason="Set TEST_MKDOCS_BUILD=1 to run mkdocs build test"
)
def test_mkdocs_build():
    """Test that mkdocs builds successfully.

    This test is skipped by default because it requires mkdocs to be installed.
    Set TEST_MKDOCS_BUILD=1 to run this test.
    """
    # Prefer the repo-local MkDocs venv if present
    mkdocs_python = PROJECT_ROOT / "venv" / "bin" / "python"
    python_exe = str(mkdocs_python) if mkdocs_python.exists() else sys.executable

    result = subprocess.run(
        [python_exe, "-m", "mkdocs", "build", "--strict"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"mkdocs build failed:\n{result.stderr}"

    # Ensure Spanish build output exists under site/es/
    assert (PROJECT_ROOT / "site" / "index.html").exists(), "Expected site/index.html to exist"
    assert (PROJECT_ROOT / "site" / "es" / "index.html").exists(), "Expected site/es/index.html to exist"
    assert (PROJECT_ROOT / "site" / "fr" / "index.html").exists(), "Expected site/fr/index.html to exist"
    assert (PROJECT_ROOT / "site" / "de" / "index.html").exists(), "Expected site/de/index.html to exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


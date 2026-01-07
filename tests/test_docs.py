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
        "docs/changelog.md",
    ]

    for section in required_sections:
        section_path = PROJECT_ROOT / section
        assert section_path.exists(), f"Required documentation section not found: {section}"


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
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"mkdocs build failed:\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


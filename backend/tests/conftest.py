"""Pytest configuration and fixtures."""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from duckling import create_app
from config import TestingConfig
from models.database import init_db, Base, engine


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)

    with app.app_context():
        init_db()

    yield app

    # Cleanup
    if TestingConfig.DATABASE_PATH.exists():
        TestingConfig.DATABASE_PATH.unlink()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_content():
    """Create minimal PDF content for testing."""
    # Minimal valid PDF
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
196
%%EOF"""


@pytest.fixture
def sample_text_content():
    """Create sample text content for testing."""
    return b"This is a sample document for testing purposes."


@pytest.fixture
def sample_markdown_content():
    """Create sample markdown content for testing."""
    return b"""# Test Document

This is a test document.

## Section 1

Some content here.

## Section 2

More content here.
"""


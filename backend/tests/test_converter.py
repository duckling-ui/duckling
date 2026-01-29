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

"""Tests for the converter service."""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.converter import ConverterService, ConversionJob, ConversionStatus


class TestConversionJob:
    """Tests for ConversionJob class."""

    def test_job_creation(self):
        """Test creating a conversion job."""
        job = ConversionJob(
            job_id="test-123",
            input_path="/path/to/file.pdf",
            original_filename="document.pdf"
        )

        assert job.id == "test-123"
        assert job.input_path == "/path/to/file.pdf"
        assert job.original_filename == "document.pdf"
        assert job.status == ConversionStatus.PENDING
        assert job.progress == 0

    def test_job_with_settings(self):
        """Test creating a job with custom settings."""
        settings = {"ocr": {"enabled": True}}
        job = ConversionJob(
            job_id="test-456",
            input_path="/path/to/file.pdf",
            original_filename="doc.pdf",
            settings=settings
        )

        assert job.settings["ocr"]["enabled"] is True


class TestConverterService:
    """Tests for ConverterService class."""

    def test_service_initialization(self):
        """Test service initialization."""
        service = ConverterService()
        assert service._default_converter is None

    def test_create_job(self):
        """Test creating a job through the service."""
        service = ConverterService()
        job = service.create_job(
            input_path="/test/path.pdf",
            original_filename="test.pdf"
        )

        assert job.id is not None
        assert len(job.id) == 36  # UUID length
        assert job.input_path == "/test/path.pdf"

    def test_get_job(self):
        """Test retrieving a job."""
        service = ConverterService()
        created_job = service.create_job(
            input_path="/test/path.pdf",
            original_filename="test.pdf"
        )

        retrieved_job = service.get_job(created_job.id)
        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id

    def test_get_nonexistent_job(self):
        """Test retrieving a non-existent job."""
        service = ConverterService()
        job = service.get_job("nonexistent-id")
        assert job is None

    def test_detect_input_format_pdf(self):
        """Test format detection for PDF."""
        assert ConverterService.detect_input_format("document.pdf") == "pdf"
        assert ConverterService.detect_input_format("DOCUMENT.PDF") == "pdf"

    def test_detect_input_format_docx(self):
        """Test format detection for DOCX."""
        assert ConverterService.detect_input_format("document.docx") == "docx"

    def test_detect_input_format_image(self):
        """Test format detection for images."""
        assert ConverterService.detect_input_format("photo.png") == "image"
        assert ConverterService.detect_input_format("photo.jpg") == "image"
        assert ConverterService.detect_input_format("photo.jpeg") == "image"

    def test_detect_input_format_html(self):
        """Test format detection for HTML."""
        assert ConverterService.detect_input_format("page.html") == "html"
        assert ConverterService.detect_input_format("page.htm") == "html"

    def test_detect_input_format_unknown(self):
        """Test format detection for unknown extension."""
        assert ConverterService.detect_input_format("file.xyz") is None

    def test_cleanup_job(self):
        """Test job cleanup."""
        service = ConverterService()
        job = service.create_job(
            input_path="/test/path.pdf",
            original_filename="test.pdf"
        )
        job_id = job.id

        service.cleanup_job(job_id)

        assert service.get_job(job_id) is None


class TestConversionStatus:
    """Tests for ConversionStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert ConversionStatus.PENDING.value == "pending"
        assert ConversionStatus.PROCESSING.value == "processing"
        assert ConversionStatus.COMPLETED.value == "completed"
        assert ConversionStatus.FAILED.value == "failed"


# Integration tests (require docling to be installed)
class TestConverterIntegration:
    """Integration tests for converter service."""

    @pytest.mark.skip(reason="Requires docling installation and sample files")
    def test_full_conversion_flow(self, temp_upload_dir, sample_markdown_content):
        """Test full conversion flow with a real file."""
        # Create a test markdown file
        test_file = temp_upload_dir / "test.md"
        test_file.write_bytes(sample_markdown_content)

        service = ConverterService()
        job = service.create_job(
            input_path=str(test_file),
            original_filename="test.md"
        )

        # Run conversion synchronously for testing
        service._run_conversion(job)

        assert job.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED]


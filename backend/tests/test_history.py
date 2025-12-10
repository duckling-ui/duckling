"""Tests for the history service."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.history import HistoryService
from models.database import init_db, db, Conversion, Base, engine


@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database before each test."""
    Base.metadata.create_all(engine)
    yield
    # Clean up after test
    with db() as session:
        session.query(Conversion).delete()
        session.commit()


class TestHistoryService:
    """Tests for HistoryService class."""

    def test_create_entry(self):
        """Test creating a history entry."""
        service = HistoryService()
        entry = service.create_entry(
            job_id="test-123",
            filename="test_file.pdf",
            original_filename="Original Document.pdf",
            input_format="pdf",
            file_size=1024
        )

        assert entry["id"] == "test-123"
        assert entry["filename"] == "test_file.pdf"
        assert entry["original_filename"] == "Original Document.pdf"
        assert entry["status"] == "pending"

    def test_get_entry(self):
        """Test retrieving a history entry."""
        service = HistoryService()
        service.create_entry(
            job_id="test-456",
            filename="test.pdf",
            original_filename="test.pdf"
        )

        entry = service.get_entry("test-456")
        assert entry is not None
        assert entry["id"] == "test-456"

    def test_get_nonexistent_entry(self):
        """Test retrieving non-existent entry."""
        service = HistoryService()
        entry = service.get_entry("nonexistent")
        assert entry is None

    def test_update_status(self):
        """Test updating entry status."""
        service = HistoryService()
        service.create_entry(
            job_id="test-789",
            filename="test.pdf",
            original_filename="test.pdf"
        )

        updated = service.update_status(
            job_id="test-789",
            status="completed",
            confidence=0.95
        )

        assert updated["status"] == "completed"
        assert updated["confidence"] == 0.95
        assert updated["completed_at"] is not None

    def test_update_status_with_error(self):
        """Test updating entry status with error."""
        service = HistoryService()
        service.create_entry(
            job_id="test-error",
            filename="test.pdf",
            original_filename="test.pdf"
        )

        updated = service.update_status(
            job_id="test-error",
            status="failed",
            error_message="Conversion failed"
        )

        assert updated["status"] == "failed"
        assert updated["error_message"] == "Conversion failed"

    def test_get_all(self):
        """Test getting all entries."""
        service = HistoryService()

        # Create multiple entries
        for i in range(5):
            service.create_entry(
                job_id=f"test-all-{i}",
                filename=f"test{i}.pdf",
                original_filename=f"test{i}.pdf"
            )

        entries = service.get_all()
        assert len(entries) >= 5

    def test_get_all_with_limit(self):
        """Test getting entries with limit."""
        service = HistoryService()

        for i in range(10):
            service.create_entry(
                job_id=f"test-limit-{i}",
                filename=f"test{i}.pdf",
                original_filename=f"test{i}.pdf"
            )

        entries = service.get_all(limit=3)
        assert len(entries) == 3

    def test_get_all_with_status_filter(self):
        """Test filtering entries by status."""
        service = HistoryService()

        service.create_entry(
            job_id="test-filter-1",
            filename="test1.pdf",
            original_filename="test1.pdf"
        )
        service.update_status("test-filter-1", "completed")

        service.create_entry(
            job_id="test-filter-2",
            filename="test2.pdf",
            original_filename="test2.pdf"
        )
        service.update_status("test-filter-2", "failed")

        completed = service.get_all(status="completed")
        assert all(e["status"] == "completed" for e in completed)

    def test_get_recent(self):
        """Test getting recent entries."""
        service = HistoryService()

        for i in range(5):
            service.create_entry(
                job_id=f"test-recent-{i}",
                filename=f"test{i}.pdf",
                original_filename=f"test{i}.pdf"
            )

        recent = service.get_recent(limit=3)
        assert len(recent) == 3

    def test_delete_entry(self):
        """Test deleting an entry."""
        service = HistoryService()
        service.create_entry(
            job_id="test-delete",
            filename="test.pdf",
            original_filename="test.pdf"
        )

        result = service.delete_entry("test-delete")
        assert result is True

        entry = service.get_entry("test-delete")
        assert entry is None

    def test_delete_nonexistent_entry(self):
        """Test deleting non-existent entry."""
        service = HistoryService()
        result = service.delete_entry("nonexistent")
        assert result is False

    def test_delete_all(self):
        """Test deleting all entries."""
        service = HistoryService()

        for i in range(3):
            service.create_entry(
                job_id=f"test-delete-all-{i}",
                filename=f"test{i}.pdf",
                original_filename=f"test{i}.pdf"
            )

        count = service.delete_all()
        assert count >= 3

        entries = service.get_all()
        assert len(entries) == 0

    def test_get_stats(self):
        """Test getting statistics."""
        service = HistoryService()

        # Create entries with different statuses
        service.create_entry(
            job_id="test-stats-1",
            filename="test1.pdf",
            original_filename="test1.pdf",
            input_format="pdf"
        )
        service.update_status("test-stats-1", "completed")

        service.create_entry(
            job_id="test-stats-2",
            filename="test2.docx",
            original_filename="test2.docx",
            input_format="docx"
        )
        service.update_status("test-stats-2", "failed")

        stats = service.get_stats()

        assert "total" in stats
        assert "completed" in stats
        assert "failed" in stats
        assert "format_breakdown" in stats

    def test_search(self):
        """Test searching entries."""
        service = HistoryService()

        service.create_entry(
            job_id="test-search-1",
            filename="important_document.pdf",
            original_filename="Important Document.pdf"
        )
        service.create_entry(
            job_id="test-search-2",
            filename="other_file.pdf",
            original_filename="Other File.pdf"
        )

        results = service.search("important")
        assert len(results) >= 1
        assert any("important" in r["original_filename"].lower() for r in results)

    def test_search_no_results(self):
        """Test search with no results."""
        service = HistoryService()
        results = service.search("nonexistentquery12345")
        assert len(results) == 0


class TestConversionModel:
    """Tests for Conversion model."""

    def test_to_dict(self):
        """Test converting model to dictionary."""
        conversion = Conversion(
            id="test-dict",
            filename="test.pdf",
            original_filename="Test Document.pdf",
            input_format="pdf",
            status="pending"
        )

        d = conversion.to_dict()

        assert d["id"] == "test-dict"
        assert d["filename"] == "test.pdf"
        assert d["original_filename"] == "Test Document.pdf"
        assert d["input_format"] == "pdf"
        assert d["status"] == "pending"

    def test_set_and_get_settings(self):
        """Test setting and getting settings."""
        conversion = Conversion(
            id="test-settings",
            filename="test.pdf",
            original_filename="test.pdf"
        )

        settings = {"ocr": {"enabled": True}, "tables": {"enabled": False}}
        conversion.set_settings(settings)

        retrieved = conversion.get_settings()
        assert retrieved["ocr"]["enabled"] is True
        assert retrieved["tables"]["enabled"] is False

    def test_repr(self):
        """Test string representation."""
        conversion = Conversion(
            id="test-repr",
            filename="test.pdf",
            original_filename="test.pdf",
            status="completed"
        )

        repr_str = repr(conversion)
        assert "test-repr" in repr_str
        assert "test.pdf" in repr_str
        assert "completed" in repr_str


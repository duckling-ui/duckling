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

"""Tests for content-addressed storage utilities."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.content_store import (
    compute_file_hash,
    compute_settings_hash,
    compute_content_hash,
    get_content_store_path,
    content_store_exists,
    save_metadata,
    load_metadata,
    ensure_content_store_dir,
)


class TestComputeFileHash:
    """Tests for compute_file_hash."""

    def test_hash_bytes(self):
        """Hash of bytes is deterministic."""
        data = b"hello world"
        h1 = compute_file_hash(data)
        h2 = compute_file_hash(data)
        assert h1 == h2
        assert len(h1) == 64
        assert all(c in "0123456789abcdef" for c in h1)

    def test_hash_different_bytes_different_hash(self):
        """Different content yields different hash."""
        h1 = compute_file_hash(b"foo")
        h2 = compute_file_hash(b"bar")
        assert h1 != h2

    def test_hash_file(self):
        """Hash of file content."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test content")
            path = f.name
        try:
            h = compute_file_hash(path)
            assert len(h) == 64
            assert h == compute_file_hash(b"test content")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_hash_nonexistent_file_raises(self):
        """Hash of nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            compute_file_hash("/nonexistent/path/file.pdf")


class TestComputeSettingsHash:
    """Tests for compute_settings_hash."""

    def test_identical_settings_same_hash(self):
        """Same settings yield same hash."""
        s = {"ocr": {"enabled": True}, "tables": {}, "images": {}}
        assert compute_settings_hash(s) == compute_settings_hash(s)

    def test_different_settings_different_hash(self):
        """Different document-affecting settings yield different hash."""
        s1 = {"ocr": {"enabled": True}}
        s2 = {"ocr": {"enabled": False}}
        assert compute_settings_hash(s1) != compute_settings_hash(s2)

    def test_only_document_affecting_settings(self):
        """Performance/chunking settings are excluded."""
        s1 = {"ocr": {"enabled": True}, "performance": {"device": "cuda"}}
        s2 = {"ocr": {"enabled": True}, "performance": {"device": "cpu"}}
        assert compute_settings_hash(s1) == compute_settings_hash(s2)


class TestComputeContentHash:
    """Tests for compute_content_hash."""

    def test_content_hash_truncated(self):
        """Content hash is 32 chars."""
        h = compute_content_hash("a" * 64, "b" * 64)
        assert len(h) == 32

    def test_content_hash_deterministic(self):
        """Same inputs yield same content hash."""
        fh = "abc123"
        sh = "def456"
        assert compute_content_hash(fh, sh) == compute_content_hash(fh, sh)


class TestContentStorePaths:
    """Tests for content store path helpers."""

    def test_get_content_store_path(self):
        """Content store path is correct."""
        with patch("utils.content_store.OUTPUT_FOLDER", Path("/tmp/outputs")):
            p = get_content_store_path("abc123")
            assert p == Path("/tmp/outputs/_content/abc123")

    def test_content_store_exists_returns_false_when_empty(self):
        """Empty dir does not count as existing."""
        with tempfile.TemporaryDirectory() as tmp:
            store_dir = Path(tmp) / "content"
            store_dir.mkdir()
            with patch("utils.content_store.OUTPUT_FOLDER", Path(tmp)):
                with patch("utils.content_store.get_content_store_path", return_value=store_dir):
                    assert content_store_exists("any") is False

    def test_content_store_exists_returns_true_with_metadata(self):
        """Dir with metadata.json exists."""
        with tempfile.TemporaryDirectory() as tmp:
            store_dir = Path(tmp) / "content"
            store_dir.mkdir()
            (store_dir / "metadata.json").write_text("{}")
            with patch("utils.content_store.OUTPUT_FOLDER", Path(tmp)):
                with patch("utils.content_store.get_content_store_path", return_value=store_dir):
                    assert content_store_exists("any") is True

    def test_content_store_exists_returns_true_with_document_json(self):
        """Dir with *.document.json exists."""
        with tempfile.TemporaryDirectory() as tmp:
            store_dir = Path(tmp) / "content"
            store_dir.mkdir()
            (store_dir / "doc.document.json").write_text("{}")
            with patch("utils.content_store.OUTPUT_FOLDER", Path(tmp)):
                with patch("utils.content_store.get_content_store_path", return_value=store_dir):
                    assert content_store_exists("any") is True


class TestMetadata:
    """Tests for save_metadata and load_metadata."""

    def test_save_and_load_metadata(self):
        """Save and load metadata round-trip."""
        with tempfile.TemporaryDirectory() as tmp:
            store_dir = Path(tmp) / "hash123"
            store_dir.mkdir()
            with patch("utils.content_store.get_content_store_path", return_value=store_dir):
                meta = {"output_paths": {"markdown": "doc.md"}, "page_count": 5}
                save_metadata("hash123", meta)
                loaded = load_metadata("hash123")
                assert loaded == meta

    def test_load_metadata_nonexistent_returns_none(self):
        """Load from nonexistent store returns None."""
        with tempfile.TemporaryDirectory() as tmp:
            store_dir = Path(tmp) / "nonexistent"
            with patch("utils.content_store.get_content_store_path", return_value=store_dir):
                assert load_metadata("nonexistent") is None

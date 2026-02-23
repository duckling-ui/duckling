"""
Content-addressed storage utilities for conversion output deduplication.

Same file + same document-affecting settings yields identical DoclingDocument.
Store once in content store, symlink from job output dir.
"""

import hashlib
import json
from pathlib import Path
from typing import Union, Dict, Any, Optional

from config import OUTPUT_FOLDER


def _document_affecting_settings(settings: dict) -> dict:
    """Extract only settings that affect the Docling document output."""
    return {
        "ocr": settings.get("ocr") or {},
        "tables": settings.get("tables") or {},
        "images": settings.get("images") or {},
    }


def compute_file_hash(path_or_bytes: Union[str, Path, bytes]) -> str:
    """
    Compute SHA-256 hash of file content.

    Args:
        path_or_bytes: File path or raw bytes

    Returns:
        64-char hex digest
    """
    h = hashlib.sha256()
    if isinstance(path_or_bytes, bytes):
        h.update(path_or_bytes)
    else:
        path = Path(path_or_bytes)
        if not path.exists():
            raise FileNotFoundError(f"Cannot hash: {path} does not exist")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    return h.hexdigest()


def compute_settings_hash(settings: dict) -> str:
    """
    Compute hash of document-affecting settings only.

    Excludes: performance, chunking, output format.
    """
    doc_settings = _document_affecting_settings(settings)
    canonical = json.dumps(doc_settings, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def compute_content_hash(file_hash: str, settings_hash: str) -> str:
    """Compute content hash from file and settings hashes."""
    combined = f"{file_hash}{settings_hash}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def get_content_store_path(content_hash: str) -> Path:
    """Return path to content store directory for this hash."""
    content_store = OUTPUT_FOLDER / "_content"
    return content_store / content_hash


def content_store_exists(content_hash: str) -> bool:
    """Check if content store has this hash (has document.json or metadata.json)."""
    store_path = get_content_store_path(content_hash)
    if not store_path.exists() or not store_path.is_dir():
        return False
    # Must have document or metadata
    doc_files = list(store_path.glob("*.document.json"))
    meta_path = store_path / "metadata.json"
    return bool(doc_files) or meta_path.exists()


def save_metadata(content_hash: str, metadata: dict) -> None:
    """
    Save metadata.json in content store.

    Paths in output_paths should be relative to content store root (filename only).
    """
    store_path = get_content_store_path(content_hash)
    store_path.mkdir(parents=True, exist_ok=True)
    meta_path = store_path / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)


def load_metadata(content_hash: str) -> Optional[Dict[str, Any]]:
    """Load metadata.json from content store."""
    meta_path = get_content_store_path(content_hash) / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def ensure_content_store_dir() -> Path:
    """Ensure _content directory exists. Returns path."""
    content_store = OUTPUT_FOLDER / "_content"
    content_store.mkdir(parents=True, exist_ok=True)
    return content_store

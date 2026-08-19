"""Chunker factory for hybrid/hierarchical options."""

from __future__ import annotations

from typing import Any, Dict


try:
    from docling.chunking import HybridChunker, HierarchicalChunker
except Exception:  # pragma: no cover
    HybridChunker = None
    HierarchicalChunker = None


def build_chunker(chunking_settings: Dict[str, Any]):
    chunker_kind = chunking_settings.get("chunker", "hybrid")
    kwargs = {
        "merge_peers": chunking_settings.get("merge_peers", True),
        "max_tokens": chunking_settings.get("max_tokens", 512),
        "tokenizer": chunking_settings.get("tokenizer", "sentence-transformers/all-MiniLM-L6-v2"),
        "use_markdown_tables": chunking_settings.get("use_markdown_tables", False),
        "use_markdown_images": chunking_settings.get("use_markdown_images", False),
        "image_placeholder": chunking_settings.get("image_placeholder", "[image]"),
        "include_raw_text": chunking_settings.get("include_raw_text", False),
    }
    if chunker_kind == "hierarchical" and HierarchicalChunker is not None:
        return HierarchicalChunker(**kwargs)
    if HybridChunker is None:
        raise RuntimeError("Docling chunkers not available")
    return HybridChunker(**kwargs)


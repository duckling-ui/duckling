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

"""History API endpoints."""

import json
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound

from services.history import history_service
from services.file_manager import file_manager
from services.converter import converter_service

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
def get_history():
    """
    Get conversion history.

    Query parameters:
    - limit: Maximum entries to return (default 50)
    - offset: Number of entries to skip (default 0)
    - status: Filter by status (optional)

    Returns:
        JSON with history entries
    """
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    status = request.args.get("status", None)

    # Clamp limit to reasonable range
    limit = max(1, min(limit, 100))

    entries = history_service.get_all(limit=limit, offset=offset, status=status)

    return jsonify({
        "entries": entries,
        "count": len(entries),
        "limit": limit,
        "offset": offset
    })


@history_bp.route("/history/recent", methods=["GET"])
def get_recent_history():
    """
    Get recent conversion history.

    Query parameters:
    - limit: Maximum entries to return (default 10)

    Returns:
        JSON with recent history entries
    """
    limit = request.args.get("limit", 10, type=int)
    limit = max(1, min(limit, 50))

    entries = history_service.get_recent(limit=limit)

    return jsonify({
        "entries": entries,
        "count": len(entries)
    })


@history_bp.route("/history/<job_id>", methods=["GET"])
def get_history_entry(job_id: str):
    """
    Get a specific history entry.

    Args:
        job_id: The job identifier

    Returns:
        JSON with history entry details
    """
    entry = history_service.get_entry(job_id)

    if not entry:
        raise NotFound(f"History entry {job_id} not found")

    return jsonify(entry)


@history_bp.route("/history/<job_id>", methods=["DELETE"])
def delete_history_entry(job_id: str):
    """
    Delete a history entry and its associated files.

    Args:
        job_id: The job identifier

    Returns:
        JSON confirmation
    """
    # Security: Validate job_id doesn't contain path traversal characters
    if ".." in job_id or "/" in job_id or "\\" in job_id:
        raise NotFound(f"History entry {job_id} not found")

    entry = history_service.get_entry(job_id)

    if not entry:
        raise NotFound(f"History entry {job_id} not found")

    # Delete associated output files (file_manager.delete_output_folder validates internally)
    file_manager.delete_output_folder(job_id)
    file_manager.cleanup_orphaned_content()

    # Delete history entry
    history_service.delete_entry(job_id)

    return jsonify({
        "message": f"History entry {job_id} deleted",
        "job_id": job_id
    })


@history_bp.route("/history", methods=["DELETE"])
def clear_history():
    """
    Clear all history entries.

    Returns:
        JSON with count of deleted entries
    """
    # Get all entries first to clean up files
    entries = history_service.get_all(limit=1000)

    # Delete all output folders
    # Security: entry["id"] comes from database (UUID), safe to use
    # file_manager.delete_output_folder validates internally
    for entry in entries:
        file_manager.delete_output_folder(entry["id"])
    file_manager.cleanup_orphaned_content()

    # Delete all history entries
    count = history_service.delete_all()

    return jsonify({
        "message": f"Cleared {count} history entries",
        "deleted_count": count
    })


@history_bp.route("/history/stats", methods=["GET"])
def get_history_stats():
    """
    Get statistics about conversion history.

    Returns:
        JSON with statistics
    """
    stats = history_service.get_stats()
    storage_stats = file_manager.get_storage_stats()

    return jsonify({
        "conversions": stats,
        "storage": storage_stats,
        "queue_depth": converter_service.get_queue_depth(),
    })


@history_bp.route("/history/search", methods=["GET"])
def search_history():
    """
    Search history by filename.

    Query parameters:
    - q: Search query
    - limit: Maximum results (default 20)

    Returns:
        JSON with matching entries
    """
    query = request.args.get("q", "")
    limit = request.args.get("limit", 20, type=int)

    if not query:
        return jsonify({
            "entries": [],
            "count": 0,
            "query": ""
        })

    limit = max(1, min(limit, 50))
    entries = history_service.search(query, limit=limit)

    return jsonify({
        "entries": entries,
        "count": len(entries),
        "query": query
    })


@history_bp.route("/history/cleanup", methods=["POST"])
def cleanup_old_history():
    """
    Clean up old history entries and files.

    Request body (optional):
    - days: Age threshold in days (default 30)
    - max_age_hours: Age threshold for files in hours (default 24)

    Returns:
        JSON with cleanup results
    """
    data = request.get_json() or {}
    days = data.get("days", 30)
    max_age_hours = data.get("max_age_hours", 24)

    # Clean up old files
    uploads_deleted, outputs_deleted = file_manager.cleanup_old_files(max_age_hours)

    # Clean up old history entries
    entries_deleted = history_service.cleanup_old_entries(days)

    return jsonify({
        "message": "Cleanup completed",
        "results": {
            "history_entries_deleted": entries_deleted,
            "upload_files_deleted": uploads_deleted,
            "output_folders_deleted": outputs_deleted
        }
    })


@history_bp.route("/history/reconcile", methods=["POST"])
def reconcile_history():
    """
    Reconcile history database with on-disk output files.

    Scans the output directory for conversion outputs that exist on disk
    but have no database entry (e.g. after DB loss or restart). Creates
    missing entries so they appear in history.

    Returns:
        JSON with count of entries added and list of job_ids
    """
    added_count, added_ids = history_service.reconcile_from_disk()
    return jsonify({
        "message": f"Reconciled {added_count} entries from disk",
        "added_count": added_count,
        "added_ids": added_ids,
    })


@history_bp.route("/history/export", methods=["GET"])
def export_history():
    """
    Export history as JSON.

    Returns:
        JSON with all history entries
    """
    entries = history_service.get_all(limit=10000)
    stats = history_service.get_stats()

    return jsonify({
        "exported_at": __import__("datetime").datetime.utcnow().isoformat(),
        "total_entries": len(entries),
        "statistics": stats,
        "entries": entries
    })


@history_bp.route("/history/<job_id>/load", methods=["GET"])
def load_history_document(job_id: str):
    """
    Load a converted document from history and return it as a ConversionResult.

    This endpoint loads the DoclingDocument from the stored JSON file and
    returns it in the same format as a fresh conversion result.

    Args:
        job_id: The job identifier

    Returns:
        JSON with conversion result matching ConversionResult format
    """
    from pathlib import Path
    from config import OUTPUT_FOLDER
    from services.converter import converter_service
    from utils.security import validate_job_id, get_validated_output_dir

    # Security: Validate job_id first before any path operations
    job_id = validate_job_id(job_id)

    # Now that job_id is validated, construct and validate the output directory
    output_dir = get_validated_output_dir(job_id, Path(OUTPUT_FOLDER))

    # Get history entry
    entry = history_service.get_entry(job_id)
    if not entry:
        raise NotFound(f"History entry {job_id} not found")

    if entry.get("status") != "completed":
        return jsonify({
            "job_id": job_id,
            "status": entry.get("status"),
            "message": "Conversion not completed"
        }), 400

    # Load the document from stored JSON
    doc = history_service.load_document(job_id)
    if not doc:
        # Fallback: try to reconstruct from output files
        # output_dir is already validated and normalized above
        if not output_dir.exists():
            raise NotFound(f"Document files for {job_id} not found")

        # Determine available formats from files on disk
        formats_available = []
        format_extensions = {
            "markdown": ".md",
            "html": ".html",
            "json": ".json",
            "text": ".txt",
            "doctags": ".doctags",
            "document_tokens": ".tokens.json",
            "chunks": ".chunks.json"
        }
        for fmt, ext in format_extensions.items():
            # $path-traversal-safe: output_dir validated above, ext is from static dict
            if list(output_dir.glob(f"*{ext}")):
                formats_available.append(fmt)

        # Count images and tables
        # Security: output_dir is already validated above
        # Subdirectories use static strings "images" and "tables", safe from path traversal
        images_dir = output_dir / "images"  # $path-traversal-safe: static string
        tables_dir = output_dir / "tables"  # $path-traversal-safe: static string
        # Additional validation: ensure subdirectories stay within output_dir
        try:
            images_dir_resolved = images_dir.resolve()
            tables_dir_resolved = tables_dir.resolve()
            images_dir_resolved.relative_to(output_dir)
            tables_dir_resolved.relative_to(output_dir)
        except ValueError:
            # Should not happen with static strings, but be safe
            images_dir_resolved = None
            tables_dir_resolved = None

        images_count = 0
        if images_dir_resolved and images_dir_resolved.exists():
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg', '*.bmp']
            for ext in image_extensions:
                # $path-traversal-safe: images_dir_resolved validated above
                images_count += len(list(images_dir_resolved.glob(ext)))

        # $path-traversal-safe: tables_dir_resolved validated above
        tables_count = len(list(tables_dir_resolved.glob("*.csv"))) if (tables_dir_resolved and tables_dir_resolved.exists()) else 0

        # Try to read markdown preview
        md_preview = ""
        # Count chunks if available
        # $path-traversal-safe: output_dir validated above
        md_files = list(output_dir.glob("*.md"))
        if md_files:
            try:
                # $path-traversal-safe: md_files[0] is from validated output_dir
                with open(md_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    md_preview = content[:5000] if len(content) > 5000 else content
            except Exception:
                pass

        # Count chunks if available
        chunks_count = 0
        # $path-traversal-safe: output_dir validated above
        chunks_files = list(output_dir.glob("*.chunks.json"))
        if chunks_files:
            try:
                # $path-traversal-safe: chunks_files[0] is from validated_output_dir
                with open(chunks_files[0], 'r', encoding='utf-8') as f:
                    chunks_data = json.load(f)
                    chunks_count = len(chunks_data) if isinstance(chunks_data, list) else 0
            except Exception:
                pass

        return jsonify({
            "job_id": job_id,
            "status": "completed",
            "confidence": entry.get("confidence"),
            "formats_available": formats_available,
            "result": {
                "markdown_preview": md_preview,
                "formats_available": formats_available,
                "page_count": 0,  # Not available without document
                "images_count": images_count,
                "tables_count": tables_count,
                "chunks_count": chunks_count,
                "warnings": []
            },
            "images_count": images_count,
            "tables_count": tables_count,
            "chunks_count": chunks_count,
            "completed_at": entry.get("completed_at")
        })

    # Document loaded successfully - extract information from it
    # output_dir is already validated above

    # Export to markdown for preview
    try:
        md_content = doc.export_to_markdown()
        md_preview = md_content[:5000] if len(md_content) > 5000 else md_content
    except Exception as e:
        print(f"[load_document] Failed to export markdown: {e}")
        md_preview = ""

    # Determine available formats from files on disk
    formats_available = []
    format_extensions = {
        "markdown": ".md",
        "html": ".html",
        "json": ".json",
        "text": ".txt",
        "doctags": ".doctags",
        "document_tokens": ".tokens.json",
        "chunks": ".chunks.json"
    }
    for fmt, ext in format_extensions.items():
        # $path-traversal-safe: output_dir (validated_output_dir) validated above, ext is from static dict
        if list(output_dir.glob(f"*{ext}")):
            formats_available.append(fmt)

    # Count images and tables
    # Security: output_dir (validated_output_dir) is already validated above
    # Subdirectories use static strings "images" and "tables", safe from path traversal
    images_dir = output_dir / "images"  # $path-traversal-safe: static string
    tables_dir = output_dir / "tables"  # $path-traversal-safe: static string
    # Additional validation: ensure subdirectories stay within output_dir
    try:
        images_dir_resolved = images_dir.resolve()
        tables_dir_resolved = tables_dir.resolve()
        images_dir_resolved.relative_to(output_dir)
        tables_dir_resolved.relative_to(output_dir)
    except ValueError:
        # Should not happen with static strings, but be safe
        images_dir_resolved = None
        tables_dir_resolved = None

    images_count = 0
    if images_dir_resolved and images_dir_resolved.exists():
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg', '*.bmp']
        for ext in image_extensions:
            # $path-traversal-safe: images_dir_resolved validated above
            images_count += len(list(images_dir_resolved.glob(ext)))

    # $path-traversal-safe: tables_dir_resolved validated above
    tables_count = len(list(tables_dir_resolved.glob("*.csv"))) if (tables_dir_resolved and tables_dir_resolved.exists()) else 0

    # Count chunks if available
    chunks_count = 0
    # $path-traversal-safe: output_dir (validated_output_dir) validated above
    chunks_files = list(output_dir.glob("*.chunks.json"))
    if chunks_files:
        try:
            # $path-traversal-safe: chunks_files[0] is from validated output_dir
            with open(chunks_files[0], 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
                chunks_count = len(chunks_data) if isinstance(chunks_data, list) else 0
        except Exception:
            pass

    # Get page count from document if available
    page_count = 0
    if hasattr(doc, 'pages') and doc.pages:
        page_count = len(doc.pages)
    elif hasattr(doc, 'metadata') and doc.metadata:
        if hasattr(doc.metadata, 'page_count'):
            page_count = doc.metadata.page_count

    return jsonify({
        "job_id": job_id,
        "status": "completed",
        "confidence": entry.get("confidence"),
        "formats_available": formats_available,
        "result": {
            "markdown_preview": md_preview,
            "formats_available": formats_available,
            "page_count": page_count,
            "images_count": images_count,
            "tables_count": tables_count,
            "chunks_count": chunks_count,
            "warnings": []
        },
        "images_count": images_count,
        "tables_count": tables_count,
        "chunks_count": chunks_count,
        "completed_at": entry.get("completed_at")
    })


@history_bp.route("/history/<job_id>/generate-chunks", methods=["POST"])
def generate_chunks(job_id: str):
    """
    Generate RAG chunks for a completed document on demand.

    Loads the DoclingDocument from disk, applies current chunking settings,
    and returns the generated chunks. Optionally saves to disk.
    """
    from pathlib import Path
    from config import OUTPUT_FOLDER
    from routes.settings import load_settings
    from utils.security import validate_job_id, get_validated_output_dir

    job_id = validate_job_id(job_id)
    output_dir = get_validated_output_dir(job_id, Path(OUTPUT_FOLDER))

    entry = history_service.get_entry(job_id)
    if not entry:
        raise NotFound(f"History entry {job_id} not found")

    if entry.get("status") != "completed":
        return jsonify({
            "job_id": job_id,
            "status": entry.get("status"),
            "message": "Conversion not completed"
        }), 400

    doc = history_service.load_document(job_id)
    if not doc:
        return jsonify({
            "job_id": job_id,
            "error": "Document not found or could not be loaded"
        }), 404

    settings = load_settings()
    chunks = converter_service.generate_chunks_for_document(doc, settings)

    # Save chunks to disk if we have a valid output dir
    if output_dir.exists() and chunks:
        try:
            stem = Path(entry.get("original_filename", "document")).stem
            chunks_path = output_dir / f"{stem}.chunks.json"
            with open(chunks_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2, default=str)
        except Exception as e:
            print(f"[generate-chunks] Failed to save: {e}")

    return jsonify({
        "job_id": job_id,
        "chunks": chunks,
        "count": len(chunks)
    })


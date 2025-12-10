"""History API endpoints."""

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound

from services.history import history_service
from services.file_manager import file_manager

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
    entry = history_service.get_entry(job_id)

    if not entry:
        raise NotFound(f"History entry {job_id} not found")

    # Delete associated output files
    file_manager.delete_output_folder(job_id)

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
    for entry in entries:
        file_manager.delete_output_folder(entry["id"])

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
        "storage": storage_stats
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


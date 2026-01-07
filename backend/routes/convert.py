"""Conversion API endpoints."""

import os
import json
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound

from services.converter import converter_service, ConversionStatus
from services.file_manager import file_manager
from services.history import history_service
from config import DEFAULT_CONVERSION_SETTINGS, OUTPUT_FOLDER, BACKEND_DIR

convert_bp = Blueprint("convert", __name__)

# Settings file path (same as in settings.py)
SETTINGS_FILE = BACKEND_DIR / "user_settings.json"


def load_user_settings() -> dict:
    """Load user settings from file or return defaults."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
                # Deep merge with defaults to ensure all keys exist
                settings = DEFAULT_CONVERSION_SETTINGS.copy()
                def deep_merge(base, updates):
                    for key, value in updates.items():
                        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                            deep_merge(base[key], value)
                        else:
                            base[key] = value
                deep_merge(settings, saved)
                return settings
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONVERSION_SETTINGS.copy()


@convert_bp.route("/convert", methods=["POST"])
def upload_and_convert():
    """
    Upload a document and start conversion.

    Expects multipart/form-data with:
    - file: The document file
    - settings (optional): JSON string of conversion settings

    Returns:
        JSON with job_id and initial status
    """
    # Check if file is present
    if "file" not in request.files:
        raise BadRequest("No file provided")

    file = request.files["file"]
    if file.filename == "":
        raise BadRequest("No file selected")

    # Validate file type
    if not file_manager.allowed_file(file.filename):
        raise BadRequest(f"File type not allowed. Allowed types: {', '.join(file_manager.upload_folder.parent.name)}")

    # Load saved user settings as the base (not defaults)
    settings = load_user_settings()

    # Override with any settings provided in the request
    if "settings" in request.form:
        try:
            request_settings = json.loads(request.form["settings"])
            # Deep merge request settings on top of user settings
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
            deep_merge(settings, request_settings)
        except json.JSONDecodeError:
            pass

    print(f"[convert] Using OCR backend: {settings.get('ocr', {}).get('backend', 'unknown')}")

    # Save the uploaded file
    saved_path, safe_filename, file_size = file_manager.save_upload(file)

    # Detect input format
    input_format = converter_service.detect_input_format(file.filename)

    # Create conversion job
    job = converter_service.create_job(saved_path, file.filename, settings)

    # Create history entry
    history_service.create_entry(
        job_id=job.id,
        filename=safe_filename,
        original_filename=file.filename,
        input_format=input_format,
        settings=settings,
        file_size=file_size
    )

    # Define callback to update history when conversion completes
    def on_complete(completed_job):
        status = "completed" if completed_job.status == ConversionStatus.COMPLETED else "failed"
        history_service.update_status(
            job_id=completed_job.id,
            status=status,
            confidence=completed_job.confidence,
            error_message=completed_job.error,
            output_path=str(completed_job.output_paths.get("markdown", ""))
        )

    # Start async conversion
    converter_service.start_conversion(job, on_complete=on_complete)

    return jsonify({
        "job_id": job.id,
        "filename": file.filename,
        "input_format": input_format,
        "status": "processing",
        "message": "Conversion started"
    }), 202


@convert_bp.route("/convert/batch", methods=["POST"])
def upload_and_convert_batch():
    """
    Upload multiple documents and start batch conversion.

    Expects multipart/form-data with:
    - files: Multiple document files
    - settings (optional): JSON string of conversion settings

    Returns:
        JSON with list of job_ids and statuses
    """
    # Check if files are present
    if "files" not in request.files:
        raise BadRequest("No files provided")

    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        raise BadRequest("No files selected")

    # Load saved user settings as the base (not defaults)
    settings = load_user_settings()

    # Override with any settings provided in the request
    if "settings" in request.form:
        try:
            request_settings = json.loads(request.form["settings"])
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
            deep_merge(settings, request_settings)
        except json.JSONDecodeError:
            pass

    print(f"[convert/batch] Using OCR backend: {settings.get('ocr', {}).get('backend', 'unknown')}")

    jobs = []
    for file in files:
        if file.filename == "":
            continue

        # Validate file type
        if not file_manager.allowed_file(file.filename):
            jobs.append({
                "filename": file.filename,
                "status": "rejected",
                "error": "File type not allowed"
            })
            continue

        # Save the uploaded file
        saved_path, safe_filename, file_size = file_manager.save_upload(file)

        # Detect input format
        input_format = converter_service.detect_input_format(file.filename)

        # Create conversion job
        job = converter_service.create_job(saved_path, file.filename, settings)

        # Create history entry
        history_service.create_entry(
            job_id=job.id,
            filename=safe_filename,
            original_filename=file.filename,
            input_format=input_format,
            settings=settings,
            file_size=file_size
        )

        # Define callback to update history when conversion completes
        def on_complete(completed_job):
            status = "completed" if completed_job.status == ConversionStatus.COMPLETED else "failed"
            history_service.update_status(
                job_id=completed_job.id,
                status=status,
                confidence=completed_job.confidence,
                error_message=completed_job.error,
                output_path=str(completed_job.output_paths.get("markdown", ""))
            )

        # Start async conversion
        converter_service.start_conversion(job, on_complete=on_complete)

        jobs.append({
            "job_id": job.id,
            "filename": file.filename,
            "input_format": input_format,
            "status": "processing"
        })

    return jsonify({
        "jobs": jobs,
        "total": len(jobs),
        "message": f"Started {len([j for j in jobs if j.get('status') == 'processing'])} conversions"
    }), 202


@convert_bp.route("/convert/<job_id>/status", methods=["GET"])
def get_conversion_status(job_id: str):
    """
    Get the status of a conversion job.

    Args:
        job_id: The job identifier

    Returns:
        JSON with current status and progress
    """
    job = converter_service.get_job(job_id)

    if not job:
        # Check history for completed jobs
        history_entry = history_service.get_entry(job_id)
        if history_entry:
            return jsonify({
                "job_id": job_id,
                "status": history_entry["status"],
                "progress": 100 if history_entry["status"] == "completed" else 0,
                "message": "Conversion completed" if history_entry["status"] == "completed" else "Conversion failed",
                "confidence": history_entry.get("confidence"),
                "error": history_entry.get("error_message")
            })
        raise NotFound(f"Job {job_id} not found")

    response = {
        "job_id": job.id,
        "status": job.status.value,
        "progress": job.progress,
        "message": job.message
    }

    if job.status == ConversionStatus.COMPLETED:
        response["confidence"] = job.confidence
        response["formats_available"] = list(job.output_paths.keys())
        response["images_count"] = len(job.extracted_images)
        response["tables_count"] = len(job.extracted_tables)
        response["chunks_count"] = len(job.chunks)
        if job.result:
            response["preview"] = job.result.get("markdown_preview", "")[:1000]
            response["page_count"] = job.result.get("page_count")

    if job.status == ConversionStatus.FAILED:
        response["error"] = job.error

    return jsonify(response)


@convert_bp.route("/convert/<job_id>/result", methods=["GET"])
def get_conversion_result(job_id: str):
    """
    Get the full result of a completed conversion.

    Args:
        job_id: The job identifier

    Returns:
        JSON with conversion result and preview
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({
            "job_id": job_id,
            "status": job.status.value,
            "message": "Conversion not yet completed"
        }), 202

    return jsonify({
        "job_id": job.id,
        "status": "completed",
        "confidence": job.confidence,
        "formats_available": list(job.output_paths.keys()),
        "result": job.result,
        "images_count": len(job.extracted_images),
        "tables_count": len(job.extracted_tables),
        "chunks_count": len(job.chunks),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    })


@convert_bp.route("/convert/<job_id>/images", methods=["GET"])
def get_extracted_images(job_id: str):
    """
    Get list of extracted images from a conversion.

    Args:
        job_id: The job identifier

    Returns:
        JSON with list of extracted images
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({
            "job_id": job_id,
            "status": job.status.value,
            "message": "Conversion not yet completed"
        }), 202

    return jsonify({
        "job_id": job_id,
        "images": job.extracted_images,
        "count": len(job.extracted_images)
    })


@convert_bp.route("/convert/<job_id>/images/<int:image_id>", methods=["GET"])
def download_extracted_image(job_id: str, image_id: int):
    """
    Download a specific extracted image.

    Args:
        job_id: The job identifier
        image_id: The image identifier (1-based)

    Returns:
        Image file
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({"error": "Conversion not completed"}), 400

    # Find the image
    image = next((img for img in job.extracted_images if img["id"] == image_id), None)
    if not image:
        raise NotFound(f"Image {image_id} not found")

    image_path = image.get("path")
    if not image_path or not os.path.exists(image_path):
        raise NotFound("Image file not found")

    return send_file(
        image_path,
        mimetype="image/png",
        as_attachment=True,
        download_name=image.get("filename", f"image_{image_id}.png")
    )


@convert_bp.route("/convert/<job_id>/tables", methods=["GET"])
def get_extracted_tables(job_id: str):
    """
    Get list of extracted tables from a conversion.

    Args:
        job_id: The job identifier

    Returns:
        JSON with list of extracted tables
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({
            "job_id": job_id,
            "status": job.status.value,
            "message": "Conversion not yet completed"
        }), 202

    return jsonify({
        "job_id": job_id,
        "tables": job.extracted_tables,
        "count": len(job.extracted_tables)
    })


@convert_bp.route("/convert/<job_id>/tables/<int:table_id>/csv", methods=["GET"])
def download_table_csv(job_id: str, table_id: int):
    """
    Download a specific table as CSV.

    Args:
        job_id: The job identifier
        table_id: The table identifier (1-based)

    Returns:
        CSV file
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({"error": "Conversion not completed"}), 400

    # Find the table
    table = next((t for t in job.extracted_tables if t["id"] == table_id), None)
    if not table:
        raise NotFound(f"Table {table_id} not found")

    csv_path = table.get("csv_path")
    if not csv_path or not os.path.exists(csv_path):
        raise NotFound("CSV file not found")

    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"table_{table_id}.csv"
    )


@convert_bp.route("/convert/<job_id>/tables/<int:table_id>/image", methods=["GET"])
def download_table_image(job_id: str, table_id: int):
    """
    Download a specific table as image.

    Args:
        job_id: The job identifier
        table_id: The table identifier (1-based)

    Returns:
        Image file
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({"error": "Conversion not completed"}), 400

    # Find the table
    table = next((t for t in job.extracted_tables if t["id"] == table_id), None)
    if not table:
        raise NotFound(f"Table {table_id} not found")

    image_path = table.get("image_path")
    if not image_path or not os.path.exists(image_path):
        raise NotFound("Table image not found")

    return send_file(
        image_path,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"table_{table_id}.png"
    )


@convert_bp.route("/convert/<job_id>/chunks", methods=["GET"])
def get_document_chunks(job_id: str):
    """
    Get document chunks for RAG applications.

    Args:
        job_id: The job identifier

    Returns:
        JSON with list of document chunks
    """
    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({
            "job_id": job_id,
            "status": job.status.value,
            "message": "Conversion not yet completed"
        }), 202

    return jsonify({
        "job_id": job_id,
        "chunks": job.chunks,
        "count": len(job.chunks)
    })


@convert_bp.route("/export/<job_id>/<format_type>", methods=["GET"])
def export_document(job_id: str, format_type: str):
    """
    Download the converted document in a specific format.

    Args:
        job_id: The job identifier
        format_type: Output format (markdown, html, json, doctags, text, document_tokens, chunks)

    Returns:
        File download
    """
    valid_formats = ["markdown", "html", "json", "doctags", "text", "document_tokens", "chunks"]
    if format_type not in valid_formats:
        raise BadRequest(f"Invalid format. Valid formats: {', '.join(valid_formats)}")

    job = converter_service.get_job(job_id)

    if not job:
        raise NotFound(f"Job {job_id} not found")

    if job.status != ConversionStatus.COMPLETED:
        return jsonify({
            "error": "Conversion not completed",
            "status": job.status.value
        }), 400

    output_path = converter_service.get_output_path(job_id, format_type)

    if not output_path:
        raise NotFound(f"Output format '{format_type}' not available for this job")

    # Determine MIME type
    mime_types = {
        "markdown": "text/markdown",
        "html": "text/html",
        "json": "application/json",
        "doctags": "text/plain",
        "text": "text/plain",
        "document_tokens": "application/json",
        "chunks": "application/json"
    }

    return send_file(
        output_path,
        mimetype=mime_types.get(format_type, "text/plain"),
        as_attachment=True,
        download_name=output_path.name
    )


@convert_bp.route("/export/<job_id>/<format_type>/content", methods=["GET"])
def get_export_content(job_id: str, format_type: str):
    """
    Get the converted content as JSON (for preview).

    Args:
        job_id: The job identifier
        format_type: Output format

    Returns:
        JSON with content
    """
    valid_formats = ["markdown", "html", "json", "doctags", "text", "document_tokens", "chunks"]
    if format_type not in valid_formats:
        raise BadRequest(f"Invalid format. Valid formats: {', '.join(valid_formats)}")

    content = converter_service.get_output_content(job_id, format_type)

    if content is None:
        raise NotFound(f"Content not available")

    return jsonify({
        "job_id": job_id,
        "format": format_type,
        "content": content
    })


@convert_bp.route("/convert/<job_id>", methods=["DELETE"])
def cancel_or_delete_job(job_id: str):
    """
    Cancel a running job or delete a completed job.

    Args:
        job_id: The job identifier

    Returns:
        JSON confirmation
    """
    job = converter_service.get_job(job_id)

    if job:
        converter_service.cleanup_job(job_id)

    # Also delete from history
    history_service.delete_entry(job_id)

    return jsonify({
        "message": f"Job {job_id} deleted",
        "job_id": job_id
    })


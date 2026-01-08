"""Conversion API endpoints."""

import os
import json
import tempfile
import requests
import re
import uuid
import base64
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
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


# Allowed extensions for URL downloads (same as file uploads)
ALLOWED_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', '.html', '.htm',
    '.md', '.markdown', '.csv', '.png', '.jpg', '.jpeg',
    '.tiff', '.tif', '.gif', '.webp', '.bmp', '.wav', '.mp3',
    '.vtt', '.xml', '.asciidoc', '.adoc', '.txt'
}

# Maximum URL download size (100MB)
MAX_URL_DOWNLOAD_SIZE = 100 * 1024 * 1024


def download_from_url(url: str) -> tuple[str, str, int]:
    """
    Download a document from a URL.

    Args:
        url: The URL to download from

    Returns:
        Tuple of (saved_path, filename, file_size)

    Raises:
        BadRequest: If the URL is invalid or the file type is not allowed
    """
    # Validate URL
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise BadRequest("Only HTTP and HTTPS URLs are supported")
    except Exception:
        raise BadRequest("Invalid URL format")

    # Extract filename from URL
    path = unquote(parsed.path)
    filename = os.path.basename(path) or "document"

    # Try to get extension from URL path
    ext = os.path.splitext(filename)[1].lower()

    # Download with streaming to check size
    try:
        response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise BadRequest("URL download timed out")
    except requests.exceptions.RequestException as e:
        raise BadRequest(f"Failed to download from URL: {str(e)}")

    # Check content length if available
    content_length = response.headers.get('content-length')
    if content_length and int(content_length) > MAX_URL_DOWNLOAD_SIZE:
        raise BadRequest(f"File too large. Maximum size: {MAX_URL_DOWNLOAD_SIZE // (1024*1024)}MB")

    # Try to get filename from Content-Disposition header
    content_disposition = response.headers.get('content-disposition', '')
    if 'filename=' in content_disposition:
        import re
        match = re.search(r'filename[*]?=["\']?([^"\';]+)', content_disposition)
        if match:
            filename = match.group(1)
            ext = os.path.splitext(filename)[1].lower()

    # Try to infer extension from content-type if not in URL
    if not ext:
        content_type = response.headers.get('content-type', '').split(';')[0].strip()
        type_to_ext = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/html': '.html',
            'text/markdown': '.md',
            'text/csv': '.csv',
            'text/plain': '.txt',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'application/xml': '.xml',
            'text/xml': '.xml',
        }
        ext = type_to_ext.get(content_type, '')
        if ext and not filename.endswith(ext):
            filename = filename + ext

    # Validate extension
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise BadRequest(f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Download to temp file then save via file_manager
    downloaded_size = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=8192):
        downloaded_size += len(chunk)
        if downloaded_size > MAX_URL_DOWNLOAD_SIZE:
            raise BadRequest(f"File too large. Maximum size: {MAX_URL_DOWNLOAD_SIZE // (1024*1024)}MB")
        chunks.append(chunk)

    content = b''.join(chunks)

    # Save using file_manager
    saved_path, safe_filename, file_size = file_manager.save_upload_from_bytes(
        content, filename
    )

    return saved_path, filename, file_size


def download_image(img_url: str, base_url: str, timeout: int = 10) -> tuple[bytes, str] | None:
    """
    Download an image from a URL.

    Args:
        img_url: The image URL (can be relative or absolute)
        base_url: The base URL of the page for resolving relative URLs
        timeout: Request timeout in seconds

    Returns:
        Tuple of (image_bytes, content_type) or None if download fails
    """
    try:
        # Handle relative URLs
        if not img_url.startswith(('http://', 'https://', 'data:')):
            img_url = urljoin(base_url, img_url)

        # Skip data URIs (already embedded)
        if img_url.startswith('data:'):
            return None

        response = requests.get(img_url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Check content type is an image
        content_type = response.headers.get('content-type', '').split(';')[0].strip()
        if not content_type.startswith('image/'):
            return None

        # Limit image size to 10MB
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:
            return None

        # Download image
        chunks = []
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192):
            total_size += len(chunk)
            if total_size > 10 * 1024 * 1024:  # 10MB limit
                return None
            chunks.append(chunk)

        return b''.join(chunks), content_type
    except Exception as e:
        print(f"[download_image] Failed to download {img_url}: {e}")
        return None


def extract_and_download_images_from_html(html_content: bytes, base_url: str, job_id: str) -> tuple[bytes, list[dict]]:
    """
    Extract images from HTML, download them, and optionally embed them.

    Args:
        html_content: The HTML content as bytes
        base_url: The base URL of the page
        job_id: The job ID for saving images

    Returns:
        Tuple of (modified_html_content, list of extracted images info)
    """
    try:
        html_str = html_content.decode('utf-8', errors='replace')
    except:
        html_str = html_content.decode('latin-1', errors='replace')

    # Create output directory for images
    images_dir = OUTPUT_FOLDER / job_id / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    extracted_images = []
    image_count = 0

    # Find all img tags with src attribute (handles both quoted and unquoted values)
    # Pattern explanation:
    # - <img\s+ : matches <img followed by whitespace
    # - [^>]* : matches any attributes before src
    # - src= : matches the src attribute
    # - (["\']?) : captures optional quote character (group 1)
    # - ([^"\'\s>]+) : captures the URL (group 2) - stops at quote, space, or >
    # - \1 : matches the same quote character (if any)
    # - [^>]* : matches any remaining attributes
    # - > : matches the closing bracket
    img_pattern = re.compile(r'<img\s+[^>]*src=(["\']?)([^"\'\s>]+)\1[^>]*>', re.IGNORECASE)

    def replace_image(match):
        nonlocal image_count
        full_tag = match.group(0)
        img_url = match.group(2)  # URL is now in group 2

        # Skip data URIs
        if img_url.startswith('data:'):
            return full_tag

        # Download the image
        result = download_image(img_url, base_url)
        if result is None:
            return full_tag

        img_bytes, content_type = result
        image_count += 1

        # Determine extension from content type
        ext_map = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/bmp': '.bmp',
        }
        ext = ext_map.get(content_type, '.png')

        # Save image to disk
        img_filename = f"image_{image_count}{ext}"
        img_path = images_dir / img_filename
        img_path.write_bytes(img_bytes)

        # Track extracted image
        extracted_images.append({
            "id": image_count,
            "filename": img_filename,
            "path": str(img_path),
            "original_url": img_url,
            "caption": "",
            "label": None
        })

        print(f"[extract_images] Downloaded image {image_count}: {img_url[:80]}...")

        # Embed as base64 data URI in the HTML
        b64_data = base64.b64encode(img_bytes).decode('ascii')
        data_uri = f"data:{content_type};base64,{b64_data}"

        # Replace src in the tag (handles both quoted and unquoted)
        # First try quoted, then unquoted
        new_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{data_uri}"', full_tag)
        if new_tag == full_tag:
            # No quoted src found, try unquoted
            new_tag = re.sub(r'src=([^\s>]+)', f'src="{data_uri}"', full_tag)
        return new_tag

    # Process all images
    modified_html = img_pattern.sub(replace_image, html_str)

    # Also handle srcset attributes
    srcset_pattern = re.compile(r'srcset=["\']([^"\']+)["\']', re.IGNORECASE)
    # Remove srcset to avoid browser trying to load original URLs
    modified_html = srcset_pattern.sub('', modified_html)

    # Also handle background-image in style attributes
    bg_pattern = re.compile(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', re.IGNORECASE)

    def replace_bg_image(match):
        nonlocal image_count
        full_match = match.group(0)
        img_url = match.group(1)

        if img_url.startswith('data:'):
            return full_match

        result = download_image(img_url, base_url)
        if result is None:
            return full_match

        img_bytes, content_type = result
        image_count += 1

        ext_map = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/webp': '.webp',
        }
        ext = ext_map.get(content_type, '.png')

        img_filename = f"image_{image_count}{ext}"
        img_path = images_dir / img_filename
        img_path.write_bytes(img_bytes)

        extracted_images.append({
            "id": image_count,
            "filename": img_filename,
            "path": str(img_path),
            "original_url": img_url,
            "caption": "",
            "label": "background"
        })

        b64_data = base64.b64encode(img_bytes).decode('ascii')
        return f'background-image: url("data:{content_type};base64,{b64_data}")'

    modified_html = bg_pattern.sub(replace_bg_image, modified_html)

    print(f"[extract_images] Extracted {len(extracted_images)} images from HTML")

    return modified_html.encode('utf-8'), extracted_images


def download_from_url_with_images(url: str, job_id: str = None) -> tuple[str, str, int, list[dict]]:
    """
    Download a document from a URL, extracting and embedding images for HTML.

    Args:
        url: The URL to download from
        job_id: Optional job ID for saving images (will be generated if not provided)

    Returns:
        Tuple of (saved_path, filename, file_size, extracted_images)

    Raises:
        BadRequest: If the URL is invalid or the file type is not allowed
    """
    # Validate URL
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise BadRequest("Only HTTP and HTTPS URLs are supported")
    except Exception:
        raise BadRequest("Invalid URL format")

    # Extract filename from URL
    path = unquote(parsed.path)
    filename = os.path.basename(path) or "document"

    # Try to get extension from URL path
    ext = os.path.splitext(filename)[1].lower()

    # Download with streaming to check size
    try:
        response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise BadRequest("URL download timed out")
    except requests.exceptions.RequestException as e:
        raise BadRequest(f"Failed to download from URL: {str(e)}")

    # Check content length if available
    content_length = response.headers.get('content-length')
    if content_length and int(content_length) > MAX_URL_DOWNLOAD_SIZE:
        raise BadRequest(f"File too large. Maximum size: {MAX_URL_DOWNLOAD_SIZE // (1024*1024)}MB")

    # Try to get filename from Content-Disposition header
    content_disposition = response.headers.get('content-disposition', '')
    if 'filename=' in content_disposition:
        match = re.search(r'filename[*]?=["\']?([^"\';]+)', content_disposition)
        if match:
            filename = match.group(1)
            ext = os.path.splitext(filename)[1].lower()

    # Try to infer extension from content-type if not in URL
    content_type = response.headers.get('content-type', '').split(';')[0].strip()
    if not ext:
        type_to_ext = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/html': '.html',
            'text/markdown': '.md',
            'text/csv': '.csv',
            'text/plain': '.txt',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'application/xml': '.xml',
            'text/xml': '.xml',
        }
        ext = type_to_ext.get(content_type, '')
        if ext and not filename.endswith(ext):
            filename = filename + ext

    # Validate extension
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise BadRequest(f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Download content
    downloaded_size = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=8192):
        downloaded_size += len(chunk)
        if downloaded_size > MAX_URL_DOWNLOAD_SIZE:
            raise BadRequest(f"File too large. Maximum size: {MAX_URL_DOWNLOAD_SIZE // (1024*1024)}MB")
        chunks.append(chunk)

    content = b''.join(chunks)
    extracted_images = []

    # For HTML content, extract and embed images
    is_html = ext.lower() in ('.html', '.htm') or content_type == 'text/html'
    if is_html and job_id:
        print(f"[download_from_url] Processing HTML content, extracting images...")
        content, extracted_images = extract_and_download_images_from_html(content, url, job_id)
        print(f"[download_from_url] Extracted {len(extracted_images)} images")

    # Save using file_manager
    saved_path, safe_filename, file_size = file_manager.save_upload_from_bytes(
        content, filename
    )

    return saved_path, filename, file_size, extracted_images


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


@convert_bp.route("/convert/url", methods=["POST"])
def convert_from_url():
    """
    Convert a document from a URL.

    Expects JSON with:
    - url: The URL of the document to convert
    - settings (optional): Conversion settings

    Returns:
        JSON with job_id and initial status
    """
    data = request.get_json()

    if not data or "url" not in data:
        raise BadRequest("No URL provided")

    url = data["url"].strip()
    if not url:
        raise BadRequest("Empty URL provided")

    # Load saved user settings as the base
    settings = load_user_settings()

    # Override with any settings provided in the request
    if "settings" in data:
        def deep_merge(base, updates):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        deep_merge(settings, data["settings"])

    print(f"[convert/url] Converting from URL: {url}")
    print(f"[convert/url] Using OCR backend: {settings.get('ocr', {}).get('backend', 'unknown')}")

    # Generate job ID first so we can use it for image extraction
    job_id = str(uuid.uuid4())

    # Download the file from URL (with image extraction for HTML)
    saved_path, filename, file_size, extracted_images = download_from_url_with_images(url, job_id)

    if extracted_images:
        print(f"[convert/url] Pre-extracted {len(extracted_images)} images from HTML")

    # Detect input format
    input_format = converter_service.detect_input_format(filename)

    # Create conversion job with pre-assigned ID
    job = converter_service.create_job(saved_path, filename, settings, job_id=job_id)

    # Store pre-extracted images in the job
    if extracted_images:
        job.extracted_images = extracted_images

    # Create history entry
    history_service.create_entry(
        job_id=job.id,
        filename=os.path.basename(saved_path),
        original_filename=filename,
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
        "filename": filename,
        "source_url": url,
        "input_format": input_format,
        "status": "processing",
        "message": "Conversion started",
        "images_preextracted": len(extracted_images) if extracted_images else 0
    }), 202


@convert_bp.route("/convert/url/batch", methods=["POST"])
def convert_from_urls_batch():
    """
    Convert multiple documents from URLs.

    Expects JSON with:
    - urls: Array of URLs to convert
    - settings (optional): Conversion settings

    Returns:
        JSON with list of job_ids and statuses
    """
    data = request.get_json()

    if not data or "urls" not in data:
        raise BadRequest("No URLs provided")

    urls = data["urls"]
    if not isinstance(urls, list) or not urls:
        raise BadRequest("URLs must be a non-empty array")

    # Load saved user settings as the base
    settings = load_user_settings()

    # Override with any settings provided in the request
    if "settings" in data:
        def deep_merge(base, updates):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        deep_merge(settings, data["settings"])

    print(f"[convert/url/batch] Converting {len(urls)} URLs")
    print(f"[convert/url/batch] Using OCR backend: {settings.get('ocr', {}).get('backend', 'unknown')}")

    jobs = []
    for url in urls:
        url = url.strip() if isinstance(url, str) else ""
        if not url:
            jobs.append({
                "url": url,
                "status": "rejected",
                "error": "Empty URL"
            })
            continue

        try:
            # Generate job ID first so we can use it for image extraction
            job_id = str(uuid.uuid4())

            # Download the file from URL (with image extraction for HTML)
            saved_path, filename, file_size, extracted_images = download_from_url_with_images(url, job_id)

            # Detect input format
            input_format = converter_service.detect_input_format(filename)

            # Create conversion job with pre-assigned ID
            job = converter_service.create_job(saved_path, filename, settings, job_id=job_id)

            # Store pre-extracted images in the job
            if extracted_images:
                job.extracted_images = extracted_images

            # Create history entry
            history_service.create_entry(
                job_id=job.id,
                filename=os.path.basename(saved_path),
                original_filename=filename,
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
                "url": url,
                "filename": filename,
                "input_format": input_format,
                "status": "processing",
                "images_preextracted": len(extracted_images) if extracted_images else 0
            })

        except BadRequest as e:
            jobs.append({
                "url": url,
                "status": "rejected",
                "error": str(e.description)
            })
        except Exception as e:
            jobs.append({
                "url": url,
                "status": "rejected",
                "error": f"Failed to process URL: {str(e)}"
            })

    return jsonify({
        "jobs": jobs,
        "total": len(jobs),
        "message": f"Started {len([j for j in jobs if j.get('status') == 'processing'])} conversions"
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

    if job:
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

    # Fallback: Check history and output directory (for multi-worker scenarios)
    history_entry = history_service.get_entry(job_id)
    if history_entry and history_entry.get("status") == "completed":
        output_dir = OUTPUT_FOLDER / job_id

        # Determine available formats from files on disk
        formats_available = []
        format_extensions = {
            "markdown": ".md",
            "html": ".html",
            "json": ".json",
            "text": ".txt",
            "doctags": ".doctags"
        }
        for fmt, ext in format_extensions.items():
            if list(output_dir.glob(f"*{ext}")):
                formats_available.append(fmt)

        # Count images and tables
        images_dir = output_dir / "images"
        tables_dir = output_dir / "tables"

        # Count all image types, not just PNG
        images_count = 0
        if images_dir.exists():
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg', '*.bmp']
            for ext in image_extensions:
                images_count += len(list(images_dir.glob(ext)))

        tables_count = len(list(tables_dir.glob("*.csv"))) if tables_dir.exists() else 0

        # Try to read markdown preview
        md_preview = ""
        md_files = list(output_dir.glob("*.md"))
        if md_files:
            try:
                with open(md_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    md_preview = content[:5000] if len(content) > 5000 else content
            except Exception:
                pass

        return jsonify({
            "job_id": job_id,
            "status": "completed",
            "confidence": history_entry.get("confidence"),
            "formats_available": formats_available,
            "result": {
                "markdown_preview": md_preview,
                "formats_available": formats_available,
                "images_count": images_count,
                "tables_count": tables_count,
                "chunks_count": 0
            },
            "images_count": images_count,
            "tables_count": tables_count,
            "chunks_count": 0,
            "completed_at": history_entry.get("completed_at")
        })

    raise NotFound(f"Job {job_id} not found")


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

    if job:
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

    # Fallback: Check if images exist on disk (for multi-worker scenarios)
    images_dir = OUTPUT_FOLDER / job_id / "images"
    if images_dir.exists():
        images = []
        # Look for all common image formats
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg', '*.bmp']
        all_image_files = []
        for ext in image_extensions:
            all_image_files.extend(images_dir.glob(ext))

        # Sort by filename to maintain consistent order
        for i, img_path in enumerate(sorted(all_image_files, key=lambda p: p.name)):
            images.append({
                "id": i + 1,
                "filename": img_path.name,
                "path": str(img_path),
                "caption": "",
                "label": None
            })

        if images:
            return jsonify({
                "job_id": job_id,
                "images": images,
                "count": len(images)
            })

    # Check if job exists in history
    history_entry = history_service.get_entry(job_id)
    if history_entry:
        # Job completed but no images extracted
        return jsonify({
            "job_id": job_id,
            "images": [],
            "count": 0
        })

    raise NotFound(f"Job {job_id} not found")


def get_mimetype_for_image(filename: str) -> str:
    """Get the correct MIME type for an image file based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    mimetypes = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp',
        '.ico': 'image/x-icon',
    }
    return mimetypes.get(ext, 'application/octet-stream')


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

    if job:
        if job.status != ConversionStatus.COMPLETED:
            return jsonify({"error": "Conversion not completed"}), 400

        # Find the image
        image = next((img for img in job.extracted_images if img["id"] == image_id), None)
        if not image:
            raise NotFound(f"Image {image_id} not found")

        image_path = image.get("path")
        if not image_path or not os.path.exists(image_path):
            raise NotFound("Image file not found")

        filename = image.get("filename", f"image_{image_id}.png")
        mimetype = get_mimetype_for_image(filename)
        
        return send_file(
            image_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    # Fallback: Look for image on disk (for multi-worker scenarios)
    images_dir = OUTPUT_FOLDER / job_id / "images"
    if images_dir.exists():
        # Find all image files with common extensions
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.svg', '*.bmp']
        all_image_files = []
        for ext in image_extensions:
            all_image_files.extend(images_dir.glob(ext))
        
        # Sort by filename to maintain consistent order
        image_files = sorted(all_image_files, key=lambda p: p.name)
        
        if 0 < image_id <= len(image_files):
            image_path = image_files[image_id - 1]
            mimetype = get_mimetype_for_image(image_path.name)
            return send_file(
                str(image_path),
                mimetype=mimetype,
                as_attachment=True,
                download_name=image_path.name
            )
        raise NotFound(f"Image {image_id} not found")

    raise NotFound(f"Job {job_id} not found")


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

    if job:
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

    # Fallback: Check if tables exist on disk (for multi-worker scenarios)
    tables_dir = OUTPUT_FOLDER / job_id / "tables"
    if tables_dir.exists():
        tables = []
        for i, csv_path in enumerate(sorted(tables_dir.glob("*.csv"))):
            table_data = {
                "id": i + 1,
                "label": None,
                "caption": "",
                "rows": [],
                "csv_path": str(csv_path),
            }
            # Try to read CSV content
            try:
                import csv
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    table_data["rows"] = list(reader)
            except Exception:
                pass

            # Check for corresponding image
            img_path = tables_dir / f"table_{i+1}.png"
            if img_path.exists():
                table_data["image_path"] = str(img_path)

            tables.append(table_data)

        return jsonify({
            "job_id": job_id,
            "tables": tables,
            "count": len(tables)
        })

    # Check if job exists in history
    history_entry = history_service.get_entry(job_id)
    if history_entry:
        # Job completed but no tables extracted
        return jsonify({
            "job_id": job_id,
            "tables": [],
            "count": 0
        })

    raise NotFound(f"Job {job_id} not found")


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


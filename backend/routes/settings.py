"""Settings API endpoints."""

import json
from pathlib import Path
from flask import Blueprint, request, jsonify

from config import (
    DEFAULT_CONVERSION_SETTINGS,
    BACKEND_DIR,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    OCR_BACKENDS,
    ACCELERATOR_DEVICES,
    TABLE_MODES,
    OCR_LANGUAGES,
)

settings_bp = Blueprint("settings", __name__)

# Settings file path
SETTINGS_FILE = BACKEND_DIR / "user_settings.json"


def load_settings() -> dict:
    """Load user settings from file or return defaults."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONVERSION_SETTINGS.copy()


def save_settings(settings: dict) -> bool:
    """Save user settings to file."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except IOError:
        return False


def merge_settings(current, new):
    """Deep merge settings dictionaries."""
    for key, value in new.items():
        if key in current:
            if isinstance(current[key], dict) and isinstance(value, dict):
                merge_settings(current[key], value)
            else:
                current[key] = value
        else:
            current[key] = value
    return current


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """
    Get current conversion settings.

    Returns:
        JSON with current settings
    """
    settings = load_settings()
    return jsonify({
        "settings": settings,
        "defaults": DEFAULT_CONVERSION_SETTINGS
    })


@settings_bp.route("/settings", methods=["PUT"])
def update_settings():
    """
    Update conversion settings.

    Expects JSON body with settings to update.

    Returns:
        JSON with updated settings
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    new_settings = request.get_json()

    # Validate settings structure
    current_settings = load_settings()

    # Merge settings (only update provided fields)
    updated_settings = merge_settings(current_settings, new_settings)

    if save_settings(updated_settings):
        return jsonify({
            "message": "Settings updated successfully",
            "settings": updated_settings
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/reset", methods=["POST"])
def reset_settings():
    """
    Reset settings to defaults.

    Returns:
        JSON with default settings
    """
    if save_settings(DEFAULT_CONVERSION_SETTINGS):
        return jsonify({
            "message": "Settings reset to defaults",
            "settings": DEFAULT_CONVERSION_SETTINGS
        })
    else:
        return jsonify({"error": "Failed to reset settings"}), 500


@settings_bp.route("/settings/formats", methods=["GET"])
def get_formats():
    """Get supported input and output formats."""
    return jsonify({
        "input_formats": SUPPORTED_INPUT_FORMATS,
        "output_formats": SUPPORTED_OUTPUT_FORMATS
    })


@settings_bp.route("/settings/ocr", methods=["GET"])
def get_ocr_settings():
    """Get OCR-specific settings."""
    settings = load_settings()
    return jsonify({
        "ocr": settings.get("ocr", DEFAULT_CONVERSION_SETTINGS["ocr"]),
        "available_languages": OCR_LANGUAGES,
        "available_backends": OCR_BACKENDS,
        "options": {
            "force_full_page_ocr": {
                "description": "OCR the entire page instead of just detected text regions",
                "default": False
            },
            "use_gpu": {
                "description": "Use GPU acceleration for OCR (EasyOCR only)",
                "default": False
            },
            "confidence_threshold": {
                "description": "Minimum confidence threshold for OCR results",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0
            },
            "bitmap_area_threshold": {
                "description": "Minimum area ratio for bitmap regions to trigger OCR",
                "default": 0.05,
                "min": 0.0,
                "max": 1.0
            }
        }
    })


@settings_bp.route("/settings/ocr", methods=["PUT"])
def update_ocr_settings():
    """Update OCR-specific settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    ocr_settings = request.get_json()
    current_settings = load_settings()

    # Validate OCR settings
    if "enabled" in ocr_settings:
        if not isinstance(ocr_settings["enabled"], bool):
            return jsonify({"error": "enabled must be a boolean"}), 400

    if "language" in ocr_settings:
        if not isinstance(ocr_settings["language"], str):
            return jsonify({"error": "language must be a string"}), 400

    if "backend" in ocr_settings:
        valid_backends = [b["id"] for b in OCR_BACKENDS]
        if ocr_settings["backend"] not in valid_backends:
            return jsonify({"error": f"backend must be one of: {', '.join(valid_backends)}"}), 400

    if "force_full_page_ocr" in ocr_settings:
        if not isinstance(ocr_settings["force_full_page_ocr"], bool):
            return jsonify({"error": "force_full_page_ocr must be a boolean"}), 400

    if "use_gpu" in ocr_settings:
        if not isinstance(ocr_settings["use_gpu"], bool):
            return jsonify({"error": "use_gpu must be a boolean"}), 400

    if "confidence_threshold" in ocr_settings:
        if not isinstance(ocr_settings["confidence_threshold"], (int, float)):
            return jsonify({"error": "confidence_threshold must be a number"}), 400
        if not 0 <= ocr_settings["confidence_threshold"] <= 1:
            return jsonify({"error": "confidence_threshold must be between 0 and 1"}), 400

    # Update OCR settings
    current_settings["ocr"] = {
        **current_settings.get("ocr", {}),
        **ocr_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "OCR settings updated",
            "ocr": current_settings["ocr"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/tables", methods=["GET"])
def get_table_settings():
    """Get table extraction settings."""
    settings = load_settings()
    return jsonify({
        "tables": settings.get("tables", DEFAULT_CONVERSION_SETTINGS["tables"]),
        "available_modes": TABLE_MODES,
        "options": {
            "enabled": {
                "description": "Enable table detection and extraction",
                "default": True
            },
            "structure_extraction": {
                "description": "Preserve table structure and cell relationships",
                "default": True
            },
            "mode": {
                "description": "Table detection mode (fast or accurate)",
                "default": "accurate"
            },
            "do_cell_matching": {
                "description": "Match cell content to table structure",
                "default": True
            }
        }
    })


@settings_bp.route("/settings/tables", methods=["PUT"])
def update_table_settings():
    """Update table extraction settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    table_settings = request.get_json()
    current_settings = load_settings()

    # Validate table settings
    if "mode" in table_settings:
        valid_modes = [m["id"] for m in TABLE_MODES]
        if table_settings["mode"] not in valid_modes:
            return jsonify({"error": f"mode must be one of: {', '.join(valid_modes)}"}), 400

    current_settings["tables"] = {
        **current_settings.get("tables", {}),
        **table_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Table settings updated",
            "tables": current_settings["tables"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/images", methods=["GET"])
def get_image_settings():
    """Get image handling settings."""
    settings = load_settings()
    return jsonify({
        "images": settings.get("images", DEFAULT_CONVERSION_SETTINGS["images"]),
        "options": {
            "extract": {
                "description": "Extract embedded images from documents",
                "default": True
            },
            "classify": {
                "description": "Automatically classify and tag images",
                "default": True
            },
            "generate_page_images": {
                "description": "Generate images of each page",
                "default": False
            },
            "generate_picture_images": {
                "description": "Extract embedded pictures as separate images",
                "default": True
            },
            "generate_table_images": {
                "description": "Extract tables as images",
                "default": True
            },
            "images_scale": {
                "description": "Scale factor for extracted images (1.0 = original size)",
                "default": 1.0,
                "min": 0.1,
                "max": 4.0
            }
        }
    })


@settings_bp.route("/settings/images", methods=["PUT"])
def update_image_settings():
    """Update image handling settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    image_settings = request.get_json()
    current_settings = load_settings()

    # Validate image settings
    if "images_scale" in image_settings:
        if not isinstance(image_settings["images_scale"], (int, float)):
            return jsonify({"error": "images_scale must be a number"}), 400
        if not 0.1 <= image_settings["images_scale"] <= 4.0:
            return jsonify({"error": "images_scale must be between 0.1 and 4.0"}), 400

    current_settings["images"] = {
        **current_settings.get("images", {}),
        **image_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Image settings updated",
            "images": current_settings["images"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/performance", methods=["GET"])
def get_performance_settings():
    """Get performance/accelerator settings."""
    settings = load_settings()
    return jsonify({
        "performance": settings.get("performance", DEFAULT_CONVERSION_SETTINGS["performance"]),
        "available_devices": ACCELERATOR_DEVICES,
        "options": {
            "device": {
                "description": "Processing device to use",
                "default": "auto"
            },
            "num_threads": {
                "description": "Number of CPU threads to use",
                "default": 4,
                "min": 1,
                "max": 32
            },
            "document_timeout": {
                "description": "Maximum time (seconds) for document processing (null = no limit)",
                "default": None
            }
        }
    })


@settings_bp.route("/settings/performance", methods=["PUT"])
def update_performance_settings():
    """Update performance/accelerator settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    perf_settings = request.get_json()
    current_settings = load_settings()

    # Validate performance settings
    if "device" in perf_settings:
        valid_devices = [d["id"] for d in ACCELERATOR_DEVICES]
        if perf_settings["device"] not in valid_devices:
            return jsonify({"error": f"device must be one of: {', '.join(valid_devices)}"}), 400

    if "num_threads" in perf_settings:
        if not isinstance(perf_settings["num_threads"], int):
            return jsonify({"error": "num_threads must be an integer"}), 400
        if not 1 <= perf_settings["num_threads"] <= 32:
            return jsonify({"error": "num_threads must be between 1 and 32"}), 400

    if "document_timeout" in perf_settings:
        if perf_settings["document_timeout"] is not None:
            if not isinstance(perf_settings["document_timeout"], (int, float)):
                return jsonify({"error": "document_timeout must be a number or null"}), 400
            if perf_settings["document_timeout"] <= 0:
                return jsonify({"error": "document_timeout must be positive"}), 400

    current_settings["performance"] = {
        **current_settings.get("performance", {}),
        **perf_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Performance settings updated",
            "performance": current_settings["performance"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/chunking", methods=["GET"])
def get_chunking_settings():
    """Get RAG chunking settings."""
    settings = load_settings()
    return jsonify({
        "chunking": settings.get("chunking", DEFAULT_CONVERSION_SETTINGS["chunking"]),
        "options": {
            "enabled": {
                "description": "Enable document chunking for RAG applications",
                "default": False
            },
            "max_tokens": {
                "description": "Maximum tokens per chunk",
                "default": 512,
                "min": 64,
                "max": 8192
            },
            "merge_peers": {
                "description": "Merge undersized chunks with similar metadata",
                "default": True
            }
        }
    })


@settings_bp.route("/settings/chunking", methods=["PUT"])
def update_chunking_settings():
    """Update RAG chunking settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    chunking_settings = request.get_json()
    current_settings = load_settings()

    # Validate chunking settings
    if "max_tokens" in chunking_settings:
        if not isinstance(chunking_settings["max_tokens"], int):
            return jsonify({"error": "max_tokens must be an integer"}), 400
        if not 64 <= chunking_settings["max_tokens"] <= 8192:
            return jsonify({"error": "max_tokens must be between 64 and 8192"}), 400

    current_settings["chunking"] = {
        **current_settings.get("chunking", {}),
        **chunking_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Chunking settings updated",
            "chunking": current_settings["chunking"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


@settings_bp.route("/settings/output", methods=["GET"])
def get_output_settings():
    """Get output format settings."""
    settings = load_settings()
    return jsonify({
        "output": settings.get("output", DEFAULT_CONVERSION_SETTINGS["output"]),
        "available_formats": SUPPORTED_OUTPUT_FORMATS
    })


@settings_bp.route("/settings/output", methods=["PUT"])
def update_output_settings():
    """Update output format settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    output_settings = request.get_json()
    current_settings = load_settings()

    # Validate default format
    valid_formats = [f["id"] for f in SUPPORTED_OUTPUT_FORMATS]
    if "default_format" in output_settings:
        if output_settings["default_format"] not in valid_formats:
            return jsonify({
                "error": f"Invalid format. Valid formats: {', '.join(valid_formats)}"
            }), 400

    current_settings["output"] = {
        **current_settings.get("output", {}),
        **output_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Output settings updated",
            "output": current_settings["output"]
        })
    else:
        return jsonify({"error": "Failed to save settings"}), 500


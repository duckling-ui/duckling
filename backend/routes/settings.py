"""Settings API endpoints."""

import json
import subprocess
import sys
import platform
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

# OCR backend package mappings
OCR_PACKAGES = {
    "easyocr": {
        "packages": ["easyocr"],
        "pip_installable": True,
        "description": "EasyOCR - Multi-language OCR with GPU support",
        "note": "First run will download language models (~100MB per language)"
    },
    "tesseract": {
        "packages": ["pytesseract"],
        "pip_installable": True,
        "system_dependency": True,
        "description": "Tesseract OCR - Classic OCR engine",
        "note": "Requires Tesseract to be installed on your system (brew install tesseract / apt-get install tesseract-ocr)"
    },
    "ocrmac": {
        "packages": ["ocrmac"],
        "pip_installable": True,
        "platform": "darwin",
        "description": "macOS Vision OCR - Native Apple OCR",
        "note": "macOS only - uses built-in Vision framework"
    },
    "rapidocr": {
        "packages": ["rapidocr-onnxruntime"],
        "pip_installable": True,
        "description": "RapidOCR - Fast OCR with ONNX runtime",
        "note": "Lightweight and fast, good for CPU-only systems"
    }
}


def check_ocr_backend_installed(backend: str) -> dict:
    """Check if an OCR backend is installed and available."""
    result = {
        "backend": backend,
        "installed": False,
        "available": False,
        "error": None
    }

    try:
        if backend == "easyocr":
            import easyocr
            result["installed"] = True
            result["available"] = True
        elif backend == "tesseract":
            import pytesseract
            result["installed"] = True
            # Check if tesseract binary is available
            try:
                pytesseract.get_tesseract_version()
                result["available"] = True
            except Exception as e:
                result["error"] = f"pytesseract installed but Tesseract binary not found: {e}"
        elif backend == "ocrmac":
            if platform.system() != "Darwin":
                result["error"] = "OcrMac is only available on macOS"
            else:
                import ocrmac
                result["installed"] = True
                result["available"] = True
        elif backend == "rapidocr":
            try:
                from rapidocr_onnxruntime import RapidOCR
                result["installed"] = True
                result["available"] = True
            except ImportError:
                # Try alternative import
                try:
                    import rapidocr_onnxruntime
                    result["installed"] = True
                    result["available"] = True
                except ImportError:
                    pass
    except ImportError as e:
        result["error"] = f"Package not installed: {e}"
    except Exception as e:
        result["error"] = str(e)

    return result


def install_ocr_backend(backend: str) -> dict:
    """Install an OCR backend package."""
    if backend not in OCR_PACKAGES:
        return {"success": False, "error": f"Unknown backend: {backend}"}

    pkg_info = OCR_PACKAGES[backend]

    # Check platform compatibility
    if "platform" in pkg_info and platform.system().lower() != pkg_info["platform"]:
        return {
            "success": False,
            "error": f"{backend} is only available on {pkg_info['platform']}"
        }

    # Check if system dependency is required
    if pkg_info.get("system_dependency"):
        return {
            "success": False,
            "error": f"{backend} requires system-level installation. {pkg_info.get('note', '')}",
            "requires_system_install": True
        }

    # Install pip packages
    packages = pkg_info["packages"]
    results = []

    for package in packages:
        try:
            print(f"[settings] Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                results.append({"package": package, "success": True})
                print(f"[settings] Successfully installed {package}")
            else:
                results.append({
                    "package": package,
                    "success": False,
                    "error": result.stderr
                })
                print(f"[settings] Failed to install {package}: {result.stderr}")
        except subprocess.TimeoutExpired:
            results.append({
                "package": package,
                "success": False,
                "error": "Installation timed out"
            })
        except Exception as e:
            results.append({
                "package": package,
                "success": False,
                "error": str(e)
            })

    all_success = all(r["success"] for r in results)

    return {
        "success": all_success,
        "packages": results,
        "note": pkg_info.get("note", "")
    }

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


@settings_bp.route("/settings/ocr/backends", methods=["GET"])
def get_ocr_backends_status():
    """Get status of all OCR backends (installed/available)."""
    backends_status = []

    for backend in OCR_BACKENDS:
        backend_id = backend["id"]
        status = check_ocr_backend_installed(backend_id)
        pkg_info = OCR_PACKAGES.get(backend_id, {})

        backends_status.append({
            "id": backend_id,
            "name": backend["name"],
            "description": backend["description"],
            "installed": status["installed"],
            "available": status["available"],
            "error": status["error"],
            "pip_installable": pkg_info.get("pip_installable", False),
            "requires_system_install": pkg_info.get("system_dependency", False),
            "platform": pkg_info.get("platform"),
            "note": pkg_info.get("note", "")
        })

    return jsonify({
        "backends": backends_status,
        "current_platform": platform.system().lower()
    })


@settings_bp.route("/settings/ocr/backends/<backend_id>/check", methods=["GET"])
def check_ocr_backend(backend_id: str):
    """Check if a specific OCR backend is installed and available."""
    if backend_id not in [b["id"] for b in OCR_BACKENDS]:
        return jsonify({"error": f"Unknown backend: {backend_id}"}), 404

    status = check_ocr_backend_installed(backend_id)
    pkg_info = OCR_PACKAGES.get(backend_id, {})

    return jsonify({
        **status,
        "pip_installable": pkg_info.get("pip_installable", False),
        "requires_system_install": pkg_info.get("system_dependency", False),
        "note": pkg_info.get("note", "")
    })


@settings_bp.route("/settings/ocr/backends/<backend_id>/install", methods=["POST"])
def install_ocr_backend_endpoint(backend_id: str):
    """Install an OCR backend package."""
    if backend_id not in [b["id"] for b in OCR_BACKENDS]:
        return jsonify({"error": f"Unknown backend: {backend_id}"}), 404

    # Check if already installed
    status = check_ocr_backend_installed(backend_id)
    if status["available"]:
        return jsonify({
            "message": f"{backend_id} is already installed and available",
            "already_installed": True
        })

    # Try to install
    result = install_ocr_backend(backend_id)

    if result["success"]:
        # Verify installation
        new_status = check_ocr_backend_installed(backend_id)
        return jsonify({
            "message": f"Successfully installed {backend_id}",
            "success": True,
            "installed": new_status["installed"],
            "available": new_status["available"],
            "note": result.get("note", "")
        })
    else:
        return jsonify({
            "message": f"Failed to install {backend_id}",
            "success": False,
            "error": result.get("error", "Unknown error"),
            "requires_system_install": result.get("requires_system_install", False),
            "packages": result.get("packages", [])
        }), 400


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

        # Check if the backend is available, offer to install if not
        backend_status = check_ocr_backend_installed(ocr_settings["backend"])
        if not backend_status["available"]:
            # Check if auto_install flag is set
            auto_install = request.args.get("auto_install", "false").lower() == "true"

            if auto_install:
                # Try to install the backend
                install_result = install_ocr_backend(ocr_settings["backend"])
                if not install_result["success"]:
                    return jsonify({
                        "error": f"Backend '{ocr_settings['backend']}' is not available and installation failed",
                        "install_error": install_result.get("error"),
                        "requires_system_install": install_result.get("requires_system_install", False),
                        "backend_status": backend_status
                    }), 400
                # Re-check after installation
                backend_status = check_ocr_backend_installed(ocr_settings["backend"])
                if not backend_status["available"]:
                    return jsonify({
                        "error": f"Backend '{ocr_settings['backend']}' installed but not available",
                        "backend_status": backend_status
                    }), 400
            else:
                # Return info about the unavailable backend
                pkg_info = OCR_PACKAGES.get(ocr_settings["backend"], {})
                return jsonify({
                    "error": f"Backend '{ocr_settings['backend']}' is not installed",
                    "backend_status": backend_status,
                    "pip_installable": pkg_info.get("pip_installable", False),
                    "requires_system_install": pkg_info.get("system_dependency", False),
                    "note": pkg_info.get("note", ""),
                    "hint": "Add ?auto_install=true to automatically install pip-installable backends"
                }), 400

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


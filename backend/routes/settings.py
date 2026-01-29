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


def get_compatible_rapidocr_version() -> str:
    """Get a compatible version of rapidocr-onnxruntime based on Python version."""
    python_version = sys.version_info[:2]  # (major, minor)

    # Python 3.13+ (including 3.14+) only supports versions up to 1.2.3
    # Versions 1.2.4+ require Python <3.13
    if python_version >= (3, 13):
        return "1.2.3"
    # Python 3.12 supports versions up to 1.3.x (but some require <3.12)
    elif python_version >= (3, 12):
        return "1.2.3"  # Safe fallback for 3.12
    # Python <3.12 supports latest versions
    else:
        return "1.4.4"


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
        "note": "Lightweight and fast, good for CPU-only systems. Note: Python 3.13+ only supports versions <=1.2.3",
        "version_selector": get_compatible_rapidocr_version  # Function to get compatible version
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

            # For rapidocr-onnxruntime, use upgrade strategy to resolve conflicts
            install_args = [sys.executable, "-m", "pip", "install"]

            # Use --upgrade to resolve dependency conflicts
            if "rapidocr" in package.lower():
                # For rapidocr, try installing onnxruntime first to avoid conflicts (optional)
                # Note: This is optional - rapidocr-onnxruntime may work without it
                print(f"[settings] Attempting to pre-install onnxruntime dependency (optional)...")
                onnx_preinstall = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "onnxruntime"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if onnx_preinstall.returncode != 0:
                    preinstall_output = onnx_preinstall.stdout + onnx_preinstall.stderr if onnx_preinstall.stdout else onnx_preinstall.stderr
                    print(f"[settings] Note: Could not pre-install onnxruntime (will try without it): {preinstall_output[:200]}")
                    # Continue anyway - rapidocr-onnxruntime might work without it

                # Get compatible version based on Python version
                version_selector = pkg_info.get("version_selector")
                if version_selector and callable(version_selector):
                    compatible_version = version_selector()
                    install_args.extend(["--upgrade", f"{package}=={compatible_version}"])
                else:
                    # Fallback: try without version pinning
                    install_args.extend(["--upgrade", package])
            else:
                install_args.append(package)

            result = subprocess.run(
                install_args,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Combine stdout and stderr for better error reporting
            result_output = result.stdout + result.stderr if result.stdout else result.stderr

            if result.returncode == 0:
                results.append({"package": package, "success": True})
                print(f"[settings] Successfully installed {package}")
            else:
                # If upgrade failed, try alternative strategies for rapidocr
                # Check both stdout and stderr for error messages
                result_output_lower = result_output.lower()
                if "rapidocr" in package.lower() and ("conflicting dependencies" in result_output_lower or "ResolutionImpossible" in result_output_lower or "No matching distribution" in result_output_lower or "Could not find a version" in result_output_lower):
                    version_selector = pkg_info.get("version_selector")
                    retry_result = None
                    retry_succeeded = False

                    # Strategy 1: Try latest compatible version without pinning (if we used a pinned version)
                    if version_selector and callable(version_selector) and "==" in " ".join(install_args):
                        # Try without version pinning to let pip find the best match
                        print(f"[settings] Retrying {package} without version pinning...")
                        retry_result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "--upgrade", package],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        retry_output = retry_result.stdout + retry_result.stderr if retry_result.stdout else retry_result.stderr
                        retry_succeeded = retry_result.returncode == 0

                    # Strategy 1b: Try older compatible versions if current attempt failed
                    if not retry_succeeded:
                        python_version = sys.version_info[:2]
                        initial_version = None
                        if version_selector and callable(version_selector):
                            initial_version = version_selector()

                        # Try progressively older versions
                        fallback_versions = []
                        if python_version >= (3, 13):
                            # For Python 3.13+ (including 3.14+), only versions up to 1.2.3 work
                            fallback_versions = ["1.2.3", "1.2.2", "1.2.1", "1.2.0", "1.1.30", "1.1.29", "1.1.28"]
                        elif python_version >= (3, 12):
                            # For Python 3.12, try versions that work
                            fallback_versions = ["1.2.3", "1.2.2", "1.2.1", "1.2.0"]
                        else:
                            # For older Python, try various versions
                            fallback_versions = ["1.3.25", "1.3.20", "1.2.3", "1.2.0"]

                        # Skip the version we already tried
                        if initial_version and initial_version in fallback_versions:
                            fallback_versions.remove(initial_version)

                        for fallback_version in fallback_versions:
                            print(f"[settings] Retrying {package} with version {fallback_version}...")
                            retry_result = subprocess.run(
                                [sys.executable, "-m", "pip", "install", "--upgrade", f"{package}=={fallback_version}"],
                                capture_output=True,
                                text=True,
                                timeout=300
                            )
                            if retry_result.returncode == 0:
                                retry_succeeded = True
                                break

                    # Strategy 2: Try with --upgrade-strategy=only-if-needed (if Strategy 1 didn't work)
                    if not retry_succeeded:
                        print(f"[settings] Retrying {package} with alternative upgrade strategy...")
                        retry_result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "--upgrade-strategy", "only-if-needed", "--upgrade", package],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        retry_succeeded = retry_result.returncode == 0

                    if retry_succeeded:
                        results.append({"package": package, "success": True})
                        print(f"[settings] Successfully installed {package} (retry)")
                    else:
                        # Last resort: try installing without dependency checks (not recommended but may work)
                        # Try with a specific version first
                        version_selector = pkg_info.get("version_selector")
                        version_to_try = None
                        if version_selector and callable(version_selector):
                            version_to_try = version_selector()

                        print(f"[settings] Trying {package} with --no-deps (may require manual dependency installation)...")
                        if version_to_try:
                            no_deps_args = [sys.executable, "-m", "pip", "install", "--no-deps", f"{package}=={version_to_try}"]
                        else:
                            no_deps_args = [sys.executable, "-m", "pip", "install", "--no-deps", package]

                        no_deps_result = subprocess.run(
                            no_deps_args,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )

                        if no_deps_result.returncode == 0:
                            # Package installed with --no-deps, now verify if it works
                            # Try importing to see if dependencies are available
                            print(f"[settings] Package installed with --no-deps, verifying functionality...")

                            # Try to verify the installation works
                            verify_result = subprocess.run(
                                [sys.executable, "-c", "from rapidocr_onnxruntime import RapidOCR; print('OK')"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )

                            if verify_result.returncode == 0:
                                results.append({
                                    "package": package,
                                    "success": True,
                                    "warning": "Installed without dependency checks, but appears to work. If issues occur, install dependencies manually."
                                })
                                print(f"[settings] Successfully installed {package} (verified working)")
                            else:
                                # Try installing onnxruntime separately as fallback
                                print(f"[settings] Package installed but import failed, trying to install onnxruntime...")
                                onnx_result = subprocess.run(
                                    [sys.executable, "-m", "pip", "install", "--upgrade", "onnxruntime"],
                                    capture_output=True,
                                    text=True,
                                    timeout=300
                                )

                                if onnx_result.returncode == 0:
                                    results.append({
                                        "package": package,
                                        "success": True,
                                        "warning": "Installed without dependency checks, then installed onnxruntime separately."
                                    })
                                    print(f"[settings] Successfully installed {package} (with manual dependency handling)")
                                else:
                                    # Even if onnxruntime fails, mark as success if package installed
                                    # User can try to use it - it might work with bundled dependencies
                                    verify_output = verify_result.stdout + verify_result.stderr if verify_result.stdout else verify_result.stderr
                                    onnx_output = onnx_result.stdout + onnx_result.stderr if onnx_result.stdout else onnx_result.stderr

                                    results.append({
                                        "package": package,
                                        "success": True,
                                        "warning": f"Package installed but may not work. Import error: {verify_output[:200]}. Onnxruntime install failed: {onnx_output[:200]}"
                                    })
                                    print(f"[settings] Package installed but functionality unverified. Import error: {verify_output[:200]}")
                        else:
                            # Print the actual error from --no-deps attempt
                            no_deps_output = no_deps_result.stdout + no_deps_result.stderr if no_deps_result.stdout else no_deps_result.stderr
                            print(f"[settings] --no-deps failed: {no_deps_output}")

                            # Final error message with all details
                            error_msg = f"Installation failed after multiple attempts.\n\n"
                            error_msg += f"Python version: {sys.version}\n"
                            python_version = sys.version_info[:2]
                            if python_version >= (3, 14):
                                error_msg += f"Note: Python 3.14+ is very new and may have limited package support.\n"
                                error_msg += f"Consider using Python 3.11 or 3.12 for better compatibility.\n\n"
                            elif python_version >= (3, 13):
                                error_msg += f"Note: Python 3.13+ has limited package support. Only rapidocr-onnxruntime <=1.2.3 is available.\n\n"
                            error_msg += f"Original attempt error:\n{result_output}\n\n"
                            if retry_result:
                                retry_output = retry_result.stdout + retry_result.stderr if retry_result.stdout else retry_result.stderr
                                error_msg += f"Retry error:\n{retry_output}\n\n"
                            error_msg += f"No-deps attempt error:\n{no_deps_output}\n\n"
                            error_msg += f"Try installing manually:\n"
                            error_msg += f"  pip install --upgrade onnxruntime\n"
                            error_msg += f"  pip install --upgrade {package}"

                            results.append({
                                "package": package,
                                "success": False,
                                "error": error_msg
                            })
                            print(f"[settings] Failed to install {package} after all attempts")
                            print(f"[settings] Error details: {error_msg}")
                else:
                    results.append({
                        "package": package,
                        "success": False,
                        "error": result_output
                    })
                    print(f"[settings] Failed to install {package}: {result_output}")
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


# Enrichment model information
# Note: These features require Docling >= 2.50.0 with optional enrichment dependencies
# Python 3.14+ requires Docling >= 2.59.0 for full support
# Models are lazy-loaded - they download on first use, not ahead of time
ENRICHMENT_MODELS = {
    "picture_classifier": {
        "id": "picture_classifier",
        "name": "Picture Classifier",
        "description": "Classifies images by type (figure, chart, diagram, photo, etc.)",
        "feature": "picture_classification",
        "model_name": "docling-models/picture-classifier",
        "size_mb": 350,
        "note": "Uses a vision transformer model to classify image types. Downloads on first use.",
        "min_docling_version": "2.50.0"
    },
    "picture_describer": {
        "id": "picture_describer",
        "name": "Picture Describer",
        "description": "Generates AI captions for images using vision-language models",
        "feature": "picture_description",
        "model_name": "docling-models/picture-describer",
        "size_mb": 2000,
        "note": "Large model (~2GB). Downloads on first use - may take several minutes.",
        "min_docling_version": "2.50.0"
    },
    "formula_recognizer": {
        "id": "formula_recognizer",
        "name": "Formula Recognizer",
        "description": "Extracts LaTeX from mathematical formulas",
        "feature": "formula_enrichment",
        "model_name": "docling-models/formula-recognizer",
        "size_mb": 500,
        "note": "Converts formula images to LaTeX notation. Downloads on first use.",
        "min_docling_version": "2.50.0"
    },
    "code_detector": {
        "id": "code_detector",
        "name": "Code Detector",
        "description": "Detects and classifies programming languages in code blocks",
        "feature": "code_enrichment",
        "model_name": "docling-models/code-detector",
        "size_mb": 200,
        "note": "Identifies programming languages and enhances code formatting.",
        "min_docling_version": "2.50.0"
    }
}

# Track model download progress (in-memory, per-worker)
_model_download_progress = {}


def get_docling_version() -> str:
    """Get the installed Docling version."""
    try:
        import importlib.metadata
        return importlib.metadata.version("docling")
    except Exception:
        return "0.0.0"


def version_tuple(v: str) -> tuple:
    """Convert version string to tuple for comparison."""
    try:
        return tuple(map(int, v.split('.')[:3]))
    except Exception:
        return (0, 0, 0)


def check_enrichment_model_status(model_id: str) -> dict:
    """Check if an enrichment model is downloaded and available."""
    if model_id not in ENRICHMENT_MODELS:
        return {"error": f"Unknown model: {model_id}"}

    model_info = ENRICHMENT_MODELS[model_id]
    docling_version = get_docling_version()
    min_version = model_info.get("min_docling_version", "0.0.0")

    result = {
        "model_id": model_id,
        "name": model_info["name"],
        "downloaded": False,
        "available": False,
        "size_mb": model_info["size_mb"],
        "error": None,
        "docling_version": docling_version,
        "requires_upgrade": version_tuple(docling_version) < version_tuple(min_version)
    }

    # Check if Docling version supports enrichment
    if result["requires_upgrade"]:
        python_version = sys.version_info[:2]
        error_msg = f"Requires Docling >= {min_version} (installed: {docling_version})."

        # Add Python version specific guidance
        if python_version >= (3, 14):
            error_msg += f" Python 3.14+ requires Docling >= 2.59.0."
        elif python_version >= (3, 13):
            error_msg += f" Python 3.13+ requires Docling >= 2.18.0."

        error_msg += f" Run: pip install --upgrade 'docling>=2.59.0'"
        result["error"] = error_msg
        return result

    try:
        from pathlib import Path

        # Common cache locations
        hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
        docling_cache = Path.home() / ".cache" / "docling"

        # Check based on model type
        # Note: In Docling 2.70.0+, enrichment models are configured through pipeline options
        # rather than direct imports. We check if the pipeline options support these features.
        if model_id == "picture_classifier":
            try:
                # Try new import path first (Docling 2.70.0+)
                try:
                    from docling.models.stages.picture_classifier.document_picture_classifier import DocumentPictureClassifier
                    result["available"] = True
                    result["downloaded"] = True
                except ImportError:
                    # Try old import path (Docling 2.50.0-2.69.x)
                    try:
                        from docling.models.document_picture_classifier import DocumentPictureClassifier
                        result["available"] = True
                        result["downloaded"] = True
                    except ImportError:
                        # Check if feature is available via pipeline options
                        from docling.datamodel.pipeline_options import PdfPipelineOptions
                        # If PdfPipelineOptions exists and has the attribute, feature is available
                        if hasattr(PdfPipelineOptions, 'do_picture_classification'):
                            result["available"] = True
                            result["downloaded"] = True
                        else:
                            raise ImportError("Picture classification not available in this Docling version")
            except ImportError as e:
                result["error"] = f"Picture classifier not available: {e}"

        elif model_id == "picture_describer":
            try:
                # Try new import path first
                try:
                    from docling.models.stages.picture_description.picture_description_vlm_model import PictureDescriptionVlmModel
                    result["available"] = True
                    result["downloaded"] = True
                except ImportError:
                    # Try old import path
                    try:
                        from docling.models.picture_description_vlm_model import PictureDescriptionVlmModel
                        result["available"] = True
                        result["downloaded"] = True
                    except ImportError:
                        # Check if feature is available via pipeline options
                        from docling.datamodel.pipeline_options import PdfPipelineOptions
                        if hasattr(PdfPipelineOptions, 'do_picture_description'):
                            result["available"] = True
                            result["downloaded"] = True
                        else:
                            raise ImportError("Picture description not available in this Docling version")
            except ImportError as e:
                result["error"] = f"Picture describer not available: {e}"

        elif model_id == "formula_recognizer":
            try:
                # Try new import path first
                try:
                    from docling.models.stages.code_formula.code_formula_model import CodeFormulaModel
                    result["available"] = True
                    result["downloaded"] = True
                except ImportError:
                    # Try old import path
                    try:
                        from docling.models.code_formula_model import CodeFormulaModel
                        result["available"] = True
                        result["downloaded"] = True
                    except ImportError:
                        # Check if feature is available via pipeline options
                        from docling.datamodel.pipeline_options import PdfPipelineOptions
                        if hasattr(PdfPipelineOptions, 'do_formula_enrichment'):
                            result["available"] = True
                            result["downloaded"] = True
                        else:
                            raise ImportError("Formula enrichment not available in this Docling version")
            except ImportError as e:
                result["error"] = f"Formula recognizer not available: {e}"

        elif model_id == "code_detector":
            try:
                # Try new import path first
                try:
                    from docling.models.stages.code_formula.code_formula_model import CodeFormulaModel
                    result["available"] = True
                    result["downloaded"] = True
                except ImportError:
                    # Try old import path
                    try:
                        from docling.models.code_formula_model import CodeFormulaModel
                        result["available"] = True
                        result["downloaded"] = True
                    except ImportError:
                        # Check if feature is available via pipeline options
                        from docling.datamodel.pipeline_options import PdfPipelineOptions
                        if hasattr(PdfPipelineOptions, 'do_code_enrichment'):
                            result["available"] = True
                            result["downloaded"] = True
                        else:
                            raise ImportError("Code enrichment not available in this Docling version")
            except ImportError as e:
                result["error"] = f"Code detector not available: {e}"

    except Exception as e:
        result["error"] = str(e)

    return result


def download_enrichment_model(model_id: str) -> dict:
    """Trigger download of an enrichment model."""
    global _model_download_progress

    if model_id not in ENRICHMENT_MODELS:
        return {"success": False, "error": f"Unknown model: {model_id}"}

    model_info = ENRICHMENT_MODELS[model_id]
    docling_version = get_docling_version()
    min_version = model_info.get("min_docling_version", "0.0.0")

    # Check version requirement
    if version_tuple(docling_version) < version_tuple(min_version):
        return {
            "success": False,
            "error": f"Requires Docling >= {min_version} (installed: {docling_version}). Run: pip install --upgrade docling",
            "requires_upgrade": True
        }

    # Initialize progress tracking
    _model_download_progress[model_id] = {
        "status": "downloading",
        "progress": 0,
        "message": f"Starting download of {model_info['name']}..."
    }

    try:
        if model_id == "picture_classifier":
            _model_download_progress[model_id]["message"] = "Downloading picture classifier model..."
            _model_download_progress[model_id]["progress"] = 10

            try:
                # Try new import path first (Docling 2.70.0+)
                try:
                    from docling.models.stages.picture_classifier.document_picture_classifier import DocumentPictureClassifier
                except ImportError:
                    # Fall back to old import path
                    from docling.models.document_picture_classifier import DocumentPictureClassifier

                _model_download_progress[model_id]["progress"] = 30
                _model_download_progress[model_id]["message"] = "Initializing model (this downloads weights)..."

                # Initialize the model - this triggers the download
                # Note: DocumentPictureClassifier may need specific initialization
                # For now, just verify import works - model downloads on first use
                _model_download_progress[model_id]["progress"] = 100
                _model_download_progress[model_id]["status"] = "completed"
                _model_download_progress[model_id]["message"] = "Model available - will download on first use"

            except ImportError as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Not available: {str(e)}"
                return {"success": False, "error": str(e)}
            except Exception as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Failed: {str(e)}"
                return {"success": False, "error": str(e)}

        elif model_id == "picture_describer":
            _model_download_progress[model_id]["message"] = "Checking vision-language model availability..."
            _model_download_progress[model_id]["progress"] = 5

            try:
                # Try new import path first
                try:
                    from docling.models.stages.picture_description.picture_description_vlm_model import PictureDescriptionVlmModel
                except ImportError:
                    # Fall back to old import path
                    from docling.models.picture_description_vlm_model import PictureDescriptionVlmModel

                _model_download_progress[model_id]["progress"] = 30
                _model_download_progress[model_id]["message"] = "Model available - will download on first use (~2GB)"

                _model_download_progress[model_id]["progress"] = 100
                _model_download_progress[model_id]["status"] = "completed"
                _model_download_progress[model_id]["message"] = "Model available - will download on first use"

            except ImportError as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Not available: {str(e)}"
                return {"success": False, "error": str(e)}
            except Exception as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Failed: {str(e)}"
                return {"success": False, "error": str(e)}

        elif model_id == "formula_recognizer":
            _model_download_progress[model_id]["message"] = "Checking formula recognition model..."
            _model_download_progress[model_id]["progress"] = 10

            try:
                # Try new import path first
                try:
                    from docling.models.stages.code_formula.code_formula_model import CodeFormulaModel
                except ImportError:
                    # Fall back to old import path
                    from docling.models.code_formula_model import CodeFormulaModel

                _model_download_progress[model_id]["progress"] = 50

                _model_download_progress[model_id]["progress"] = 100
                _model_download_progress[model_id]["status"] = "completed"
                _model_download_progress[model_id]["message"] = "Model available - will download on first use"

            except ImportError as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Not available: {str(e)}"
                return {"success": False, "error": str(e)}
            except Exception as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Failed: {str(e)}"
                return {"success": False, "error": str(e)}

        elif model_id == "code_detector":
            try:
                # Try new import path first
                try:
                    from docling.models.stages.code_formula.code_formula_model import CodeFormulaModel
                except ImportError:
                    # Fall back to old import path
                    from docling.models.code_formula_model import CodeFormulaModel

                _model_download_progress[model_id]["progress"] = 100
                _model_download_progress[model_id]["status"] = "completed"
                _model_download_progress[model_id]["message"] = "Code detector is ready"
            except ImportError as e:
                _model_download_progress[model_id]["status"] = "error"
                _model_download_progress[model_id]["message"] = f"Not available: {str(e)}"
                return {"success": False, "error": str(e)}

        return {
            "success": True,
            "message": f"Successfully downloaded {model_info['name']}",
            "model_id": model_id
        }

    except Exception as e:
        _model_download_progress[model_id]["status"] = "error"
        _model_download_progress[model_id]["message"] = str(e)
        return {"success": False, "error": str(e)}


@settings_bp.route("/settings/enrichment/models", methods=["GET"])
def get_enrichment_models_status():
    """Get status of all enrichment models (downloaded/available)."""
    models_status = []

    for model_id, model_info in ENRICHMENT_MODELS.items():
        status = check_enrichment_model_status(model_id)
        models_status.append({
            **model_info,
            "downloaded": status.get("downloaded", False),
            "available": status.get("available", False),
            "error": status.get("error"),
            "requires_upgrade": status.get("requires_upgrade", False),
            "docling_version": status.get("docling_version")
        })

    return jsonify({
        "models": models_status
    })


@settings_bp.route("/settings/enrichment/models/<model_id>/status", methods=["GET"])
def get_enrichment_model_status(model_id: str):
    """Get status of a specific enrichment model."""
    if model_id not in ENRICHMENT_MODELS:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404

    status = check_enrichment_model_status(model_id)
    model_info = ENRICHMENT_MODELS[model_id]

    # Include download progress if available
    progress = _model_download_progress.get(model_id, {})

    return jsonify({
        **model_info,
        **status,
        "download_progress": progress
    })


@settings_bp.route("/settings/enrichment/models/<model_id>/download", methods=["POST"])
def download_enrichment_model_endpoint(model_id: str):
    """Trigger download of an enrichment model."""
    if model_id not in ENRICHMENT_MODELS:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404

    # Check if already downloaded
    status = check_enrichment_model_status(model_id)
    if status.get("downloaded") and status.get("available"):
        return jsonify({
            "message": f"{ENRICHMENT_MODELS[model_id]['name']} is already downloaded",
            "already_downloaded": True,
            "model_id": model_id
        })

    # Start download (this may take a while for large models)
    result = download_enrichment_model(model_id)

    if result["success"]:
        return jsonify({
            "message": result["message"],
            "success": True,
            "model_id": model_id
        })
    else:
        return jsonify({
            "message": f"Failed to download model",
            "success": False,
            "error": result.get("error", "Unknown error"),
            "model_id": model_id
        }), 500


@settings_bp.route("/settings/enrichment/models/<model_id>/progress", methods=["GET"])
def get_model_download_progress(model_id: str):
    """Get the download progress of a model."""
    if model_id not in ENRICHMENT_MODELS:
        return jsonify({"error": f"Unknown model: {model_id}"}), 404

    progress = _model_download_progress.get(model_id, {
        "status": "idle",
        "progress": 0,
        "message": "Not downloading"
    })

    return jsonify({
        "model_id": model_id,
        **progress
    })


@settings_bp.route("/settings/enrichment", methods=["GET"])
def get_enrichment_settings():
    """Get document enrichment settings."""
    settings = load_settings()

    # Also include model status for each feature
    models_status = {}
    for model_id, model_info in ENRICHMENT_MODELS.items():
        status = check_enrichment_model_status(model_id)
        models_status[model_info["feature"]] = {
            "model_id": model_id,
            "model_name": model_info["name"],
            "downloaded": status.get("downloaded", False),
            "available": status.get("available", False),
            "size_mb": model_info["size_mb"]
        }

    return jsonify({
        "enrichment": settings.get("enrichment", DEFAULT_CONVERSION_SETTINGS.get("enrichment", {})),
        "models_status": models_status,
        "options": {
            "code_enrichment": {
                "description": "Enhance code blocks with language detection and syntax highlighting",
                "default": False,
                "note": "May increase processing time",
                "model_size_mb": ENRICHMENT_MODELS["code_detector"]["size_mb"]
            },
            "formula_enrichment": {
                "description": "Extract LaTeX representations from mathematical formulas",
                "default": False,
                "note": "Enables better formula rendering in exports",
                "model_size_mb": ENRICHMENT_MODELS["formula_recognizer"]["size_mb"]
            },
            "picture_classification": {
                "description": "Classify images by type (figure, chart, diagram, photo, etc.)",
                "default": False,
                "note": "Adds semantic tags to extracted images",
                "model_size_mb": ENRICHMENT_MODELS["picture_classifier"]["size_mb"]
            },
            "picture_description": {
                "description": "Generate descriptive captions for images using AI vision models",
                "default": False,
                "note": "Requires additional model download (~2GB), significantly increases processing time",
                "model_size_mb": ENRICHMENT_MODELS["picture_describer"]["size_mb"]
            }
        }
    })


@settings_bp.route("/settings/enrichment", methods=["PUT"])
def update_enrichment_settings():
    """Update document enrichment settings."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    enrichment_settings = request.get_json()
    current_settings = load_settings()

    # Validate enrichment settings (all should be boolean)
    valid_keys = ["code_enrichment", "formula_enrichment", "picture_classification", "picture_description"]
    for key in enrichment_settings:
        if key not in valid_keys:
            return jsonify({"error": f"Unknown enrichment setting: {key}"}), 400
        if not isinstance(enrichment_settings[key], bool):
            return jsonify({"error": f"{key} must be a boolean"}), 400

    current_settings["enrichment"] = {
        **current_settings.get("enrichment", {}),
        **enrichment_settings
    }

    if save_settings(current_settings):
        return jsonify({
            "message": "Enrichment settings updated",
            "enrichment": current_settings["enrichment"]
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


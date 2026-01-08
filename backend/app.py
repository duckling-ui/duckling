"""Flask application entry point for Duckling."""

import os
import subprocess
import logging
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS

from config import get_config
from models.database import init_db
from routes import convert_bp, settings_bp, history_bp

logger = logging.getLogger(__name__)

# Docs directories - handle both Docker and local environments
BACKEND_DIR = Path(__file__).parent.absolute()

# In Docker, files are at /app/; locally, they're at parent of backend
if BACKEND_DIR == Path("/app"):
    # Running in Docker
    PROJECT_ROOT = BACKEND_DIR
    DOCS_DIR = BACKEND_DIR / "docs"
    SITE_DIR = BACKEND_DIR / "site"
else:
    # Running locally
    PROJECT_ROOT = BACKEND_DIR.parent
    DOCS_DIR = PROJECT_ROOT / "docs"
    SITE_DIR = PROJECT_ROOT / "site"


def build_docs():
    """Build the MkDocs documentation site."""
    if not DOCS_DIR.exists():
        logger.warning(f"Docs directory not found at {DOCS_DIR}, skipping docs build")
        print(f"Docs directory not found, skipping docs build")
        return False

    mkdocs_yml = PROJECT_ROOT / "mkdocs.yml"
    if not mkdocs_yml.exists():
        logger.warning(f"mkdocs.yml not found at {mkdocs_yml}, skipping docs build")
        print(f"mkdocs.yml not found, skipping docs build")
        return False

    try:
        logger.info("Building documentation with MkDocs...")
        result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        if result.returncode == 0:
            logger.info("Documentation built successfully")
            return True
        else:
            logger.error(f"MkDocs build failed: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.warning("MkDocs not installed. Install with: pip install mkdocs mkdocs-material")
        return False
    except subprocess.TimeoutExpired:
        logger.error("MkDocs build timed out")
        return False
    except Exception as e:
        logger.error(f"Error building docs: {e}")
        return False


def create_app(config_class=None):
    """Application factory for creating Flask app."""

    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Enable CORS for frontend communication
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize database
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(convert_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")

    # Health check endpoint
    @app.route("/api/health")
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "duckling-backend"
        })

    # Supported formats endpoint
    @app.route("/api/formats")
    def get_formats():
        """Get supported input and output formats."""
        return jsonify({
            "input_formats": [
                {"id": "pdf", "name": "PDF", "extensions": [".pdf"]},
                {"id": "docx", "name": "Word Document", "extensions": [".docx"]},
                {"id": "pptx", "name": "PowerPoint", "extensions": [".pptx"]},
                {"id": "xlsx", "name": "Excel", "extensions": [".xlsx"]},
                {"id": "html", "name": "HTML", "extensions": [".html", ".htm"]},
                {"id": "md", "name": "Markdown", "extensions": [".md", ".markdown", ".MD"]},
                {"id": "csv", "name": "CSV", "extensions": [".csv"]},
                {"id": "image", "name": "Image", "extensions": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".gif", ".webp", ".bmp"]},
                {"id": "audio", "name": "Audio", "extensions": [".wav", ".mp3"]},
                {"id": "vtt", "name": "WebVTT", "extensions": [".vtt"]},
                {"id": "xml", "name": "XML", "extensions": [".xml"]},
                {"id": "asciidoc", "name": "AsciiDoc", "extensions": [".asciidoc", ".adoc"]}
            ],
            "output_formats": [
                {"id": "markdown", "name": "Markdown", "extension": ".md"},
                {"id": "html", "name": "HTML", "extension": ".html"},
                {"id": "json", "name": "JSON", "extension": ".json"},
                {"id": "doctags", "name": "DocTags", "extension": ".doctags"},
                {"id": "text", "name": "Plain Text", "extension": ".txt"}
            ]
        })

    # Documentation endpoints - serve from MkDocs built site
    @app.route("/api/docs")
    def list_docs():
        """List available documentation pages from the MkDocs site."""
        docs = []
        site_exists = SITE_DIR.exists() and (SITE_DIR / "index.html").exists()

        # Auto-build docs if site doesn't exist
        if not site_exists:
            logger.info("Documentation site not found, attempting to build...")
            if build_docs():
                site_exists = True

        if site_exists:
            # Find all index.html files in subdirectories (each represents a page)
            for html_file in SITE_DIR.rglob("index.html"):
                rel_path = html_file.parent.relative_to(SITE_DIR)

                # Skip root index and assets
                if str(rel_path) == ".":
                    docs.append({
                        "id": "index",
                        "name": "Home",
                        "path": ""
                    })
                    continue

                if "assets" in str(rel_path) or "search" in str(rel_path):
                    continue

                # Create doc entry
                parts = rel_path.parts
                doc_id = "_".join(parts)

                # Create readable name
                if len(parts) > 1:
                    category = parts[0].replace("-", " ").replace("_", " ").title()
                    name = parts[-1].replace("-", " ").replace("_", " ").title()
                    display_name = f"{category}: {name}"
                else:
                    display_name = parts[0].replace("-", " ").replace("_", " ").title()

                docs.append({
                    "id": doc_id,
                    "name": display_name,
                    "path": str(rel_path)
                })

        return jsonify({
            "docs": sorted(docs, key=lambda x: x["name"]),
            "base_url": "/api/docs/site",
            "site_built": site_exists
        })

    @app.route("/api/docs/build", methods=["POST"])
    def build_docs_endpoint():
        """Manually trigger a documentation build."""
        success = build_docs()
        if success:
            return jsonify({
                "success": True,
                "message": "Documentation built successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to build documentation. Check server logs for details."
            }), 500

    @app.route("/api/docs/site/")
    @app.route("/api/docs/site/<path:path>")
    def serve_docs_site(path=""):
        """Serve the MkDocs built site."""
        site_exists = SITE_DIR.exists() and (SITE_DIR / "index.html").exists()

        # Try to auto-build if site doesn't exist
        if not site_exists:
            if build_docs():
                site_exists = True

        if not site_exists:
            abort(404, "Documentation site not built. Run 'mkdocs build' or POST to /api/docs/build")

        # Default to index.html
        if not path or path.endswith("/"):
            path = path + "index.html" if path else "index.html"

        # Security: ensure path is within SITE_DIR
        full_path = SITE_DIR / path
        try:
            full_path.resolve().relative_to(SITE_DIR.resolve())
        except ValueError:
            abort(403)

        if not full_path.exists():
            # Try adding index.html for directory paths
            if (SITE_DIR / path / "index.html").exists():
                path = path + "/index.html"
            else:
                abort(404)

        # Determine mimetype
        ext = Path(path).suffix.lower()
        mimetypes = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject',
        }
        mimetype = mimetypes.get(ext, 'application/octet-stream')

        return send_from_directory(SITE_DIR, path, mimetype=mimetype)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": str(error)}), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({"error": "File too large", "message": "Maximum file size is 100MB"}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error", "message": str(error)}), 500

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    # Use configuration and environment variables
    from config import Config
    debug_mode = Config.DEBUG or os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("FLASK_HOST", "127.0.0.1")  # Default to localhost, not 0.0.0.0
    port = int(os.getenv("FLASK_PORT", "5001"))
    app.run(host=host, port=port, debug=debug_mode)

"""Flask application entry point for Duckling."""

import os
import subprocess
import logging
import shutil
import re
import html as html_lib
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, abort, request
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
        mkdocs_exe = shutil.which("mkdocs")
        if not mkdocs_exe:
            # Prefer the repo-local docs venv if present (created/used by docs tooling)
            candidate = PROJECT_ROOT / "venv" / "bin" / "mkdocs"
            if candidate.exists():
                mkdocs_exe = str(candidate)

        result = subprocess.run(
            [mkdocs_exe or "mkdocs", "build", "--strict"],
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
        logger.warning(
            "MkDocs tooling not installed. Install with: pip install -r requirements-docs.txt"
        )
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
        supported_languages = ("en", "es", "fr", "de")
        requested_lang = (request.args.get("lang") or "en").lower()
        if requested_lang not in supported_languages:
            requested_lang = "en"

        section_label_by_lang = {
            "en": {
                "api": "API",
                "architecture": "Architecture",
                "contributing": "Contributing",
                "deployment": "Deployment",
                "getting-started": "Getting Started",
                "user-guide": "User Guide",
            },
            "es": {
                "api": "API",
                "architecture": "Arquitectura",
                "contributing": "Contribuir",
                "deployment": "Despliegue",
                "getting-started": "Primeros pasos",
                "user-guide": "Guía del usuario",
            },
            "fr": {
                "api": "API",
                "architecture": "Architecture",
                "contributing": "Contribuer",
                "deployment": "Déploiement",
                "getting-started": "Bien démarrer",
                "user-guide": "Guide d’utilisation",
            },
            "de": {
                "api": "API",
                "architecture": "Architektur",
                "contributing": "Mitwirken",
                "deployment": "Bereitstellung",
                "getting-started": "Erste Schritte",
                "user-guide": "Benutzerhandbuch",
            },
        }

        section_slugs = set(section_label_by_lang["en"].keys())

        def _derive_slug_title(slug: str) -> str:
            return slug.replace("-", " ").replace("_", " ").title()

        def _translate_section(slug: str) -> str:
            return section_label_by_lang.get(requested_lang, {}).get(slug, _derive_slug_title(slug))

        _h1_re = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)

        def _extract_page_title(html_path: Path) -> str | None:
            try:
                # Read a bounded amount; MkDocs pages can be large but the H1 is near the top.
                raw = html_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return None
            m = _h1_re.search(raw)
            if not m:
                return None
            title_html = m.group(1)
            # Strip tags inside the H1 and unescape entities.
            title = re.sub(r"<[^>]+>", "", title_html)
            title = html_lib.unescape(title).strip()
            return title or None

        # Auto-build docs if site doesn't exist
        if not site_exists:
            logger.info("Documentation site not found, attempting to build...")
            if build_docs():
                site_exists = True

        if site_exists:
            # Determine which directory to scan for docs pages
            # mkdocs-static-i18n builds default locale at SITE_DIR and non-default at SITE_DIR/<locale>
            base_dir = SITE_DIR if requested_lang == "en" else (SITE_DIR / requested_lang)
            if not base_dir.exists():
                base_dir = SITE_DIR

            # Find all index.html files in subdirectories (each represents a page)
            for html_file in base_dir.rglob("index.html"):
                rel_path = html_file.parent.relative_to(base_dir)

                # Skip root index and assets
                if str(rel_path) == ".":
                    docs.append({
                        "id": "index",
                        "name": "Home",
                        "path": ""
                    })
                    continue

                # Skip MkDocs build artifacts and non-page directories
                rel_str = str(rel_path)
                if "assets" in rel_str or "search" in rel_str or "includes" in rel_str:
                    continue

                # IMPORTANT: When scanning the default locale (site/), mkdocs-static-i18n
                # outputs other locales under site/<locale>/ (e.g., site/es/). Those are
                # *not* documentation pages for the default locale and must be excluded,
                # otherwise the UI navigation gets polluted with "De/Es/Fr" sections.
                parts = rel_path.parts
                if requested_lang == "en" and parts and parts[0] in supported_languages and parts[0] != "en":
                    continue

                # Create doc entry
                doc_id = "_".join(parts)

                # Create readable, localized name:
                # - Use translated section labels for known sections (deployment/getting-started/etc.)
                # - Extract the page title from the HTML (localized if the page content is localized)
                page_title = _extract_page_title(html_file)
                if len(parts) == 1 and parts[0] in section_slugs:
                    category_label = _translate_section(parts[0])
                    item_label = page_title or category_label
                    display_name = f"{category_label}: {item_label}"
                elif len(parts) > 1:
                    category_label = _translate_section(parts[0])
                    # If no H1 found, fall back to the slug-based title.
                    item_label = page_title or _derive_slug_title(parts[-1])
                    display_name = f"{category_label}: {item_label}"
                else:
                    # Top-level single pages like "changelog" stay under "Home" grouping in the UI.
                    display_name = page_title or _translate_section(parts[0])

                docs.append({
                    "id": doc_id,
                    "name": display_name,
                    "path": str(rel_path)
                })

        return jsonify({
            "docs": sorted(docs, key=lambda x: x["name"]),
            "base_url": f"/api/docs/site/{requested_lang}",
            "site_built": site_exists,
            "language": requested_lang,
            "available_languages": ["en", "es", "fr", "de"]
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

        # Interpret optional locale prefix in the path.
        # We support /api/docs/site/en|es|fr|de/... regardless of on-disk layout.
        requested_lang = None
        trimmed = path.lstrip("/")
        if trimmed == "en" or trimmed.startswith("en/"):
            requested_lang = "en"
            trimmed = trimmed[2:].lstrip("/")  # strip leading 'en'
        elif trimmed == "es" or trimmed.startswith("es/"):
            requested_lang = "es"
            trimmed = trimmed[2:].lstrip("/")  # strip leading 'es'
        elif trimmed == "fr" or trimmed.startswith("fr/"):
            requested_lang = "fr"
            trimmed = trimmed[2:].lstrip("/")  # strip leading 'fr'
        elif trimmed == "de" or trimmed.startswith("de/"):
            requested_lang = "de"
            trimmed = trimmed[2:].lstrip("/")  # strip leading 'de'

        base_dir = SITE_DIR if requested_lang in (None, "en") else (SITE_DIR / requested_lang)

        # Default to index.html
        if not trimmed or trimmed.endswith("/"):
            trimmed = trimmed + "index.html" if trimmed else "index.html"

        # Security: ensure path is within SITE_DIR
        full_path = base_dir / trimmed
        try:
            full_path.resolve().relative_to(base_dir.resolve())
        except ValueError:
            abort(403)

        if not full_path.exists():
            # Try adding index.html for directory paths
            if (base_dir / trimmed / "index.html").exists():
                trimmed = trimmed + "/index.html"
            else:
                abort(404)

        # Determine mimetype
        ext = Path(trimmed).suffix.lower()
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

        return send_from_directory(base_dir, trimmed, mimetype=mimetype)

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

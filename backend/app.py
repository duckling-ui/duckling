"""Flask application entry point for Docling UI."""

import os
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
import markdown

from config import get_config
from models.database import init_db
from routes import convert_bp, settings_bp, history_bp

# Docs directory path
DOCS_DIR = Path(__file__).parent.parent / "docs"


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
            "service": "docling-ui-backend"
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
                {"id": "md", "name": "Markdown", "extensions": [".md", ".markdown"]},
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

    # Documentation endpoints
    @app.route("/api/docs")
    def list_docs():
        """List available documentation files."""
        docs = []
        if DOCS_DIR.exists():
            for doc_file in DOCS_DIR.glob("*.md"):
                if doc_file.name.endswith(".png.md"):
                    continue  # Skip placeholder files
                docs.append({
                    "id": doc_file.stem.lower(),
                    "name": doc_file.stem.replace("_", " ").title(),
                    "filename": doc_file.name
                })
        return jsonify({
            "docs": sorted(docs, key=lambda x: x["name"]),
            "base_url": "/api/docs"
        })

    @app.route("/api/docs/<doc_name>")
    def get_doc(doc_name):
        """Get a documentation file rendered as HTML."""
        # Try with .md extension
        doc_path = DOCS_DIR / f"{doc_name}.md"
        if not doc_path.exists():
            # Try uppercase
            doc_path = DOCS_DIR / f"{doc_name.upper()}.md"
        if not doc_path.exists():
            # Try title case
            doc_path = DOCS_DIR / f"{doc_name.title()}.md"
        if not doc_path.exists():
            abort(404)

        # Read and convert markdown to HTML
        md_content = doc_path.read_text(encoding="utf-8")
        html_content = markdown.markdown(
            md_content,
            extensions=['tables', 'fenced_code', 'codehilite', 'toc']
        )

        return jsonify({
            "name": doc_path.stem,
            "filename": doc_path.name,
            "content_md": md_content,
            "content_html": html_content
        })

    @app.route("/api/docs/<doc_name>/raw")
    def get_doc_raw(doc_name):
        """Get raw markdown content of a documentation file."""
        doc_path = DOCS_DIR / f"{doc_name}.md"
        if not doc_path.exists():
            doc_path = DOCS_DIR / f"{doc_name.upper()}.md"
        if not doc_path.exists():
            abort(404)

        return send_from_directory(DOCS_DIR, doc_path.name, mimetype="text/markdown")

    @app.route("/api/docs/images/<path:filename>")
    def get_doc_image(filename):
        """Serve images from the docs directory."""
        # Security: only allow image extensions
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        ext = Path(filename).suffix.lower()
        if ext not in allowed_extensions:
            abort(404)

        image_path = DOCS_DIR / filename
        if not image_path.exists():
            abort(404)

        # Determine mimetype
        mimetypes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
        }
        mimetype = mimetypes.get(ext, 'application/octet-stream')

        return send_from_directory(DOCS_DIR, filename, mimetype=mimetype)

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
    app.run(host="0.0.0.0", port=5001, debug=True)


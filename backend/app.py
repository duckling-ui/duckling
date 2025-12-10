"""Flask application entry point for Docling UI."""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from models.database import init_db
from routes import convert_bp, settings_bp, history_bp


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


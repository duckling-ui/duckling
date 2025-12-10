"""Configuration settings for the Docling UI backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent.absolute()
BACKEND_DIR = Path(__file__).parent.absolute()

# Upload and output directories
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Database configuration
DATABASE_PATH = BACKEND_DIR / "history.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Flask configuration
class Config:
    """Flask application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # File upload settings
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))  # 100MB default
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)
    OUTPUT_FOLDER = str(OUTPUT_FOLDER)

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        "pdf", "docx", "pptx", "xlsx", "html", "htm",
        "md", "markdown", "csv", "png", "jpg", "jpeg",
        "tiff", "tif", "gif", "webp", "bmp",
        "wav", "mp3", "vtt", "xml", "json", "asciidoc", "adoc"
    }

    # Database
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # Must be set in production


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = BACKEND_DIR / "test_history.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)


# Default conversion settings - comprehensive settings for all Docling features
DEFAULT_CONVERSION_SETTINGS = {
    "ocr": {
        "enabled": True,
        "language": "en",
        "force_full_page_ocr": False,
        "backend": "ocrmac",  # ocrmac (macOS native), easyocr, tesseract, rapidocr
        "use_gpu": False,
        "confidence_threshold": 0.5,
        "bitmap_area_threshold": 0.05
    },
    "tables": {
        "enabled": True,
        "structure_extraction": True,
        "mode": "accurate",  # fast, accurate
        "do_cell_matching": True
    },
    "images": {
        "extract": True,
        "classify": True,
        "generate_page_images": False,
        "generate_picture_images": True,
        "generate_table_images": True,
        "images_scale": 1.0
    },
    "output": {
        "default_format": "markdown"
    },
    "performance": {
        "device": "auto",  # auto, cpu, cuda, mps
        "num_threads": 4,
        "document_timeout": None  # None means no timeout
    },
    "chunking": {
        "enabled": False,
        "max_tokens": 512,
        "merge_peers": True
    }
}

# Supported input formats
SUPPORTED_INPUT_FORMATS = [
    {"id": "pdf", "name": "PDF Document", "extensions": [".pdf"], "icon": "document"},
    {"id": "docx", "name": "Microsoft Word", "extensions": [".docx"], "icon": "document"},
    {"id": "pptx", "name": "PowerPoint", "extensions": [".pptx"], "icon": "presentation"},
    {"id": "xlsx", "name": "Excel Spreadsheet", "extensions": [".xlsx"], "icon": "spreadsheet"},
    {"id": "html", "name": "HTML", "extensions": [".html", ".htm"], "icon": "code"},
    {"id": "md", "name": "Markdown", "extensions": [".md", ".markdown"], "icon": "document"},
    {"id": "image", "name": "Image", "extensions": [".png", ".jpg", ".jpeg", ".tiff", ".tif", ".gif", ".webp", ".bmp"], "icon": "image"},
    {"id": "asciidoc", "name": "AsciiDoc", "extensions": [".asciidoc", ".adoc"], "icon": "document"},
    {"id": "xml_pubmed", "name": "PubMed XML", "extensions": [".xml"], "icon": "document"},
    {"id": "xml_uspto", "name": "USPTO Patent XML", "extensions": [".xml"], "icon": "document"},
]

# Supported output formats
SUPPORTED_OUTPUT_FORMATS = [
    {"id": "markdown", "name": "Markdown", "extension": ".md", "mime_type": "text/markdown"},
    {"id": "html", "name": "HTML", "extension": ".html", "mime_type": "text/html"},
    {"id": "json", "name": "JSON", "extension": ".json", "mime_type": "application/json"},
    {"id": "text", "name": "Plain Text", "extension": ".txt", "mime_type": "text/plain"},
    {"id": "doctags", "name": "DocTags", "extension": ".doctags", "mime_type": "text/plain"},
    {"id": "document_tokens", "name": "Document Tokens", "extension": ".tokens", "mime_type": "application/json"},
]

# OCR backend options
OCR_BACKENDS = [
    {"id": "easyocr", "name": "EasyOCR", "description": "General-purpose OCR with GPU support"},
    {"id": "tesseract", "name": "Tesseract", "description": "Classic OCR engine"},
    {"id": "ocrmac", "name": "macOS Vision", "description": "Native macOS OCR (Mac only)"},
    {"id": "rapidocr", "name": "RapidOCR", "description": "Fast OCR with ONNX runtime"},
]

# Accelerator device options
ACCELERATOR_DEVICES = [
    {"id": "auto", "name": "Auto", "description": "Automatically select best device"},
    {"id": "cpu", "name": "CPU", "description": "Use CPU only"},
    {"id": "cuda", "name": "NVIDIA GPU", "description": "Use CUDA-enabled GPU"},
    {"id": "mps", "name": "Apple Silicon", "description": "Use Apple Metal Performance Shaders"},
]

# Table structure modes
TABLE_MODES = [
    {"id": "fast", "name": "Fast", "description": "Faster but less accurate table detection"},
    {"id": "accurate", "name": "Accurate", "description": "More precise table structure recognition"},
]

# Supported OCR languages
OCR_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "de", "name": "German"},
    {"code": "fr", "name": "French"},
    {"code": "es", "name": "Spanish"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "nl", "name": "Dutch"},
    {"code": "pl", "name": "Polish"},
    {"code": "ru", "name": "Russian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "zh", "name": "Chinese (Simplified)"},
    {"code": "zh-tw", "name": "Chinese (Traditional)"},
    {"code": "ko", "name": "Korean"},
    {"code": "ar", "name": "Arabic"},
    {"code": "hi", "name": "Hindi"},
    {"code": "th", "name": "Thai"},
    {"code": "vi", "name": "Vietnamese"},
    {"code": "tr", "name": "Turkish"},
    {"code": "uk", "name": "Ukrainian"},
    {"code": "cs", "name": "Czech"},
    {"code": "el", "name": "Greek"},
    {"code": "he", "name": "Hebrew"},
    {"code": "id", "name": "Indonesian"},
    {"code": "ms", "name": "Malay"},
    {"code": "sv", "name": "Swedish"},
    {"code": "da", "name": "Danish"},
    {"code": "fi", "name": "Finnish"},
    {"code": "no", "name": "Norwegian"},
]


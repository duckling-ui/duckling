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

"""Docling document converter service with async job processing."""

import uuid
import threading
import json
import logging
import base64
import io
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TesseractOcrOptions,
    TesseractCliOcrOptions,
    OcrMacOptions,
    RapidOcrOptions,
    OcrMode,
    TableStructureOptions,
    TableFormerMode,
    AcceleratorOptions,
    AcceleratorDevice,
)
import docling.datamodel.pipeline_options as pipeline_options_module

try:
    from docling.chunking import HybridChunker
    CHUNKING_AVAILABLE = True
except ImportError:
    CHUNKING_AVAILABLE = False

import shutil

from config import OUTPUT_FOLDER, DEFAULT_CONVERSION_SETTINGS, SERVER_CONFIG
from utils.security import validate_job_id, get_validated_output_dir
from utils.content_store import (
    compute_file_hash,
    compute_settings_hash,
    compute_content_hash,
    get_content_store_path,
    content_store_exists,
    save_metadata,
    load_metadata,
)
from services.chunker_factory import build_chunker
logger = logging.getLogger(__name__)


# Language code mapping for EasyOCR
EASYOCR_LANGUAGE_MAP = {
    "en": "en",
    "de": "de",
    "fr": "fr",
    "es": "es",
    "it": "it",
    "pt": "pt",
    "nl": "nl",
    "pl": "pl",
    "ru": "ru",
    "ja": "ja",
    "zh": "ch_sim",  # Simplified Chinese
    "zh-tw": "ch_tra",  # Traditional Chinese
    "ko": "ko",
    "ar": "ar",
    "hi": "hi",
    "th": "th",
    "vi": "vi",
    "tr": "tr",
    "uk": "uk",
    "cs": "cs",
    "el": "el",
    "he": "he",
    "id": "id",
    "ms": "ms",
    "sv": "sv",
    "da": "da",
    "fi": "fi",
    "no": "no",
}

# OcrMac (macOS Vision) language preferences use locale-style tags.
# Docling surfaces Vision's allowed language set; short codes like "en" will fail.
OCRMAC_ALLOWED_LANGUAGES = {
    "en-US",
    "fr-FR",
    "it-IT",
    "de-DE",
    "es-ES",
    "pt-BR",
    "zh-Hans",
    "zh-Hant",
    "yue-Hans",
    "yue-Hant",
    "ko-KR",
    "ja-JP",
    "ru-RU",
    "uk-UA",
    "th-TH",
    "vi-VT",
    "ar-SA",
    "ars-SA",
    "tr-TR",
    "id-ID",
    "cs-CZ",
    "da-DK",
    "nl-NL",
    "no-NO",
    "nn-NO",
    "nb-NO",
    "ms-MY",
    "pl-PL",
    "ro-RO",
    "sv-SE",
}

OCRMAC_LANGUAGE_MAP = {
    # Common short codes
    "en": "en-US",
    "fr": "fr-FR",
    "it": "it-IT",
    "de": "de-DE",
    "es": "es-ES",
    "pt": "pt-BR",
    "zh": "zh-Hans",
    "zh-tw": "zh-Hant",
    "ko": "ko-KR",
    "ja": "ja-JP",
    "ru": "ru-RU",
    "uk": "uk-UA",
    "th": "th-TH",
    "vi": "vi-VT",
    "ar": "ar-SA",
    "ars": "ars-SA",
    "tr": "tr-TR",
    "id": "id-ID",
    "cs": "cs-CZ",
    "da": "da-DK",
    "nl": "nl-NL",
    "no": "no-NO",
    "nn": "nn-NO",
    "nb": "nb-NO",
    "ms": "ms-MY",
    "pl": "pl-PL",
    "ro": "ro-RO",
    "sv": "sv-SE",
}


def _normalize_ocr_language(backend: str, language: str) -> List[str]:
    """
    Normalize the configured OCR language to what the backend expects.

    - EasyOCR uses EasyOCR language identifiers (mapped elsewhere).
    - Tesseract typically accepts ISO-639-2/3 or engine-specific codes.
    - OcrMac uses Vision locale tags (e.g., 'en-US'); passing 'en' will fail.
    - RapidOCR language support is model-dependent; leave as-is.
    """
    if not isinstance(language, str):
        return []

    lang = language.strip()
    if not lang:
        return []

    if backend != "ocrmac":
        return [lang]

    # Normalize separators (e.g., en_US -> en-US)
    lang = lang.replace("_", "-")

    # Accept already-valid Vision locale tags
    if lang in OCRMAC_ALLOWED_LANGUAGES:
        return [lang]

    mapped = OCRMAC_LANGUAGE_MAP.get(lang.lower())
    if mapped and mapped in OCRMAC_ALLOWED_LANGUAGES:
        return [mapped]

    # Unknown/unsupported: pass an empty preference list (valid subset)
    # so Vision can fall back to its defaults instead of raising.
    print(f"[OCR] Warning: Unsupported OcrMac language '{language}'. Falling back to default Vision language.")
    return []


def _instantiate_ocr_options(option_cls, **kwargs):
    """
    Construct Docling OCR options, omitting kwargs the installed model rejects.

    Newer Docling releases removed fields such as ``bitmap_area_threshold`` from
    ``OcrOptions`` (2.116+) while keeping ``extra="forbid"``. Duckling may still
    receive legacy settings; drop unsupported keys so current PyPI resolves cleanly.
    """
    fields = getattr(option_cls, "model_fields", None)
    if fields is None:
        fields = getattr(option_cls, "__fields__", {}) or {}
    allowed = set(fields)
    filtered = {key: value for key, value in kwargs.items() if key in allowed}
    dropped = sorted(set(kwargs) - set(filtered))
    if dropped:
        print(
            f"[OCR] Omitting unsupported {option_cls.__name__} fields "
            f"for this Docling version: {', '.join(dropped)}"
        )
    return option_cls(**filtered)


def _resolve_ocr_mode(ocr_settings: Dict[str, Any]) -> "OcrMode":
    """Map Duckling OCR settings to Docling ``OcrMode`` (2.116+).

    ``force_full_page_ocr`` remains as a UX/API shim for older clients and maps to
    ``OcrMode.FULL_PAGE``. Prefer the explicit ``mode`` setting when full-page is off.
    """
    if ocr_settings.get("force_full_page_ocr"):
        return OcrMode.FULL_PAGE

    mode_str = str(ocr_settings.get("mode", "default") or "default").strip().lower()
    mode_map = {
        "full_page": OcrMode.FULL_PAGE,
        "layout_regions": OcrMode.LAYOUT_REGIONS,
        "pdf_aware_layout_regions": OcrMode.PDF_AWARE_LAYOUT_REGIONS,
        "default": OcrMode.DEFAULT,
    }
    return mode_map.get(mode_str, OcrMode.DEFAULT)

# Device mapping
DEVICE_MAP = {
    "auto": AcceleratorDevice.AUTO,
    "cpu": AcceleratorDevice.CPU,
    "cuda": AcceleratorDevice.CUDA,
    "mps": AcceleratorDevice.MPS,
}

# Table mode mapping
TABLE_MODE_MAP = {
    "fast": TableFormerMode.FAST,
    "accurate": TableFormerMode.ACCURATE,
}


class ConversionStatus(Enum):
    """Conversion job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversionJob:
    """Represents a conversion job."""

    def __init__(self, job_id: str, input_path: str, original_filename: str, settings: Dict[str, Any] = None):
        self.id = job_id
        self.input_path = input_path
        self.original_filename = original_filename
        self.settings = settings or DEFAULT_CONVERSION_SETTINGS.copy()
        self.status = ConversionStatus.PENDING
        self.progress = 0
        self.message = "Queued for processing"
        self.result = None
        self.error = None
        self.confidence = None
        self.output_paths: Dict[str, str] = {}
        self.created_at = datetime.utcnow()
        self.completed_at = None
        # Additional result data
        self.extracted_images: List[Dict] = []
        self.extracted_tables: List[Dict] = []
        self.chunks: List[Dict] = []
        self.page_count = 0
        self.document_metadata: Dict = {}
        self.ocr_backend_used: Optional[str] = None  # Actual backend used (or "none" if fallback)
        self.cpu_usage_avg_during_conversion: Optional[float] = None
        self.performance_device_used: Optional[str] = None  # cpu, cuda, mps, auto
        self.images_classify_enabled: Optional[bool] = None
        self.engine: str = (SERVER_CONFIG.get("engine", {}) or {}).get("kind", "local")
        self.page_range = (self.settings or {}).get("page_range")
        self.requested_output_formats = (self.settings or {}).get("requested_output_formats")


class ConverterService:
    """Service for handling document conversions using Docling."""

    # Class-level storage for jobs (in production, use Redis or similar)
    _jobs: Dict[str, ConversionJob] = {}
    _lock = threading.Lock()
    _converters: Dict[str, DocumentConverter] = {}  # Cache converters by settings hash

    # Job queue for sequential processing (prevents memory exhaustion)
    _job_queue: queue.Queue = None
    _worker_thread: threading.Thread = None
    _worker_running: bool = False
    _max_concurrent_jobs: int = 2  # Process max 2 jobs at a time

    def __init__(self):
        """Initialize the converter service."""
        self._default_converter = None
        self._start_worker()

    def _get_ocr_options(self, settings: Dict[str, Any]):
        """Create OCR options based on settings."""
        ocr_settings = settings.get("ocr", {})
        backend = ocr_settings.get("backend", "easyocr")
        language = ocr_settings.get("language", "en")
        ocr_mode = _resolve_ocr_mode(ocr_settings)
        try:
            ocr_scale = float(ocr_settings.get("scale", 3.0))
        except (TypeError, ValueError):
            ocr_scale = 3.0
        if ocr_scale <= 0:
            ocr_scale = 3.0

        print(
            f"[OCR] Configuring OCR backend: {backend}, language: {language}, "
            f"mode: {ocr_mode.value}, scale: {ocr_scale}"
        )

        # Map language code
        easyocr_lang = EASYOCR_LANGUAGE_MAP.get(language, "en")
        common_kwargs = {
            "mode": ocr_mode,
            "scale": ocr_scale,
        }

        try:
            if backend == "easyocr":
                print(f"[OCR] Creating EasyOCR options with lang={easyocr_lang}")
                return _instantiate_ocr_options(
                    EasyOcrOptions,
                    lang=[easyocr_lang],
                    use_gpu=ocr_settings.get("use_gpu", False),
                    confidence_threshold=ocr_settings.get("confidence_threshold", 0.5),
                    **common_kwargs,
                )
            elif backend == "tesseract":
                print(f"[OCR] Creating Tesseract options with lang={language}")
                return _instantiate_ocr_options(
                    TesseractOcrOptions,
                    lang=[language],  # Tesseract uses standard language codes
                    **common_kwargs,
                )
            elif backend == "ocrmac":
                ocrmac_lang = _normalize_ocr_language("ocrmac", language)
                print(f"[OCR] Creating OcrMac options with lang={ocrmac_lang or '[default]'} (from {language})")
                return _instantiate_ocr_options(
                    OcrMacOptions,
                    lang=ocrmac_lang,
                    **common_kwargs,
                )
            elif backend == "rapidocr":
                print(f"[OCR] Creating RapidOCR options with lang={language}")
                return _instantiate_ocr_options(
                    RapidOcrOptions,
                    lang=[language],
                    **common_kwargs,
                )
            else:
                # Default to EasyOCR
                print(f"[OCR] Unknown backend '{backend}', defaulting to EasyOCR")
                return _instantiate_ocr_options(
                    EasyOcrOptions,
                    lang=[easyocr_lang],
                    use_gpu=False,
                    **common_kwargs,
                )
        except Exception as e:
            print(f"[OCR] Error creating OCR options for {backend}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _get_table_options(self, settings: Dict[str, Any]) -> TableStructureOptions:
        """Create table structure options based on settings."""
        table_settings = settings.get("tables", {})
        mode_str = table_settings.get("mode", "accurate")
        mode = TABLE_MODE_MAP.get(mode_str, TableFormerMode.ACCURATE)

        return TableStructureOptions(
            do_cell_matching=table_settings.get("do_cell_matching", True),
            mode=mode,
        )

    def _get_accelerator_options(self, settings: Dict[str, Any]) -> AcceleratorOptions:
        """Create accelerator options based on settings."""
        perf_settings = settings.get("performance", {})
        device_str = perf_settings.get("device", "auto")
        device = DEVICE_MAP.get(device_str, AcceleratorDevice.AUTO)

        return AcceleratorOptions(
            num_threads=perf_settings.get("num_threads", 4),
            device=device,
        )

    def _get_converter(self, settings: Dict[str, Any] = None) -> DocumentConverter:
        """
        Get or create a DocumentConverter with the specified settings.

        Creates converters with OCR and table extraction settings based on user preferences.
        """
        if settings is None:
            settings = DEFAULT_CONVERSION_SETTINGS

        # Extract settings
        ocr_settings = settings.get("ocr", {})
        table_settings = settings.get("tables", {})
        image_settings = settings.get("images", {})
        perf_settings = settings.get("performance", {})
        enrichment_settings = settings.get("enrichment", {})

        ocr_enabled = ocr_settings.get("enabled", True)
        table_enabled = table_settings.get("enabled", True) and table_settings.get("structure_extraction", True)

        # Create a settings hash for caching
        settings_key = json.dumps(settings, sort_keys=True)
        settings_hash = hash(settings_key)

        if settings_hash in self._converters:
            return self._converters[settings_hash]

        pdf_settings = settings.get("pdf", {})
        pipeline_settings = settings.get("pipeline", {})
        picture_classification_enabled = bool(
            enrichment_settings.get("picture_classification", False) or image_settings.get("classify", False)
        )
        pipeline_kwargs = {
            "do_ocr": ocr_enabled,
            "do_table_structure": table_enabled,
            "generate_page_images": image_settings.get("generate_page_images", False),
            "generate_picture_images": image_settings.get("generate_picture_images", True),
            "generate_table_images": image_settings.get("generate_table_images", True),
            "images_scale": image_settings.get("images_scale", 1.0),
            "accelerator_options": self._get_accelerator_options(settings),
            "do_code_enrichment": enrichment_settings.get("code_enrichment", False),
            "do_formula_enrichment": enrichment_settings.get("formula_enrichment", False),
            "do_picture_classification": picture_classification_enabled,
            "do_picture_description": enrichment_settings.get("picture_description", False),
            "do_chart_extraction": enrichment_settings.get("chart_extraction", False),
            "do_pdf_heading_hierarchy": pdf_settings.get("do_pdf_heading_hierarchy", False),
            "image_export_mode": pdf_settings.get("image_export_mode", "placeholder"),
            "pdf_backend": pdf_settings.get("pdf_backend", "docling_parse"),
        }
        heading_opts = pdf_settings.get("pdf_heading_hierarchy_options") or {}
        if heading_opts:
            pipeline_kwargs["pdf_heading_hierarchy_options"] = heading_opts
        fields = getattr(PdfPipelineOptions, "model_fields", None)
        allowed_fields = set(fields.keys()) if fields else set()
        if allowed_fields:
            pipeline_kwargs = {k: v for k, v in pipeline_kwargs.items() if k in allowed_fields}
        pipeline_options = PdfPipelineOptions(**pipeline_kwargs)

        # Log enrichment settings
        if any([enrichment_settings.get("code_enrichment"),
                enrichment_settings.get("formula_enrichment"),
                enrichment_settings.get("picture_classification"),
                enrichment_settings.get("picture_description")]):
            logger.info(
                "Enrichment enabled code=%s formula=%s pic_class=%s pic_desc=%s chart=%s",
                enrichment_settings.get("code_enrichment", False),
                enrichment_settings.get("formula_enrichment", False),
                enrichment_settings.get("picture_classification", False),
                enrichment_settings.get("picture_description", False),
                enrichment_settings.get("chart_extraction", False),
            )

        # Set document timeout if specified
        timeout = perf_settings.get("document_timeout")
        if timeout:
            pipeline_options.document_timeout = float(timeout)

        # Configure OCR options if enabled
        if ocr_enabled:
            logger.info("OCR is enabled; configuring OCR options")
            pipeline_options.ocr_options = self._get_ocr_options(settings)
            logger.info("OCR options configured: %s", type(pipeline_options.ocr_options).__name__)
        else:
            logger.info("OCR is disabled")

        # Configure table structure options
        if table_enabled:
            pipeline_options.table_structure_options = self._get_table_options(settings)

        pipeline_kind = pipeline_settings.get("kind", "standard")
        logger.info("Creating DocumentConverter with pipeline=%s", pipeline_kind)

        # Create format options for PDF/images; try specialized pipeline kinds when available.
        format_options = {}
        if pipeline_kind in {"vlm", "asr"}:
            logger.info("Requested pipeline kind=%s; attempting dynamic Docling pipeline support", pipeline_kind)
        if pipeline_kind == "vlm":
            vlm_pipeline_cls = getattr(pipeline_options_module, "VlmPipelineOptions", None)
            vlm_format_cls = getattr(pipeline_options_module, "VlmFormatOption", None)
            if vlm_pipeline_cls and vlm_format_cls:
                vlm_preset = pipeline_settings.get("vlm_preset")
                vlm_custom = pipeline_settings.get("vlm_custom_config")
                if vlm_custom and SERVER_CONFIG.get("allow_custom_vlm_config", False):
                    try:
                        vlm_pipeline_options = vlm_pipeline_cls(**vlm_custom)
                    except Exception:
                        logger.exception("Invalid vlm_custom_config; falling back to preset/default")
                        vlm_pipeline_options = vlm_pipeline_cls.from_preset(vlm_preset or "default")
                else:
                    vlm_pipeline_options = vlm_pipeline_cls.from_preset(vlm_preset or "default")
                format_options[InputFormat.PDF] = vlm_format_cls(pipeline_options=vlm_pipeline_options)
                format_options[InputFormat.IMAGE] = vlm_format_cls(pipeline_options=vlm_pipeline_options)
            else:
                logger.warning("Docling VLM classes unavailable; falling back to standard pipeline")
        elif pipeline_kind == "asr":
            asr_pipeline_cls = getattr(pipeline_options_module, "AsrPipelineOptions", None)
            asr_format_cls = getattr(pipeline_options_module, "AsrFormatOption", None)
            if asr_pipeline_cls and asr_format_cls:
                asr_pipeline_options = asr_pipeline_cls()
                for maybe_fmt in ("AUDIO", "VIDEO"):
                    input_format = getattr(InputFormat, maybe_fmt, None)
                    if input_format is not None:
                        format_options[input_format] = asr_format_cls(pipeline_options=asr_pipeline_options)
            else:
                logger.warning("Docling ASR classes unavailable; falling back to standard pipeline")

        if not format_options:
            pdf_format_option = PdfFormatOption(
                pipeline_options=pipeline_options,
            )
            image_format_option = ImageFormatOption(
                pipeline_options=pipeline_options,
            )
            format_options = {
                InputFormat.PDF: pdf_format_option,
                InputFormat.IMAGE: image_format_option,
            }
        converter = DocumentConverter(format_options=format_options)

        logger.info("DocumentConverter created successfully")

        # Cache the converter
        self._converters[settings_hash] = converter

        return converter

    @property
    def converter(self) -> DocumentConverter:
        """Lazy initialization of default DocumentConverter."""
        if self._default_converter is None:
            self._default_converter = self._get_converter()
        return self._default_converter

    def create_job(self, input_path: str, original_filename: str, settings: Dict[str, Any] = None, job_id: str = None) -> ConversionJob:
        """Create a new conversion job.

        Args:
            input_path: Path to the input file
            original_filename: Original filename
            settings: Conversion settings
            job_id: Optional pre-assigned job ID (generated if not provided)
        """
        if job_id is None:
            job_id = str(uuid.uuid4())
        job = ConversionJob(job_id, input_path, original_filename, settings)

        with self._lock:
            self._jobs[job_id] = job

        return job

    def get_job(self, job_id: str) -> Optional[ConversionJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def _start_worker(self):
        """Start the background worker thread for processing jobs."""
        if ConverterService._job_queue is None:
            ConverterService._job_queue = queue.Queue()

        if ConverterService._worker_thread is None or not ConverterService._worker_thread.is_alive():
            ConverterService._worker_running = True
            ConverterService._worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True
            )
            ConverterService._worker_thread.start()

    def _worker_loop(self):
        """Background worker that processes jobs from the queue."""
        active_threads = []

        while ConverterService._worker_running:
            try:
                # Clean up completed threads
                active_threads = [t for t in active_threads if t.is_alive()]

                # Wait for a job if we have capacity
                if len(active_threads) < ConverterService._max_concurrent_jobs:
                    try:
                        job, on_complete = ConverterService._job_queue.get(timeout=0.5)

                        # Start conversion in a thread
                        thread = threading.Thread(
                            target=self._run_conversion,
                            args=(job, on_complete),
                            daemon=True
                        )
                        thread.start()
                        active_threads.append(thread)

                        ConverterService._job_queue.task_done()
                    except queue.Empty:
                        continue
                else:
                    # At capacity, wait a bit before checking again
                    import time
                    time.sleep(0.5)

            except Exception as e:
                print(f"Worker error: {e}")
                import time
                time.sleep(1)

    def get_queue_depth(self) -> int:
        """Return current number of jobs waiting in the queue."""
        if ConverterService._job_queue is None:
            return 0
        return ConverterService._job_queue.qsize()

    def start_conversion(self, job: ConversionJob, on_complete: Callable = None):
        """Queue a job for async conversion."""
        # Ensure worker is running
        self._start_worker()

        # Add job to queue
        ConverterService._job_queue.put((job, on_complete))
        job.message = f"Queued for processing (position: {ConverterService._job_queue.qsize()})"

    @staticmethod
    def _relativize_cached_artifact_path(path_value: str, output_base_path: Path) -> str:
        """
        Store artifact paths relative to the job output root.

        During content-store moves we still have absolute paths that point at the
        original job directory. Paths must be made relative to `output_base_path`
        (not the content-store destination) so nested folders like `images/` and
        `tables/` are preserved in metadata.
        """
        artifact_path = Path(path_value)
        try:
            return str(artifact_path.relative_to(output_base_path))
        except ValueError:
            return artifact_path.name

    def _extract_images(self, doc, output_base: Path, job: ConversionJob) -> List[Dict]:
        """Extract images from the document."""
        images = []
        try:
            # Get all picture items from the document
            if hasattr(doc, 'pictures') and doc.pictures:
                for i, picture in enumerate(doc.pictures):
                    if hasattr(picture, 'image') and picture.image:
                        try:
                            # Save image to file
                            img_filename = f"image_{i+1}.png"
                            img_path = output_base / "images" / img_filename
                            img_path.parent.mkdir(parents=True, exist_ok=True)

                            # Get image data
                            if hasattr(picture.image, 'pil_image'):
                                pil_img = picture.image.pil_image
                                pil_img.save(str(img_path), "PNG")
                            elif hasattr(picture.image, 'uri'):
                                # Handle URI-based images
                                import urllib.request
                                urllib.request.urlretrieve(picture.image.uri, str(img_path))

                            # Get caption if available
                            caption = ""
                            if hasattr(picture, 'captions') and picture.captions:
                                caption = " ".join([c.text for c in picture.captions if hasattr(c, 'text')])

                            images.append({
                                "id": i + 1,
                                "filename": img_filename,
                                "path": str(img_path),
                                "caption": caption,
                                "label": picture.label if hasattr(picture, 'label') else None,
                            })
                        except Exception as e:
                            print(f"Error extracting image {i}: {e}")
        except Exception as e:
            print(f"Error extracting images: {e}")

        return images

    def _extract_tables(self, doc, output_base: Path, job: ConversionJob) -> List[Dict]:
        """Extract tables from the document."""
        tables = []
        try:
            if hasattr(doc, 'tables') and doc.tables:
                for i, table in enumerate(doc.tables):
                    try:
                        table_data = {
                            "id": i + 1,
                            "label": table.label if hasattr(table, 'label') else None,
                            "caption": "",
                            "rows": [],
                            "csv_path": None,
                        }

                        # Get caption if available
                        if hasattr(table, 'captions') and table.captions:
                            table_data["caption"] = " ".join([c.text for c in table.captions if hasattr(c, 'text')])

                        # Extract table data
                        if hasattr(table, 'data') and table.data:
                            # Export to CSV
                            csv_filename = f"table_{i+1}.csv"
                            csv_path = output_base / "tables" / csv_filename
                            csv_path.parent.mkdir(parents=True, exist_ok=True)

                            # Build CSV content
                            csv_rows = []
                            if hasattr(table.data, 'grid'):
                                for row in table.data.grid:
                                    csv_row = []
                                    for cell in row:
                                        cell_text = cell.text if hasattr(cell, 'text') else str(cell)
                                        csv_row.append(cell_text)
                                    csv_rows.append(csv_row)
                                    table_data["rows"].append(csv_row)

                            # Write CSV
                            import csv
                            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerows(csv_rows)

                            table_data["csv_path"] = str(csv_path)

                        # Save table image if available
                        if hasattr(table, 'image') and table.image:
                            try:
                                img_filename = f"table_{i+1}.png"
                                img_path = output_base / "tables" / img_filename
                                if hasattr(table.image, 'pil_image'):
                                    table.image.pil_image.save(str(img_path), "PNG")
                                    table_data["image_path"] = str(img_path)
                            except Exception as e:
                                print(f"Error saving table image {i}: {e}")

                        tables.append(table_data)
                    except Exception as e:
                        print(f"Error extracting table {i}: {e}")
        except Exception as e:
            print(f"Error extracting tables: {e}")

        return tables

    def _generate_chunks(self, doc, settings: Dict[str, Any]) -> List[Dict]:
        """Generate document chunks for RAG applications."""
        chunks = []

        if not CHUNKING_AVAILABLE:
            return chunks

        chunking_settings = settings.get("chunking", {})
        if not chunking_settings.get("enabled", False):
            return chunks

        try:
            chunker = build_chunker(chunking_settings)

            for i, chunk in enumerate(chunker.chunk(doc)):
                chunk_data: Dict[str, Any] = {
                    "id": i + 1,
                    "text": chunk.text,
                    "meta": {}
                }
                if hasattr(chunk, "raw_text"):
                    chunk_data["raw_text"] = getattr(chunk, "raw_text")

                if hasattr(chunk, 'meta'):
                    # Extract relevant metadata
                    if hasattr(chunk.meta, 'headings'):
                        chunk_data["meta"]["headings"] = chunk.meta.headings
                    if hasattr(chunk.meta, 'page'):
                        chunk_data["meta"]["page"] = chunk.meta.page
                    if hasattr(chunk.meta, "has_image"):
                        chunk_data["meta"]["has_image"] = chunk.meta.has_image

                chunks.append(chunk_data)
        except Exception as e:
            logger.exception("Error generating chunks: %s", e)

        return chunks

    def generate_chunks_for_document(self, doc, settings: Dict[str, Any] = None) -> List[Dict]:
        """
        Generate RAG chunks for a DoclingDocument on demand.
        Uses chunking settings from settings, or defaults if not provided.
        """
        chunks = []
        if not CHUNKING_AVAILABLE:
            return chunks

        settings = settings or {}
        chunking_settings = settings.get("chunking", {})
        # For on-demand generation, always generate (ignore enabled flag)
        try:
            chunker = build_chunker(chunking_settings)
            for i, chunk in enumerate(chunker.chunk(doc)):
                chunk_data: Dict[str, Any] = {
                    "id": i + 1,
                    "text": chunk.text,
                    "meta": {}
                }
                if hasattr(chunk, "raw_text"):
                    chunk_data["raw_text"] = getattr(chunk, "raw_text")
                if hasattr(chunk, 'meta'):
                    if hasattr(chunk.meta, 'headings'):
                        chunk_data["meta"]["headings"] = chunk.meta.headings
                    if hasattr(chunk.meta, 'page'):
                        chunk_data["meta"]["page"] = chunk.meta.page
                    if hasattr(chunk.meta, "has_image"):
                        chunk_data["meta"]["has_image"] = chunk.meta.has_image
                chunks.append(chunk_data)
        except Exception as e:
            logger.exception("Error generating chunks: %s", e)

        return chunks

    def _run_conversion(self, job: ConversionJob, on_complete: Callable = None):
        """Run the actual conversion process."""
        from utils.system_info import sample_cpu_during_conversion

        # Content-addressed cache check: skip conversion if we have identical content
        try:
            file_hash = compute_file_hash(job.input_path)
            settings_hash = compute_settings_hash(job.settings)
            content_hash = compute_content_hash(file_hash, settings_hash)
            if content_store_exists(content_hash):
                content_store_path = get_content_store_path(content_hash)
                output_base = Path(OUTPUT_FOLDER) / job.id
                if output_base.exists():
                    shutil.rmtree(output_base)
                output_base.symlink_to(content_store_path)
                meta = load_metadata(content_hash)
                if meta:
                    output_paths_rel = meta.get("output_paths", {})
                    job.output_paths = {
                        k: str(output_base / v) for k, v in output_paths_rel.items()
                    }
                    doc_path_rel = meta.get("document_json_path", "")
                    job.document_json_path = str(output_base / doc_path_rel) if doc_path_rel else None
                    job.extracted_images = []
                    for img in meta.get("extracted_images", []):
                        img_copy = dict(img)
                        if "path" in img_copy and img_copy["path"]:
                            img_copy["path"] = str(output_base / img_copy["path"])
                        job.extracted_images.append(img_copy)
                    job.extracted_tables = []
                    for tbl in meta.get("extracted_tables", []):
                        tbl_copy = dict(tbl)
                        for key in ("csv_path", "image_path"):
                            if key in tbl_copy and tbl_copy[key]:
                                tbl_copy[key] = str(output_base / tbl_copy[key])
                        job.extracted_tables.append(tbl_copy)
                    job.chunks = meta.get("chunks", [])
                    job.page_count = meta.get("page_count", 0)
                    job.confidence = meta.get("confidence")
                job.content_hash = content_hash
                job.status = ConversionStatus.COMPLETED
                job.progress = 100
                job.message = "Conversion completed (from cache)"
                job.completed_at = datetime.utcnow()
                if on_complete:
                    on_complete(job)
                return
        except Exception as e:
            print(f"[converter] Cache check skipped: {e}")

        stop_event = threading.Event()
        cpu_samples_container: list = []  # [list] - thread appends result here

        def _sample_cpu():
            samples = sample_cpu_during_conversion(stop_event)
            cpu_samples_container.append(samples)

        cpu_thread = None
        try:
            cpu_thread = threading.Thread(target=_sample_cpu, daemon=True)
            cpu_thread.start()

            job.status = ConversionStatus.PROCESSING
            job.progress = 10
            job.message = "Starting document conversion..."

            # Check if OCR is enabled for status message
            ocr_enabled = job.settings.get("ocr", {}).get("enabled", True)
            ocr_language = job.settings.get("ocr", {}).get("language", "en")
            ocr_backend = job.settings.get("ocr", {}).get("backend", "easyocr")
            job.ocr_backend_used = ocr_backend if ocr_enabled else "none"

            job.progress = 20
            if ocr_enabled:
                job.message = f"Analyzing document with OCR ({ocr_backend}, {ocr_language})..."
            else:
                job.message = "Analyzing document structure..."

            # Try to get converter and convert, with fallback for OCR errors
            result = None
            conversion_error = None

            try:
                # Get converter with job-specific settings
                converter = self._get_converter(job.settings)
                job.progress = 30
                page_range = job.settings.get("page_range")
                if page_range and isinstance(page_range, (list, tuple)) and len(page_range) == 2:
                    result = converter.convert(job.input_path, page_range=tuple(page_range))
                else:
                    result = converter.convert(job.input_path)
            except Exception as ocr_error:
                error_str = str(ocr_error)
                print(f"[converter] Conversion error: {error_str}")
                import traceback
                traceback.print_exc()

                # Check if it's an OCR-related error that we should retry without OCR
                ocr_error_indicators = [
                    "meta tensor", "EasyOCR", "tesseract", "ocrmac", "rapidocr",
                    "OCR", "OcrOptions", "No module named", "cannot import",
                    "CUDA", "cuda", "GPU", "gpu"
                ]
                is_ocr_error = any(indicator.lower() in error_str.lower() for indicator in ocr_error_indicators)

                if is_ocr_error:
                    print(f"[converter] OCR error detected, retrying without OCR...")
                    job.message = "OCR failed, retrying without OCR..."
                    job.progress = 25

                    # Disable OCR and try again
                    fallback_settings = job.settings.copy()
                    fallback_settings["ocr"] = fallback_settings.get("ocr", {}).copy()
                    fallback_settings["ocr"]["enabled"] = False

                    try:
                        converter = self._get_converter(fallback_settings)
                        job.progress = 30
                        if page_range and isinstance(page_range, (list, tuple)) and len(page_range) == 2:
                            result = converter.convert(job.input_path, page_range=tuple(page_range))
                        else:
                            result = converter.convert(job.input_path)
                        job.ocr_backend_used = "none"
                        job.settings = fallback_settings  # Use effective settings for content hash
                        job.message = "Converted without OCR (OCR initialization failed)"
                        print(f"[converter] Successfully converted without OCR")
                    except Exception as fallback_error:
                        print(f"[converter] Fallback conversion also failed: {fallback_error}")
                        conversion_error = fallback_error
                else:
                    conversion_error = ocr_error

            if conversion_error:
                raise conversion_error

            job.progress = 50
            job.message = "Processing document content..."

            # Check conversion status
            if result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
                # Calculate average confidence from layout predictions
                job.confidence = self._calculate_confidence(result)
                job.page_count = len(result.pages) if hasattr(result, 'pages') else 0

                # Generate all output formats
                output_base = OUTPUT_FOLDER / job.id
                output_base.mkdir(parents=True, exist_ok=True)

                doc = result.document

                job.progress = 60
                job.message = "Extracting images and tables..."

                # Extract images
                image_settings = job.settings.get("images", {})
                if image_settings.get("extract", True):
                    docling_images = self._extract_images(doc, output_base, job)

                    # Merge with pre-extracted images (from URL HTML downloads)
                    pre_extracted = getattr(job, 'extracted_images', []) or []
                    if pre_extracted:
                        # Pre-extracted images were already saved, just need to renumber
                        # to avoid conflicts with Docling-extracted images
                        max_id = max([img.get('id', 0) for img in pre_extracted], default=0)
                        for img in docling_images:
                            img['id'] = img['id'] + max_id
                        job.extracted_images = pre_extracted + docling_images
                        print(f"[converter] Merged {len(pre_extracted)} pre-extracted + {len(docling_images)} docling images")
                    else:
                        job.extracted_images = docling_images

                # Extract tables
                table_settings = job.settings.get("tables", {})
                if table_settings.get("enabled", True):
                    job.extracted_tables = self._extract_tables(doc, output_base, job)

                job.progress = 70
                job.message = "Generating output formats..."

                # Export to different formats
                requested_formats = set(job.settings.get("requested_output_formats") or [])
                def should_export(fmt: str) -> bool:
                    return not requested_formats or fmt in requested_formats
                # Markdown
                if should_export("markdown"):
                    md_path = output_base / f"{Path(job.original_filename).stem}.md"
                    md_content = doc.export_to_markdown()
                    md_path.write_text(md_content, encoding="utf-8")
                    job.output_paths["markdown"] = str(md_path)

                job.progress = 75

                # HTML
                try:
                    if not should_export("html"):
                        raise RuntimeError("skip")
                    html_path = output_base / f"{Path(job.original_filename).stem}.html"
                    html_content = doc.export_to_html()
                    html_path.write_text(html_content, encoding="utf-8")
                    job.output_paths["html"] = str(html_path)
                except Exception as e:
                    print(f"HTML export failed: {e}")

                job.progress = 80

                # JSON (full document structure)
                try:
                    if not should_export("json"):
                        raise RuntimeError("skip")
                    json_path = output_base / f"{Path(job.original_filename).stem}.json"
                    json_content = doc.export_to_dict()
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(json_content, f, indent=2, default=str)
                    job.output_paths["json"] = str(json_path)
                except Exception as e:
                    print(f"JSON export failed: {e}")

                job.progress = 85

                # Plain text
                try:
                    if not should_export("text"):
                        raise RuntimeError("skip")
                    txt_path = output_base / f"{Path(job.original_filename).stem}.txt"
                    txt_content = doc.export_to_text()
                    txt_path.write_text(txt_content, encoding="utf-8")
                    job.output_paths["text"] = str(txt_path)
                except Exception as e:
                    print(f"Text export failed: {e}")

                # DocTags
                try:
                    if not should_export("doctags"):
                        raise RuntimeError("skip")
                    doctags_path = output_base / f"{Path(job.original_filename).stem}.doctags"
                    doctags_content = doc.export_to_doctags()
                    doctags_path.write_text(str(doctags_content), encoding="utf-8")
                    job.output_paths["doctags"] = str(doctags_path)
                except Exception as e:
                    print(f"DocTags export failed: {e}")

                # DocLang
                try:
                    if not should_export("doclang"):
                        raise RuntimeError("skip")
                    doclang_path = output_base / f"{Path(job.original_filename).stem}.dclg.xml"
                    doclang_content = doc.export_to_doclang()
                    doclang_path.write_text(str(doclang_content), encoding="utf-8")
                    job.output_paths["doclang"] = str(doclang_path)
                except Exception as e:
                    print(f"DocLang export failed: {e}")

                # DCLX (if supported by this Docling version)
                try:
                    if not should_export("dclx"):
                        raise RuntimeError("skip")
                    dclx_path = output_base / f"{Path(job.original_filename).stem}.dclx"
                    dclx_content = doc.export_to_dclx()
                    if isinstance(dclx_content, bytes):
                        dclx_path.write_bytes(dclx_content)
                    else:
                        dclx_path.write_text(str(dclx_content), encoding="utf-8")
                    job.output_paths["dclx"] = str(dclx_path)
                except Exception as e:
                    logger.debug("DCLX export skipped/failed: %s", e)

                # YAML (if supported by this Docling version)
                try:
                    if not should_export("yaml"):
                        raise RuntimeError("skip")
                    yaml_path = output_base / f"{Path(job.original_filename).stem}.yaml"
                    if hasattr(doc, "export_to_yaml"):
                        yaml_content = doc.export_to_yaml()
                        yaml_path.write_text(str(yaml_content), encoding="utf-8")
                    else:
                        doc_dict = doc.export_to_dict()
                        try:
                            import yaml  # type: ignore
                            yaml_path.write_text(yaml.safe_dump(doc_dict, allow_unicode=True), encoding="utf-8")
                        except Exception:
                            yaml_path.write_text(json.dumps(doc_dict, indent=2, default=str), encoding="utf-8")
                    job.output_paths["yaml"] = str(yaml_path)
                except Exception as e:
                    logger.debug("YAML export skipped/failed: %s", e)

                # HTML split-by-page (best effort fallback to normal HTML)
                try:
                    if not should_export("html_split_page"):
                        raise RuntimeError("skip")
                    html_split_path = output_base / f"{Path(job.original_filename).stem}.split.html"
                    html_split = doc.export_to_html(split_page=True)
                    html_split_path.write_text(str(html_split), encoding="utf-8")
                    job.output_paths["html_split_page"] = str(html_split_path)
                except Exception as e:
                    logger.debug("HTML split-page export skipped/failed: %s", e)

                # VTT
                try:
                    if not should_export("vtt"):
                        raise RuntimeError("skip")
                    vtt_path = output_base / f"{Path(job.original_filename).stem}.vtt"
                    vtt_content = doc.export_to_vtt()
                    vtt_path.write_text(str(vtt_content), encoding="utf-8")
                    job.output_paths["vtt"] = str(vtt_path)
                except Exception as e:
                    logger.debug("VTT export skipped/failed: %s", e)

                # Document tokens
                try:
                    if not should_export("document_tokens"):
                        raise RuntimeError("skip")
                    tokens_path = output_base / f"{Path(job.original_filename).stem}.tokens.json"
                    tokens_content = doc.export_to_document_tokens()
                    with open(tokens_path, 'w', encoding='utf-8') as f:
                        json.dump(list(tokens_content), f, indent=2, default=str)
                    job.output_paths["document_tokens"] = str(tokens_path)
                except Exception as e:
                    print(f"Document tokens export failed: {e}")

                job.progress = 90
                job.message = "Generating chunks for RAG..."

                # Generate chunks if enabled
                job.chunks = self._generate_chunks(doc, job.settings)

                # Save chunks if generated
                if job.chunks and should_export("chunks"):
                    chunks_path = output_base / f"{Path(job.original_filename).stem}.chunks.json"
                    with open(chunks_path, 'w', encoding='utf-8') as f:
                        json.dump(job.chunks, f, indent=2)
                    job.output_paths["chunks"] = str(chunks_path)

                # Save DoclingDocument for later reloading
                try:
                    doc_json_path = output_base / f"{Path(job.original_filename).stem}.document.json"
                    doc_dict = doc.export_to_dict()
                    with open(doc_json_path, 'w', encoding='utf-8') as f:
                        json.dump(doc_dict, f, indent=2, default=str)
                    job.document_json_path = str(doc_json_path)
                    print(f"[converter] Saved DoclingDocument to {doc_json_path}")
                except Exception as e:
                    print(f"[converter] Failed to save DoclingDocument: {e}")

                # Content-addressed store: move to content store and symlink for deduplication
                try:
                    file_hash = compute_file_hash(job.input_path)
                    settings_hash = compute_settings_hash(job.settings)
                    content_hash = compute_content_hash(file_hash, settings_hash)
                    content_store_path = get_content_store_path(content_hash)
                    output_base_path = Path(OUTPUT_FOLDER) / job.id
                    if content_store_path.exists():
                        # Race: another job already stored this content
                        shutil.rmtree(output_base_path)
                        meta = load_metadata(content_hash)
                    else:
                        shutil.move(str(output_base_path), str(content_store_path))
                        stem = Path(job.original_filename).stem
                        meta = {
                            "output_paths": {k: Path(v).name for k, v in job.output_paths.items()},
                            "document_json_path": f"{stem}.document.json",
                            "extracted_images": [],
                            "extracted_tables": [],
                            "chunks": job.chunks or [],
                            "page_count": job.page_count,
                            "confidence": job.confidence,
                        }
                        for img in (job.extracted_images or []):
                            img_copy = dict(img)
                            if img_copy.get("path"):
                                img_copy["path"] = self._relativize_cached_artifact_path(
                                    img_copy["path"], output_base_path
                                )
                            meta["extracted_images"].append(img_copy)
                        for tbl in (job.extracted_tables or []):
                            tbl_copy = dict(tbl)
                            for key in ("csv_path", "image_path"):
                                if tbl_copy.get(key):
                                    tbl_copy[key] = self._relativize_cached_artifact_path(
                                        tbl_copy[key], output_base_path
                                    )
                            meta["extracted_tables"].append(tbl_copy)
                        save_metadata(content_hash, meta)
                    output_base_path.symlink_to(content_store_path)
                    if meta:
                        job.output_paths = {k: str(output_base_path / v) for k, v in meta["output_paths"].items()}
                        job.document_json_path = str(output_base_path / meta["document_json_path"])
                        job.extracted_images = [
                            {**img, "path": str(output_base_path / img["path"]) if img.get("path") else img}
                            for img in meta.get("extracted_images", [])
                        ]
                        job.extracted_tables = [
                            {
                                **tbl,
                                "csv_path": str(output_base_path / tbl["csv_path"]) if tbl.get("csv_path") else None,
                                "image_path": str(output_base_path / tbl["image_path"]) if tbl.get("image_path") else None,
                            }
                            for tbl in meta.get("extracted_tables", [])
                        ]
                    job.content_hash = content_hash
                    print(f"[converter] Stored in content store {content_hash}")
                except Exception as e:
                    print(f"[converter] Content store save skipped: {e}")

                job.progress = 100
                job.status = ConversionStatus.COMPLETED

                if result.status.name == "SUCCESS":
                    job.message = "Conversion completed successfully"
                else:
                    job.message = "Conversion completed with some warnings"

                job.result = {
                    "markdown_preview": md_content[:5000] if len(md_content) > 5000 else md_content,
                    "formats_available": list(job.output_paths.keys()),
                    "page_count": job.page_count,
                    "images_count": len(job.extracted_images),
                    "tables_count": len(job.extracted_tables),
                    "chunks_count": len(job.chunks),
                    "warnings": [str(e) for e in result.errors] if hasattr(result, 'errors') and result.errors else []
                }

            else:
                job.status = ConversionStatus.FAILED
                job.error = f"Conversion failed with status: {result.status.name}"
                job.message = job.error
                if hasattr(result, 'errors') and result.errors:
                    job.error += f" - {result.errors}"

        except Exception as e:
            job.status = ConversionStatus.FAILED
            job.error = str(e)
            job.message = f"Conversion failed: {str(e)}"

        finally:
            stop_event.set()
            if cpu_thread:
                cpu_thread.join(timeout=2.0)
            cpu_samples = cpu_samples_container[0] if cpu_samples_container else []
            if cpu_samples:
                job.cpu_usage_avg_during_conversion = round(sum(cpu_samples) / len(cpu_samples), 1)
            # Record performance device: resolve "auto" to actual hardware at completion
            perf_setting = (job.settings.get("performance") or {}).get("device", "auto")
            if perf_setting == "auto":
                try:
                    from utils.system_info import get_hardware_type
                    job.performance_device_used = get_hardware_type().get("type", "auto")
                except Exception:
                    job.performance_device_used = "auto"
            else:
                job.performance_device_used = perf_setting
            job.images_classify_enabled = (job.settings.get("images") or {}).get("classify", False)
            job.completed_at = datetime.utcnow()
            if on_complete:
                on_complete(job)

    def _calculate_confidence(self, result) -> Optional[float]:
        """
        Calculate average confidence from layout predictions.

        Docling stores confidence scores at the cluster level within page predictions.
        This method extracts all confidence values and returns an average.
        """
        confidences = []

        try:
            # Iterate through all pages
            if hasattr(result, 'pages'):
                for page in result.pages:
                    # Try multiple ways to access confidence based on Docling version
                    if hasattr(page, 'predictions') and page.predictions:
                        predictions = page.predictions

                        # Try layout predictions
                        if hasattr(predictions, 'layout') and predictions.layout:
                            layout = predictions.layout
                            if hasattr(layout, 'clusters'):
                                for cluster in layout.clusters:
                                    if hasattr(cluster, 'confidence') and cluster.confidence is not None:
                                        confidences.append(cluster.confidence)
                                    # Also check children clusters
                                    if hasattr(cluster, 'children'):
                                        for child in cluster.children:
                                            if hasattr(child, 'confidence') and child.confidence is not None:
                                                confidences.append(child.confidence)

                        # Try OCR predictions if available
                        if hasattr(predictions, 'ocr') and predictions.ocr:
                            ocr = predictions.ocr
                            if hasattr(ocr, 'cells'):
                                for cell in ocr.cells:
                                    if hasattr(cell, 'confidence') and cell.confidence is not None:
                                        confidences.append(cell.confidence)

                    # Also try page-level confidence
                    if hasattr(page, 'confidence') and page.confidence is not None:
                        confidences.append(page.confidence)

            # Also check document-level metadata for confidence
            if hasattr(result, 'document') and result.document:
                doc = result.document
                if hasattr(doc, 'metadata') and doc.metadata:
                    meta = doc.metadata
                    if hasattr(meta, 'confidence') and meta.confidence is not None:
                        confidences.append(meta.confidence)

            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"[confidence] Found {len(confidences)} confidence values, average: {avg_confidence:.4f}")
                return avg_confidence
            else:
                print("[confidence] No confidence values found in result")
        except Exception as e:
            # Log the error but don't fail the conversion
            print(f"Error calculating confidence: {e}")
            import traceback
            traceback.print_exc()

        return None

    def get_output_content(self, job_id: str, format_type: str) -> Optional[str]:
        """Get the output content for a specific format."""
        job = self.get_job(job_id)
        if job and job.status == ConversionStatus.COMPLETED:
            output_path = job.output_paths.get(format_type)
            if output_path:
                path = Path(output_path)
                if path.exists():
                    return path.read_text(encoding="utf-8")

        # Fallback: Check output directory directly (for multi-worker scenarios)
        validate_job_id(job_id)
        output_dir = get_validated_output_dir(job_id, Path(OUTPUT_FOLDER))
        if output_dir.exists():
            format_extensions = {
                "markdown": ".md",
                "html": ".html",
                "json": ".json",
                "text": ".txt",
                "doctags": ".doctags",
                "doclang": ".dclg.xml",
                "document_tokens": ".tokens.json",
                "chunks": ".chunks.json"
            }
            ext = format_extensions.get(format_type)
            if ext:
                files = list(output_dir.glob(f"*{ext}"))
                if files:
                    return files[0].read_text(encoding="utf-8")

        return None

    def get_output_path(self, job_id: str, format_type: str) -> Optional[Path]:
        """Get the output file path for a specific format."""
        job = self.get_job(job_id)
        if job and job.status == ConversionStatus.COMPLETED:
            output_path = job.output_paths.get(format_type)
            if output_path:
                path = Path(output_path)
                if path.exists():
                    return path

        # Fallback: Check output directory directly (for multi-worker scenarios)
        validate_job_id(job_id)
        output_dir = get_validated_output_dir(job_id, Path(OUTPUT_FOLDER))
        if output_dir.exists():
            format_extensions = {
                "markdown": ".md",
                "html": ".html",
                "json": ".json",
                "text": ".txt",
                "doctags": ".doctags",
                "doclang": ".dclg.xml",
                "document_tokens": ".tokens.json",
                "chunks": ".chunks.json"
            }
            ext = format_extensions.get(format_type)
            if ext:
                files = list(output_dir.glob(f"*{ext}"))
                if files:
                    return files[0]

        return None

    def get_extracted_images(self, job_id: str) -> List[Dict]:
        """Get extracted images for a job."""
        job = self.get_job(job_id)
        if not job or job.status != ConversionStatus.COMPLETED:
            return []
        return job.extracted_images

    def get_extracted_tables(self, job_id: str) -> List[Dict]:
        """Get extracted tables for a job."""
        job = self.get_job(job_id)
        if not job or job.status != ConversionStatus.COMPLETED:
            return []
        return job.extracted_tables

    def get_chunks(self, job_id: str) -> List[Dict]:
        """Get document chunks for a job."""
        job = self.get_job(job_id)
        if not job or job.status != ConversionStatus.COMPLETED:
            return []
        return job.chunks

    def cleanup_job(self, job_id: str):
        """Remove a job and its output files."""
        validate_job_id(job_id)
        job = self._jobs.pop(job_id, None)
        if job:
            # Clean up output files (output_base is validated)
            output_base = get_validated_output_dir(job_id, Path(OUTPUT_FOLDER))
            if output_base.exists():
                import shutil
                shutil.rmtree(output_base, ignore_errors=True)

    @staticmethod
    def detect_input_format(filename: str) -> Optional[str]:
        """Detect input format from filename extension."""
        ext = Path(filename).suffix.lower()
        format_map = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".pptx": "pptx",
            ".xlsx": "xlsx",
            ".html": "html",
            ".htm": "html",
            ".md": "md",
            ".markdown": "md",
            ".csv": "csv",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".tiff": "image",
            ".tif": "image",
            ".gif": "image",
            ".webp": "image",
            ".bmp": "image",
            ".wav": "audio",
            ".mp3": "audio",
            ".mp4": "video",
            ".mov": "video",
            ".mkv": "video",
            ".vtt": "vtt",
            ".xml": "xml",
            ".asciidoc": "asciidoc",
            ".adoc": "asciidoc",
            ".json": "json",
            ".odt": "odt",
            ".ods": "ods",
            ".odp": "odp",
            ".epub": "epub",
            ".tex": "latex",
            ".latex": "latex",
            ".eml": "email",
            ".msg": "email",
            ".dclx": "dclx",
            ".doc": "doc",
            ".ppt": "ppt",
            ".xls": "xls",
            ".txt": "text",
        }
        return format_map.get(ext)


# Singleton instance
converter_service = ConverterService()


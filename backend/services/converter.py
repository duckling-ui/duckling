"""Docling document converter service with async job processing."""

import uuid
import threading
import json
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
    TableStructureOptions,
    TableFormerMode,
    AcceleratorOptions,
    AcceleratorDevice,
)

try:
    from docling.chunking import HybridChunker
    CHUNKING_AVAILABLE = True
except ImportError:
    CHUNKING_AVAILABLE = False

from config import OUTPUT_FOLDER, DEFAULT_CONVERSION_SETTINGS


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
        force_full_page_ocr = ocr_settings.get("force_full_page_ocr", False)
        bitmap_area_threshold = ocr_settings.get("bitmap_area_threshold", 0.05)

        print(f"[OCR] Configuring OCR backend: {backend}, language: {language}, force_full_page: {force_full_page_ocr}")

        # Map language code
        easyocr_lang = EASYOCR_LANGUAGE_MAP.get(language, "en")

        try:
            if backend == "easyocr":
                print(f"[OCR] Creating EasyOCR options with lang={easyocr_lang}")
                return EasyOcrOptions(
                    lang=[easyocr_lang],
                    force_full_page_ocr=force_full_page_ocr,
                    use_gpu=ocr_settings.get("use_gpu", False),
                    confidence_threshold=ocr_settings.get("confidence_threshold", 0.5),
                    bitmap_area_threshold=bitmap_area_threshold,
                )
            elif backend == "tesseract":
                print(f"[OCR] Creating Tesseract options with lang={language}")
                return TesseractOcrOptions(
                    lang=[language],  # Tesseract uses standard language codes
                    force_full_page_ocr=force_full_page_ocr,
                    bitmap_area_threshold=bitmap_area_threshold,
                )
            elif backend == "ocrmac":
                print(f"[OCR] Creating OcrMac options with lang={language}")
                return OcrMacOptions(
                    lang=[language],
                    force_full_page_ocr=force_full_page_ocr,
                    bitmap_area_threshold=bitmap_area_threshold,
                )
            elif backend == "rapidocr":
                print(f"[OCR] Creating RapidOCR options with lang={language}")
                return RapidOcrOptions(
                    lang=[language],
                    force_full_page_ocr=force_full_page_ocr,
                    bitmap_area_threshold=bitmap_area_threshold,
                )
            else:
                # Default to EasyOCR
                print(f"[OCR] Unknown backend '{backend}', defaulting to EasyOCR")
                return EasyOcrOptions(
                    lang=[easyocr_lang],
                    force_full_page_ocr=force_full_page_ocr,
                    use_gpu=False,
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

        ocr_enabled = ocr_settings.get("enabled", True)
        table_enabled = table_settings.get("enabled", True)

        # Create a settings hash for caching
        settings_key = json.dumps(settings, sort_keys=True)
        settings_hash = hash(settings_key)

        if settings_hash in self._converters:
            return self._converters[settings_hash]

        # Build pipeline options
        pipeline_options = PdfPipelineOptions(
            do_ocr=ocr_enabled,
            do_table_structure=table_enabled,
            generate_page_images=image_settings.get("generate_page_images", False),
            generate_picture_images=image_settings.get("generate_picture_images", True),
            generate_table_images=image_settings.get("generate_table_images", True),
            images_scale=image_settings.get("images_scale", 1.0),
            accelerator_options=self._get_accelerator_options(settings),
        )

        # Set document timeout if specified
        timeout = perf_settings.get("document_timeout")
        if timeout:
            pipeline_options.document_timeout = float(timeout)

        # Configure OCR options if enabled
        if ocr_enabled:
            print(f"[converter] OCR is enabled, configuring OCR options...")
            pipeline_options.ocr_options = self._get_ocr_options(settings)
            print(f"[converter] OCR options configured: {type(pipeline_options.ocr_options).__name__}")
        else:
            print(f"[converter] OCR is disabled")

        # Configure table structure options
        if table_enabled:
            pipeline_options.table_structure_options = self._get_table_options(settings)

        # Create format options for PDF and images (both use OCR)
        pdf_format_option = PdfFormatOption(
            pipeline_options=pipeline_options,
        )

        image_format_option = ImageFormatOption(
            pipeline_options=pipeline_options,
        )

        print(f"[converter] Creating DocumentConverter...")

        # Create converter with format options for all supported formats
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_format_option,
                InputFormat.IMAGE: image_format_option,
            }
        )

        print(f"[converter] DocumentConverter created successfully")

        # Cache the converter
        self._converters[settings_hash] = converter

        return converter

    @property
    def converter(self) -> DocumentConverter:
        """Lazy initialization of default DocumentConverter."""
        if self._default_converter is None:
            self._default_converter = self._get_converter()
        return self._default_converter

    def create_job(self, input_path: str, original_filename: str, settings: Dict[str, Any] = None) -> ConversionJob:
        """Create a new conversion job."""
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

    def start_conversion(self, job: ConversionJob, on_complete: Callable = None):
        """Queue a job for async conversion."""
        # Ensure worker is running
        self._start_worker()

        # Add job to queue
        ConverterService._job_queue.put((job, on_complete))
        job.message = f"Queued for processing (position: {ConverterService._job_queue.qsize()})"

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
            max_tokens = chunking_settings.get("max_tokens", 512)
            merge_peers = chunking_settings.get("merge_peers", True)

            chunker = HybridChunker(
                merge_peers=merge_peers,
            )

            for i, chunk in enumerate(chunker.chunk(doc)):
                chunk_data = {
                    "id": i + 1,
                    "text": chunk.text,
                    "meta": {}
                }

                if hasattr(chunk, 'meta'):
                    # Extract relevant metadata
                    if hasattr(chunk.meta, 'headings'):
                        chunk_data["meta"]["headings"] = chunk.meta.headings
                    if hasattr(chunk.meta, 'page'):
                        chunk_data["meta"]["page"] = chunk.meta.page

                chunks.append(chunk_data)
        except Exception as e:
            print(f"Error generating chunks: {e}")

        return chunks

    def _run_conversion(self, job: ConversionJob, on_complete: Callable = None):
        """Run the actual conversion process."""
        try:
            job.status = ConversionStatus.PROCESSING
            job.progress = 10
            job.message = "Starting document conversion..."

            # Check if OCR is enabled for status message
            ocr_enabled = job.settings.get("ocr", {}).get("enabled", True)
            ocr_language = job.settings.get("ocr", {}).get("language", "en")
            ocr_backend = job.settings.get("ocr", {}).get("backend", "easyocr")

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
                        result = converter.convert(job.input_path)
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
                    job.extracted_images = self._extract_images(doc, output_base, job)

                # Extract tables
                table_settings = job.settings.get("tables", {})
                if table_settings.get("enabled", True):
                    job.extracted_tables = self._extract_tables(doc, output_base, job)

                job.progress = 70
                job.message = "Generating output formats..."

                # Export to different formats
                # Markdown
                md_path = output_base / f"{Path(job.original_filename).stem}.md"
                md_content = doc.export_to_markdown()
                md_path.write_text(md_content, encoding="utf-8")
                job.output_paths["markdown"] = str(md_path)

                job.progress = 75

                # HTML
                try:
                    html_path = output_base / f"{Path(job.original_filename).stem}.html"
                    html_content = doc.export_to_html()
                    html_path.write_text(html_content, encoding="utf-8")
                    job.output_paths["html"] = str(html_path)
                except Exception as e:
                    print(f"HTML export failed: {e}")

                job.progress = 80

                # JSON (full document structure)
                try:
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
                    txt_path = output_base / f"{Path(job.original_filename).stem}.txt"
                    txt_content = doc.export_to_text()
                    txt_path.write_text(txt_content, encoding="utf-8")
                    job.output_paths["text"] = str(txt_path)
                except Exception as e:
                    print(f"Text export failed: {e}")

                # DocTags
                try:
                    doctags_path = output_base / f"{Path(job.original_filename).stem}.doctags"
                    doctags_content = doc.export_to_doctags()
                    doctags_path.write_text(str(doctags_content), encoding="utf-8")
                    job.output_paths["doctags"] = str(doctags_path)
                except Exception as e:
                    print(f"DocTags export failed: {e}")

                # Document tokens
                try:
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
                if job.chunks:
                    chunks_path = output_base / f"{Path(job.original_filename).stem}.chunks.json"
                    with open(chunks_path, 'w', encoding='utf-8') as f:
                        json.dump(job.chunks, f, indent=2)
                    job.output_paths["chunks"] = str(chunks_path)

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
        if not job or job.status != ConversionStatus.COMPLETED:
            return None

        output_path = job.output_paths.get(format_type)
        if not output_path:
            return None

        path = Path(output_path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def get_output_path(self, job_id: str, format_type: str) -> Optional[Path]:
        """Get the output file path for a specific format."""
        job = self.get_job(job_id)
        if not job or job.status != ConversionStatus.COMPLETED:
            return None

        output_path = job.output_paths.get(format_type)
        if not output_path:
            return None

        path = Path(output_path)
        if path.exists():
            return path
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
        job = self._jobs.pop(job_id, None)
        if job:
            # Clean up output files
            output_base = OUTPUT_FOLDER / job_id
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
            ".vtt": "vtt",
            ".xml": "xml",
            ".asciidoc": "asciidoc",
            ".adoc": "asciidoc",
            ".json": "json"
        }
        return format_map.get(ext)


# Singleton instance
converter_service = ConverterService()


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

"""Conversion history service with CRUD operations."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import desc

from models.database import db, Conversion, get_db_session


class HistoryService:
    """Service for managing conversion history."""

    def create_entry(
        self,
        job_id: str,
        filename: str,
        original_filename: str,
        input_format: str = None,
        settings: Dict[str, Any] = None,
        file_size: float = None,
        source_type: str = None,
    ) -> Dict[str, Any]:
        """
        Create a new history entry.

        Args:
            job_id: Unique job identifier
            filename: Stored filename
            original_filename: Original uploaded filename
            input_format: Detected input format
            settings: Conversion settings used
            file_size: File size in bytes
            source_type: How the document was submitted (upload, url, batch)

        Returns:
            Dictionary representation of the created entry
        """
        with get_db_session() as session:
            entry = Conversion(
                id=job_id,
                filename=filename,
                original_filename=original_filename,
                input_format=input_format,
                status="pending",
                settings=json.dumps(settings) if settings else None,
                file_size=file_size,
                source_type=source_type,
            )
            session.add(entry)
            session.commit()

            # Refresh to get the committed state and convert to dict before session closes
            session.refresh(entry)
            return entry.to_dict()

    def update_status(
        self,
        job_id: str,
        status: str,
        confidence: float = None,
        error_message: str = None,
        output_path: str = None,
        processing_duration_seconds: float = None,
        ocr_backend_used: str = None,
        page_count: int = None,
        cpu_usage_avg_during_conversion: float = None,
        performance_device_used: str = None,
        images_classify_enabled: bool = None,
        content_hash: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update the status of a conversion entry.

        Args:
            job_id: Job identifier
            status: New status
            confidence: Conversion confidence score
            error_message: Error message if failed
            output_path: Path to output files
            processing_duration_seconds: Duration of conversion in seconds
            ocr_backend_used: OCR backend that was used (or "none" if fallback)
            page_count: Number of pages in the document
            cpu_usage_avg_during_conversion: Average CPU % during conversion
            performance_device_used: Device used (cpu, cuda, mps, auto)
            images_classify_enabled: Whether image classification was enabled
            content_hash: Content-addressed dedup hash (for cache hits)

        Returns:
            Dictionary representation of updated entry or None if not found
        """
        with get_db_session() as session:
            entry = session.query(Conversion).filter_by(id=job_id).first()
            if not entry:
                return None

            entry.status = status
            if confidence is not None:
                entry.confidence = confidence
            if error_message:
                entry.error_message = error_message
            if output_path:
                entry.output_path = output_path
            if processing_duration_seconds is not None:
                entry.processing_duration_seconds = processing_duration_seconds
            if ocr_backend_used is not None:
                entry.ocr_backend_used = ocr_backend_used
            if page_count is not None:
                entry.page_count = page_count
            if cpu_usage_avg_during_conversion is not None:
                entry.cpu_usage_avg_during_conversion = cpu_usage_avg_during_conversion
            if performance_device_used is not None:
                entry.performance_device_used = performance_device_used
            if images_classify_enabled is not None:
                entry.images_classify_enabled = "true" if images_classify_enabled else "false"
            if content_hash is not None:
                entry.content_hash = content_hash

            if status in ["completed", "failed"]:
                entry.completed_at = datetime.utcnow()

            session.commit()
            session.refresh(entry)
            return entry.to_dict()

    def get_entry(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single history entry by ID.

        Args:
            job_id: Job identifier

        Returns:
            Dictionary representation of the entry or None
        """
        with get_db_session() as session:
            entry = session.query(Conversion).filter_by(id=job_id).first()
            if entry:
                return entry.to_dict()
            return None

    def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get all history entries with optional filtering.

        Args:
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            status: Filter by status

        Returns:
            List of entry dictionaries
        """
        with get_db_session() as session:
            query = session.query(Conversion)

            if status:
                query = query.filter_by(status=status)

            entries = query.order_by(desc(Conversion.created_at)).offset(offset).limit(limit).all()
            return [entry.to_dict() for entry in entries]

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent history entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of entry dictionaries
        """
        return self.get_all(limit=limit)

    def delete_entry(self, job_id: str) -> bool:
        """
        Delete a history entry.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted, False if not found
        """
        with get_db_session() as session:
            entry = session.query(Conversion).filter_by(id=job_id).first()
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False

    def delete_all(self) -> int:
        """
        Delete all history entries.

        Returns:
            Number of entries deleted
        """
        with get_db_session() as session:
            count = session.query(Conversion).delete()
            session.commit()
            return count

    def _parse_settings(self, settings_json: Optional[str]) -> Dict[str, Any]:
        """Safely parse settings JSON. Returns empty dict on error."""
        if not settings_json:
            return {}
        try:
            return json.loads(settings_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _categorize_error(self, error_message: Optional[str]) -> str:
        """Categorize error message for error_category_breakdown."""
        if not error_message:
            return "unknown"
        err_lower = error_message.lower()
        if any(x in err_lower for x in ["ocr", "easyocr", "tesseract", "ocrmac", "rapidocr", "cuda", "gpu"]):
            return "ocr"
        if any(x in err_lower for x in ["timeout", "timed out"]):
            return "timeout"
        if any(x in err_lower for x in ["memory", "oom"]):
            return "memory"
        if any(x in err_lower for x in ["not found", "no such file", "file not found"]):
            return "file_not_found"
        return "other"

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about conversion history.

        Returns:
            Dictionary with statistics including extended metrics
        """
        with get_db_session() as session:
            total = session.query(Conversion).count()
            completed = session.query(Conversion).filter_by(status="completed").count()
            failed = session.query(Conversion).filter_by(status="failed").count()
            pending = session.query(Conversion).filter_by(status="pending").count()
            processing = session.query(Conversion).filter_by(status="processing").count()

            # Get format breakdown
            format_counts = {}
            entries = session.query(Conversion.input_format).all()
            for (fmt,) in entries:
                if fmt:
                    format_counts[fmt] = format_counts.get(fmt, 0) + 1

            # Extended stats from all entries
            all_entries = session.query(Conversion).all()
            durations = []
            ocr_backend_counts: Dict[str, int] = {}
            output_format_counts: Dict[str, int] = {}
            performance_device_counts: Dict[str, int] = {}
            source_type_counts: Dict[str, int] = {}
            chunking_enabled_count = 0
            error_category_counts: Dict[str, int] = {}

            for entry in all_entries:
                settings = self._parse_settings(entry.settings)

                # Processing duration: prefer stored column, else compute from timestamps
                if entry.status in ("completed", "failed"):
                    if getattr(entry, "processing_duration_seconds", None) is not None:
                        durations.append(entry.processing_duration_seconds)
                    elif entry.completed_at and entry.created_at:
                        delta = entry.completed_at - entry.created_at
                        durations.append(delta.total_seconds())

                # OCR backend: prefer ocr_backend_used column, else from settings
                ocr_backend = getattr(entry, "ocr_backend_used", None) or (settings.get("ocr") or {}).get("backend")
                if ocr_backend:
                    ocr_backend_counts[ocr_backend] = ocr_backend_counts.get(ocr_backend, 0) + 1

                # Source type: from column
                source_type = getattr(entry, "source_type", None)
                if source_type:
                    source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

                # Output default format from settings
                output_format = (settings.get("output") or {}).get("default_format", "markdown")
                output_format_counts[output_format] = output_format_counts.get(output_format, 0) + 1

                # Performance device: prefer stored column, else from settings
                perf_device = getattr(entry, "performance_device_used", None) or (settings.get("performance") or {}).get("device", "auto")
                performance_device_counts[perf_device] = performance_device_counts.get(perf_device, 0) + 1

                # Chunking enabled
                if (settings.get("chunking") or {}).get("enabled", False):
                    chunking_enabled_count += 1

                # Error category for failed entries
                if entry.status == "failed" and entry.error_message:
                    category = self._categorize_error(entry.error_message)
                    error_category_counts[category] = error_category_counts.get(category, 0) + 1

            avg_processing_seconds = round(sum(durations) / len(durations), 1) if durations else None

            # Build pages/sec and conversion time distribution from completed entries
            # Also collect per-entry config for breakdown stats
            pages_per_sec_list = []
            completed_with_config: List[Dict[str, Any]] = []  # for breakdowns
            for entry in all_entries:
                if entry.status not in ("completed", "failed"):
                    continue
                dur = getattr(entry, "processing_duration_seconds", None)
                if dur is None and entry.completed_at and entry.created_at:
                    delta = entry.completed_at - entry.created_at
                    dur = delta.total_seconds()
                pages = getattr(entry, "page_count", None) or 0
                pps = (pages / dur) if (dur and dur > 0 and pages and pages > 0) else None
                if pps is not None:
                    pages_per_sec_list.append((entry.id, entry.created_at, pps))
                perf_device = getattr(entry, "performance_device_used", None) or (self._parse_settings(entry.settings).get("performance") or {}).get("device", "auto")
                ocr_backend = getattr(entry, "ocr_backend_used", None) or (self._parse_settings(entry.settings).get("ocr") or {}).get("backend", "none")
                img_classify = getattr(entry, "images_classify_enabled", None)
                if img_classify is None:
                    img_classify = (self._parse_settings(entry.settings).get("images") or {}).get("classify", False)
                    img_classify = "true" if img_classify else "false"
                completed_with_config.append({
                    "dur": dur, "pages": pages, "pps": pps,
                    "perf_device": perf_device, "ocr_backend": ocr_backend, "images_classify": img_classify,
                })

            avg_pages_per_second = None
            avg_pages_per_second_per_cpu = None
            conversion_time_distribution = None
            pages_per_second_over_time = []

            if pages_per_sec_list:
                pps_values = [p[2] for p in pages_per_sec_list]
                avg_pages_per_second = round(sum(pps_values) / len(pps_values), 2)
                try:
                    from utils.system_info import get_cpu_count
                    cpu_count = get_cpu_count() or 1
                    avg_pages_per_second_per_cpu = round(avg_pages_per_second / cpu_count, 2)
                except Exception:
                    avg_pages_per_second_per_cpu = avg_pages_per_second

            if durations:
                sorted_dur = sorted(durations)
                n = len(sorted_dur)

                def _percentile(arr, p):
                    if not arr:
                        return 0
                    idx = min(int(n * p / 100), n - 1)
                    return arr[idx]

                conversion_time_distribution = {
                    "p50": round(_percentile(sorted_dur, 50), 1),
                    "p95": round(_percentile(sorted_dur, 95), 1),
                    "p99": round(_percentile(sorted_dur, 99), 1),
                }

            for job_id, created_at, pps in sorted(pages_per_sec_list, key=lambda x: x[1] or datetime.min):
                pages_per_second_over_time.append({
                    "job_id": job_id,
                    "created_at": created_at.isoformat() if created_at else None,
                    "pages_per_sec": round(pps, 2),
                })

            # Breakdown stats by hardware, OCR backend, image classifier
            def _group_stats(items: List[Dict], key: str) -> Dict[str, Dict]:
                groups: Dict[str, List[Dict]] = {}
                for item in items:
                    k = item.get(key, "unknown")
                    groups.setdefault(k, []).append(item)
                result = {}
                for k, group in groups.items():
                    durs = [x["dur"] for x in group if x.get("dur")]
                    pps_vals = [x["pps"] for x in group if x.get("pps") is not None]
                    result[k] = {
                        "count": len(group),
                        "avg_processing_seconds": round(sum(durs) / len(durs), 1) if durs else None,
                        "avg_pages_per_second": round(sum(pps_vals) / len(pps_vals), 2) if pps_vals else None,
                    }
                    if durs:
                        sorted_dur = sorted(durs)
                        n = len(sorted_dur)

                        def _p(arr, pct):
                            if not arr:
                                return 0
                            idx = min(int(n * pct / 100), n - 1)
                            return arr[idx]

                        result[k]["conversion_time_p50"] = round(_p(sorted_dur, 50), 1)
                        result[k]["conversion_time_p95"] = round(_p(sorted_dur, 95), 1)
                        result[k]["conversion_time_p99"] = round(_p(sorted_dur, 99), 1)
                return result

            by_hardware = _group_stats(completed_with_config, "perf_device")
            by_ocr_backend = _group_stats(completed_with_config, "ocr_backend")
            by_images_classify = _group_stats(completed_with_config, "images_classify")

            # System info (hardware type, CPU count, current CPU % - process-specific)
            system_info = {}
            try:
                from utils.system_info import get_hardware_type, get_cpu_usage
                hw = get_hardware_type()
                system_info = {
                    "cpu_count": hw.get("cpu_count"),
                    "hardware_type": hw.get("type"),
                    "gpu_name": hw.get("gpu_name"),
                    "gpu_memory_mb": hw.get("gpu_memory_mb"),
                    "cpu_usage_current": get_cpu_usage(),
                }
            except Exception:
                pass

            result = {
                "total": total,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "processing": processing,
                "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
                "format_breakdown": format_counts,
                "avg_processing_seconds": avg_processing_seconds,
                "ocr_backend_breakdown": ocr_backend_counts,
                "output_format_breakdown": output_format_counts,
                "performance_device_breakdown": performance_device_counts,
                "chunking_enabled_count": chunking_enabled_count,
                "error_category_breakdown": error_category_counts,
                "source_type_breakdown": source_type_counts,
                "system": system_info,
                "avg_pages_per_second": avg_pages_per_second,
                "avg_pages_per_second_per_cpu": avg_pages_per_second_per_cpu,
                "conversion_time_distribution": conversion_time_distribution,
                "pages_per_second_over_time": pages_per_second_over_time,
                "by_hardware": by_hardware,
                "by_ocr_backend": by_ocr_backend,
                "by_images_classify": by_images_classify,
            }
            return result

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search history entries by filename.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching entries
        """
        # Sanitize input: limit length and escape SQL wildcards
        if not query or len(query) > 200:
            return []
        
        # Escape SQL LIKE wildcards in user input
        sanitized_query = query.replace('%', r'\%').replace('_', r'\_')
        
        with get_db_session() as session:
            entries = session.query(Conversion).filter(
                Conversion.original_filename.ilike(f"%{sanitized_query}%", escape='\\')
            ).order_by(desc(Conversion.created_at)).limit(min(limit, 100)).all()
            return [entry.to_dict() for entry in entries]

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Delete entries older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of entries deleted
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)

        with get_db_session() as session:
            count = session.query(Conversion).filter(
                Conversion.created_at < cutoff
            ).delete()
            session.commit()
            return count

    def update_document_path(self, job_id: str, document_path: str) -> Optional[Dict[str, Any]]:
        """
        Update conversion entry with document JSON path.

        Args:
            job_id: Job identifier
            document_path: Path to the stored DoclingDocument JSON file

        Returns:
            Dictionary representation of updated entry or None if not found
        """
        with get_db_session() as session:
            entry = session.query(Conversion).filter_by(id=job_id).first()
            if not entry:
                return None
            entry.document_json_path = document_path
            session.commit()
            session.refresh(entry)
            return entry.to_dict()

    def load_document(self, job_id: str):
        """
        Load DoclingDocument from stored JSON file.

        Tries, in order:
        1. Path from DB (document_json_path)
        2. *.document.json in OUTPUT_FOLDER / job_id (for entries missing DB path)

        Args:
            job_id: Job identifier

        Returns:
            DoclingDocument instance or None if not found/available
        """
        from pathlib import Path
        from config import OUTPUT_FOLDER
        from werkzeug.utils import safe_join

        try:
            from docling_core.types.doc.document import DoclingDocument
        except ImportError:
            try:
                # Fallback for different import paths
                from docling.datamodel.document import DoclingDocument
            except ImportError:
                print("[history] DoclingDocument not available")
                return None

        # Validate job_id defensively so this service method does not rely on callers.
        # Allow only alphanumerics, dash and underscore; disallow path separators and dots.
        if not isinstance(job_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", job_id):
            # In a service context, just indicate "not found"/unavailable.
            return None

        entry = self.get_entry(job_id)
        if not entry:
            return None

        output_folder_resolved = OUTPUT_FOLDER.resolve()

        def _load_from_path(doc_path: Path):
            if not doc_path.exists():
                return None
            try:
                doc_path_resolved = doc_path.resolve()
                doc_path_resolved.relative_to(output_folder_resolved)
            except ValueError:
                return None
            try:
                return DoclingDocument.load_from_json(str(doc_path_resolved))
            except Exception as e:
                err_str = str(e)
                if "incompatible with SDK schema version" in err_str or "Doc version" in err_str:
                    print(
                        f"[history] Document schema version mismatch: {e}. "
                        "Upgrade docling to load documents saved with a newer version: pip install --upgrade docling"
                    )
                else:
                    print(f"[history] Error loading document: {e}")
                return None

        # 1. Try path from DB
        stored_path = entry.get("document_json_path")
        if stored_path:
            doc = _load_from_path(Path(stored_path))
            if doc is not None:
                return doc

        # 2. Fallback: find *.document.json in output dir (handles missing DB path)
        # Construct the output directory using a safe, normalized join and
        # verify it stays under OUTPUT_FOLDER to prevent path traversal.
        joined = safe_join(str(OUTPUT_FOLDER), job_id)
        if not joined:
            return None

        output_dir = Path(joined)
        try:
            output_dir_resolved = output_dir.resolve()
            output_dir_resolved.relative_to(output_folder_resolved)
        except ValueError:
            return None

        if not output_dir_resolved.exists():
            return None

        matches = list(output_dir_resolved.glob("*.document.json"))
        if matches:
            # Use the first match; path has already been resolved and validated.
            match_path_resolved = matches[0].resolve()
            doc = _load_from_path(match_path_resolved)
            if doc is not None:
                # Backfill DB so future loads use document_json_path
                self.update_document_path(job_id, str(match_path_resolved))
                return doc
        return None

    def create_entry_from_disk(
        self,
        job_id: str,
        filename: str,
        original_filename: str,
        output_path: str,
        document_json_path: str = None,
        input_format: str = None,
        file_size: float = None,
        created_at: datetime = None,
        completed_at: datetime = None,
        settings: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Create a history entry for a conversion that exists on disk but not in DB.

        Used by reconcile_from_disk() to restore entries after DB loss.

        Args:
            job_id: Unique job identifier (directory name)
            filename: Stored filename
            original_filename: Original uploaded filename
            output_path: Path to primary output file (e.g. .md)
            document_json_path: Path to DoclingDocument JSON if present
            input_format: Detected input format (optional)
            file_size: File size in bytes (optional)
            created_at: Override for created_at (default: now)
            completed_at: Override for completed_at (default: now)
            settings: Conversion settings (optional)

        Returns:
            Dictionary representation of the created entry
        """
        with get_db_session() as session:
            entry = Conversion(
                id=job_id,
                filename=filename,
                original_filename=original_filename,
                input_format=input_format,
                status="completed",
                confidence=None,
                created_at=created_at or datetime.utcnow(),
                completed_at=completed_at or datetime.utcnow(),
                settings=json.dumps(settings) if settings else None,
                error_message=None,
                output_path=output_path,
                file_size=file_size,
                document_json_path=document_json_path,
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry.to_dict()

    def reconcile_from_disk(self) -> Tuple[int, List[str]]:
        """
        Scan output directory for conversions that exist on disk but not in DB,
        and create missing history entries.

        Returns:
            Tuple of (count of entries added, list of job_ids added)
        """
        from config import OUTPUT_FOLDER

        # UUID pattern: 8-4-4-4-12 hex
        uuid_re = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )

        output_folder = Path(OUTPUT_FOLDER)
        if not output_folder.exists():
            return 0, []

        output_folder_resolved = output_folder.resolve()
        added: List[str] = []
        added_count = 0

        for dir_path in output_folder.iterdir():
            if not dir_path.is_dir():
                continue

            job_id = dir_path.name

            # Security: validate job_id
            if ".." in job_id or "/" in job_id or "\\" in job_id:
                continue
            if not uuid_re.match(job_id):
                continue

            # Ensure path is within OUTPUT_FOLDER
            try:
                dir_resolved = dir_path.resolve()
                dir_resolved.relative_to(output_folder_resolved)
            except ValueError:
                continue

            # Skip if already in DB
            if self.get_entry(job_id):
                continue

            # Find output files to infer original_filename and paths
            md_files = list(dir_path.glob("*.md"))
            doc_files = list(dir_path.glob("*.document.json"))
            html_files = list(dir_path.glob("*.html"))
            json_files = list(dir_path.glob("*.json"))

            # Require at least one substantial output (exclude .document.json for "has output" check)
            has_output = bool(
                md_files
                or html_files
                or [f for f in json_files if not f.name.endswith(".document.json")]
            )
            if not has_output and not doc_files:
                continue

            # Infer stem from first available output file
            stem = None
            output_path_str = None
            for files in (md_files, html_files, doc_files, json_files):
                if files:
                    first = files[0]
                    stem = first.stem
                    output_path_str = str(first.resolve())
                    break

            if stem is None or output_path_str is None:
                continue

            # original_filename: use stem + generic extension (we don't know original format)
            original_filename = f"{stem}.doc"

            # document_json_path if present
            doc_path_str = None
            if doc_files:
                doc_path_str = str(doc_files[0].resolve())

            # Use directory mtime for created_at/completed_at
            try:
                mtime = dir_path.stat().st_mtime
                dt = datetime.utcfromtimestamp(mtime)
            except Exception:
                dt = datetime.utcnow()

            try:
                self.create_entry_from_disk(
                    job_id=job_id,
                    filename=original_filename,
                    original_filename=original_filename,
                    output_path=output_path_str,
                    document_json_path=doc_path_str,
                    input_format=None,
                    file_size=None,
                    created_at=dt,
                    completed_at=dt,
                    settings=None,
                )
                added.append(job_id)
                added_count += 1
            except Exception as e:
                print(f"[history] Failed to reconcile {job_id}: {e}")

        return added_count, added

# Singleton instance
history_service = HistoryService()


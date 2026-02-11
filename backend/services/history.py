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
        file_size: float = None
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
                file_size=file_size
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
        output_path: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update the status of a conversion entry.

        Args:
            job_id: Job identifier
            status: New status
            confidence: Conversion confidence score
            error_message: Error message if failed
            output_path: Path to output files

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

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about conversion history.

        Returns:
            Dictionary with statistics
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

            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "processing": processing,
                "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
                "format_breakdown": format_counts
            }

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
        try:
            from docling_core.types.doc.document import DoclingDocument
        except ImportError:
            try:
                # Fallback for different import paths
                from docling.datamodel.document import DoclingDocument
            except ImportError:
                print("[history] DoclingDocument not available")
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
                print(f"[history] Error loading document: {e}")
                return None

        # 1. Try path from DB
        stored_path = entry.get("document_json_path")
        if stored_path:
            doc = _load_from_path(Path(stored_path))
            if doc is not None:
                return doc

        # 2. Fallback: find *.document.json in output dir (handles missing DB path)
        output_dir = OUTPUT_FOLDER / job_id
        if not output_dir.exists():
            return None
        try:
            output_dir_resolved = output_dir.resolve()
            output_dir_resolved.relative_to(output_folder_resolved)
        except ValueError:
            return None
        matches = list(output_dir.glob("*.document.json"))
        if matches:
            doc = _load_from_path(matches[0])
            if doc is not None:
                # Backfill DB so future loads use document_json_path
                self.update_document_path(job_id, str(matches[0].resolve()))
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


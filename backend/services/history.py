"""Conversion history service with CRUD operations."""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
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
        with get_db_session() as session:
            entries = session.query(Conversion).filter(
                Conversion.original_filename.ilike(f"%{query}%")
            ).order_by(desc(Conversion.created_at)).limit(limit).all()
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


# Singleton instance
history_service = HistoryService()


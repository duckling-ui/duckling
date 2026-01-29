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

"""File upload and download management service."""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from config import UPLOAD_FOLDER, OUTPUT_FOLDER, Config


class FileManager:
    """Service for handling file uploads and downloads."""

    def __init__(self, upload_folder: str = None, output_folder: str = None):
        """Initialize the file manager."""
        self.upload_folder = Path(upload_folder or UPLOAD_FOLDER)
        self.output_folder = Path(output_folder or OUTPUT_FOLDER)

        # Ensure directories exist
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def allowed_file(self, filename: str) -> bool:
        """Check if a file extension is allowed."""
        if "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in Config.ALLOWED_EXTENSIONS

    def save_upload(self, file, original_filename: str = None) -> Tuple[str, str, int]:
        """
        Save an uploaded file.

        Args:
            file: File object from Flask request
            original_filename: Original filename (optional, will use file.filename if not provided)

        Returns:
            Tuple of (saved_path, secure_filename, file_size)
        """
        if original_filename is None:
            original_filename = file.filename

        # Secure the filename
        safe_filename = secure_filename(original_filename)
        if not safe_filename:
            safe_filename = "unnamed_file"

        # Generate unique filename to avoid collisions
        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(safe_filename)
        # Normalize extension to lowercase for Docling compatibility
        ext = ext.lower()
        unique_filename = f"{name}_{unique_id}{ext}"

        # Save the file
        save_path = self.upload_folder / unique_filename
        file.save(str(save_path))

        # Get file size
        file_size = save_path.stat().st_size

        return str(save_path), safe_filename, file_size

    def save_upload_from_bytes(self, content: bytes, filename: str) -> Tuple[str, str, int]:
        """
        Save uploaded content from bytes.

        Args:
            content: File content as bytes
            filename: Original filename

        Returns:
            Tuple of (saved_path, secure_filename, file_size)
        """
        safe_filename = secure_filename(filename)
        if not safe_filename:
            safe_filename = "unnamed_file"

        unique_id = str(uuid.uuid4())[:8]
        name, ext = os.path.splitext(safe_filename)
        # Normalize extension to lowercase for Docling compatibility
        ext = ext.lower()
        unique_filename = f"{name}_{unique_id}{ext}"

        save_path = self.upload_folder / unique_filename
        save_path.write_bytes(content)

        file_size = len(content)

        return str(save_path), safe_filename, file_size

    def get_upload_path(self, filename: str) -> Optional[Path]:
        """Get the full path for an uploaded file."""
        path = self.upload_folder / filename
        if path.exists():
            return path
        return None

    def get_output_path(self, job_id: str, format_type: str, original_filename: str) -> Optional[Path]:
        """Get the output file path for a conversion job."""
        output_dir = self.output_folder / job_id
        if not output_dir.exists():
            return None

        # Determine extension based on format
        ext_map = {
            "markdown": ".md",
            "html": ".html",
            "json": ".json",
            "doctags": ".doctags",
            "text": ".txt"
        }

        ext = ext_map.get(format_type, ".md")
        stem = Path(original_filename).stem
        output_path = output_dir / f"{stem}{ext}"

        if output_path.exists():
            return output_path
        return None

    def delete_upload(self, filepath: str) -> bool:
        """Delete an uploaded file."""
        try:
            path = Path(filepath)
            if path.exists() and str(path).startswith(str(self.upload_folder)):
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def delete_output_folder(self, job_id: str) -> bool:
        """Delete the output folder for a job."""
        try:
            output_dir = self.output_folder / job_id
            if output_dir.exists():
                shutil.rmtree(output_dir)
                return True
        except Exception:
            pass
        return False

    def cleanup_old_files(self, max_age_hours: int = 24) -> Tuple[int, int]:
        """
        Clean up files older than the specified age.

        Args:
            max_age_hours: Maximum age in hours before files are deleted

        Returns:
            Tuple of (uploads_deleted, outputs_deleted)
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        uploads_deleted = 0
        outputs_deleted = 0

        # Clean uploads
        for file_path in self.upload_folder.iterdir():
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        file_path.unlink()
                        uploads_deleted += 1
                    except Exception:
                        pass

        # Clean output directories
        for dir_path in self.output_folder.iterdir():
            if dir_path.is_dir():
                mtime = datetime.fromtimestamp(dir_path.stat().st_mtime)
                if mtime < cutoff:
                    try:
                        shutil.rmtree(dir_path)
                        outputs_deleted += 1
                    except Exception:
                        pass

        return uploads_deleted, outputs_deleted

    def get_file_info(self, filepath: str) -> Optional[dict]:
        """Get information about a file."""
        path = Path(filepath)
        if not path.exists():
            return None

        stat = path.stat()
        return {
            "filename": path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": path.suffix.lower()
        }

    def list_uploads(self) -> List[dict]:
        """List all uploaded files."""
        files = []
        for file_path in self.upload_folder.iterdir():
            if file_path.is_file():
                info = self.get_file_info(str(file_path))
                if info:
                    files.append(info)
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        upload_size = sum(f.stat().st_size for f in self.upload_folder.iterdir() if f.is_file())
        upload_count = sum(1 for f in self.upload_folder.iterdir() if f.is_file())

        output_size = 0
        output_count = 0
        for dir_path in self.output_folder.iterdir():
            if dir_path.is_dir():
                output_count += 1
                for f in dir_path.iterdir():
                    if f.is_file():
                        output_size += f.stat().st_size

        return {
            "uploads": {
                "count": upload_count,
                "size_bytes": upload_size,
                "size_mb": round(upload_size / (1024 * 1024), 2)
            },
            "outputs": {
                "count": output_count,
                "size_bytes": output_size,
                "size_mb": round(output_size / (1024 * 1024), 2)
            },
            "total_size_mb": round((upload_size + output_size) / (1024 * 1024), 2)
        }


# Singleton instance
file_manager = FileManager()


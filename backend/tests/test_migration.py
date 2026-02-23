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

"""Tests for database migration scripts."""

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys
import importlib.util

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    cursor.execute("PRAGMA table_info(conversions)")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns


class TestMigrationScript:
    """Tests for migration script."""

    def test_migration_adds_column(self):
        """Test that migration adds document_json_path column."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            # Create table without the new column
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    input_format VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'pending',
                    confidence FLOAT,
                    created_at DATETIME,
                    completed_at DATETIME,
                    settings TEXT,
                    error_message TEXT,
                    output_path VARCHAR(500),
                    file_size FLOAT
                )
            """)
            conn.commit()
            conn.close()

            # Verify column doesn't exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            assert not check_column_exists(cursor, "conversions", "document_json_path")
            conn.close()

            # Run migration by importing and executing the function
            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location("migrate_add_document_path", scripts_dir / "migrate_add_document_path.py")
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)
            
            # Temporarily override DATABASE_PATH
            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)
            
            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

            # Verify column was added
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            assert check_column_exists(cursor, "conversions", "document_json_path")
            conn.close()

        finally:
            # Cleanup
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_migration_idempotent(self):
        """Test that migration can be run multiple times safely."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            # Create table with the column already present
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    document_json_path VARCHAR(500)
                )
            """)
            conn.commit()
            conn.close()

            # Run migration (should detect column exists)
            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location("migrate_add_document_path", scripts_dir / "migrate_add_document_path.py")
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)
            
            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)
            
            try:
                result = migrate_module.migrate_database()
                assert result == 0  # Should succeed without error
            finally:
                migrate_module.DATABASE_PATH = original_path

        finally:
            # Cleanup
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_migration_nonexistent_database(self):
        """Test migration handles non-existent database gracefully."""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        spec = importlib.util.spec_from_file_location("migrate_add_document_path", scripts_dir / "migrate_add_document_path.py")
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)
        
        original_path = migrate_module.DATABASE_PATH
        migrate_module.DATABASE_PATH = Path("/nonexistent/path/history.db")
        
        try:
            result = migrate_module.migrate_database()
            assert result == 0  # Should handle gracefully
        finally:
            migrate_module.DATABASE_PATH = original_path


class TestStatsColumnsMigration:
    """Tests for migrate_add_stats_columns script."""

    def test_migration_adds_stats_columns(self):
        """Test that migration adds stats columns."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    document_json_path VARCHAR(500)
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_stats_columns",
                scripts_dir / "migrate_add_stats_columns.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for col in ("processing_duration_seconds", "ocr_backend_used", "page_count", "source_type"):
                assert check_column_exists(cursor, "conversions", col), f"Column {col} should exist"
            conn.close()

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_stats_migration_idempotent(self):
        """Test stats migration can be run multiple times safely."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    processing_duration_seconds REAL,
                    ocr_backend_used VARCHAR(50),
                    page_count INTEGER,
                    source_type VARCHAR(20)
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_stats_columns",
                scripts_dir / "migrate_add_stats_columns.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()


class TestCpuUsageColumnMigration:
    """Tests for migrate_add_cpu_usage_column script."""

    def test_migration_adds_cpu_usage_column(self):
        """Test that migration adds cpu_usage_avg_during_conversion column."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_cpu_usage_column",
                scripts_dir / "migrate_add_cpu_usage_column.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            assert check_column_exists(
                cursor, "conversions", "cpu_usage_avg_during_conversion"
            ), "Column cpu_usage_avg_during_conversion should exist"
            conn.close()

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_cpu_usage_migration_idempotent(self):
        """Test cpu usage migration can be run multiple times safely."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    cpu_usage_avg_during_conversion REAL
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_cpu_usage_column",
                scripts_dir / "migrate_add_cpu_usage_column.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()


class TestConfigColumnsMigration:
    """Tests for migrate_add_config_columns script."""

    def test_migration_adds_config_columns(self):
        """Test that migration adds performance_device_used and images_classify_enabled."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_config_columns",
                scripts_dir / "migrate_add_config_columns.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for col in ("performance_device_used", "images_classify_enabled"):
                assert check_column_exists(
                    cursor, "conversions", col
                ), f"Column {col} should exist"
            conn.close()

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()


class TestContentHashColumnMigration:
    """Tests for migrate_add_content_hash script."""

    def test_migration_adds_content_hash_column(self):
        """Test that migration adds content_hash column."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_content_hash",
                scripts_dir / "migrate_add_content_hash.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            assert check_column_exists(
                cursor, "conversions", "content_hash"
            ), "Column content_hash should exist"
            conn.close()

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_content_hash_migration_idempotent(self):
        """Test content_hash migration can be run multiple times safely."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE conversions (
                    id VARCHAR(36) PRIMARY KEY,
                    content_hash VARCHAR(64)
                )
            """)
            conn.commit()
            conn.close()

            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            spec = importlib.util.spec_from_file_location(
                "migrate_add_content_hash",
                scripts_dir / "migrate_add_content_hash.py",
            )
            migrate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migrate_module)

            original_path = migrate_module.DATABASE_PATH
            migrate_module.DATABASE_PATH = Path(db_path)

            try:
                result = migrate_module.migrate_database()
                assert result == 0
            finally:
                migrate_module.DATABASE_PATH = original_path

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

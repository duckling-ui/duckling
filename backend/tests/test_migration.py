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

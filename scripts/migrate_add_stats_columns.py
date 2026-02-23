#!/usr/bin/env python3
"""
The MIT License (MIT)

Copyright (c) 2022-present David G. Simmons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Database migration script to add stats columns to conversions table.

Adds: processing_duration_seconds, ocr_backend_used, page_count, source_type.

Usage:
    python scripts/migrate_add_stats_columns.py

The script is idempotent and can be run multiple times safely.
"""

import sqlite3
import sys
from pathlib import Path

# Add backend directory to path to import config
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from config import DATABASE_PATH
except ImportError:
    DATABASE_PATH = backend_dir / "history.db"

COLUMNS_TO_ADD = [
    ("processing_duration_seconds", "REAL"),
    ("ocr_backend_used", "VARCHAR(50)"),
    ("page_count", "INTEGER"),
    ("source_type", "VARCHAR(20)"),
]


def check_column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    cursor.execute("PRAGMA table_info(conversions)")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns


def migrate_database():
    """Add stats columns to conversions table if they don't exist."""
    db_path = DATABASE_PATH

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("Database will be created automatically on first run with the new schema.")
        return 0

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        added = 0

        for column_name, column_type in COLUMNS_TO_ADD:
            if check_column_exists(cursor, "conversions", column_name):
                print(f"Column '{column_name}' already exists. Skipping.")
                continue

            print(f"Adding '{column_name}' column to conversions table...")
            cursor.execute(
                f"ALTER TABLE conversions ADD COLUMN {column_name} {column_type}"
            )
            conn.commit()
            if check_column_exists(cursor, "conversions", column_name):
                print(f"  Successfully added '{column_name}'.")
                added += 1
            else:
                print(f"  Error: Column '{column_name}' was not added successfully.")
                conn.close()
                return 1

        conn.close()
        if added > 0:
            print(f"Migration complete. Added {added} column(s).")
        return 0

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn is not None:
            conn.rollback()
            conn.close()
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        if conn is not None:
            conn.close()
        return 1


def main():
    """Main entry point."""
    print("=" * 60)
    print("Database Migration: Add stats columns to conversions")
    print("=" * 60)
    print(f"Database path: {DATABASE_PATH}")
    print()

    exit_code = migrate_database()

    print()
    if exit_code == 0:
        print("Migration completed successfully.")
    else:
        print("Migration failed. Please check the error messages above.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

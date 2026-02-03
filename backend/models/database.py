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

"""SQLite database models for conversion history."""

import json
import threading
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from config import DATABASE_URL

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
session_factory = sessionmaker(bind=engine)
db = scoped_session(session_factory)

# Lock for database initialization
_init_lock = threading.Lock()
_initialized = False

Base = declarative_base()


class Conversion(Base):
    """Model for storing conversion history."""

    __tablename__ = "conversions"

    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    input_format = Column(String(50))
    status = Column(String(20), default="pending")
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    settings = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    output_path = Column(String(500), nullable=True)
    file_size = Column(Float, nullable=True)  # Size in bytes

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "input_format": self.input_format,
            "status": self.status,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "settings": json.loads(self.settings) if self.settings else None,
            "error_message": self.error_message,
            "output_path": self.output_path,
            "file_size": self.file_size
        }

    def set_settings(self, settings_dict):
        """Set settings from dictionary."""
        self.settings = json.dumps(settings_dict)

    def get_settings(self):
        """Get settings as dictionary."""
        return json.loads(self.settings) if self.settings else {}

    def __repr__(self):
        return f"<Conversion {self.id}: {self.filename} ({self.status})>"


class UserSettings(Base):
    """Model for storing user-specific settings per session."""

    __tablename__ = "user_settings"

    session_id = Column(String(255), primary_key=True)
    settings = Column(Text, nullable=False)  # JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "session_id": self.session_id,
            "settings": json.loads(self.settings) if self.settings else {},
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def set_settings(self, settings_dict):
        """Set settings from dictionary."""
        self.settings = json.dumps(settings_dict)

    def get_settings(self):
        """Get settings as dictionary."""
        return json.loads(self.settings) if self.settings else {}

    def __repr__(self):
        return f"<UserSettings {self.session_id}>"


def init_db():
    """Initialize the database, creating tables if they don't exist."""
    global _initialized

    # Use lock to prevent race conditions between workers
    with _init_lock:
        if _initialized:
            return

        try:
            # create_all already uses checkfirst=True by default
            Base.metadata.create_all(engine)
            _initialized = True
        except Exception:
            # Table might already exist from another process, that's OK
            _initialized = True


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = db()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


"""SQLite database models for conversion history."""

import json
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


def init_db():
    """Initialize the database, creating tables if they don't exist."""
    Base.metadata.create_all(engine)


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


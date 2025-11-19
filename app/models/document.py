from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """Document metadata stored in PostgreSQL"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)  # doc_id
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes
    num_pages = Column(Integer)
    doc_hash = Column(String, unique=True)  # MD5 hash
    full_text = Column(Text)  # Complete extracted text
    num_chunks = Column(Integer)
    doc_metadata = Column(JSON)  # Changed from 'metadata' to 'doc_metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "num_pages": self.num_pages,
            "num_chunks": self.num_chunks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "doc_metadata": self.doc_metadata
        }
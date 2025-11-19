from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    doc_id: str
    filename: str
    num_pages: int
    num_chunks: int
    message: str

class QueryRequest(BaseModel):
    """Request for querying documents"""
    question: str = Field(..., description="User's question")
    doc_id: Optional[str] = Field(None, description="Specific document to query")
    user_id: str = Field(default="default_user", description="User identifier")

class QueryResponse(BaseModel):
    """Response for query"""
    success: bool
    answer: str
    question: str
    retrieved_chunks: Optional[List[str]] = None
    num_chunks_used: Optional[int] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    doc_id: Optional[str] = None

class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    filename: str
    num_pages: int
    num_chunks: int
    created_at: str
    file_size: Optional[int] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    databases: dict
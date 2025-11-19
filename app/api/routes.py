from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.api.schemas import (
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    DocumentInfo,
    HealthResponse
)
from app.core.rag_engine import RAGEngine
from app.database.postgres import postgres_db
from app.database.mongodb import mongodb
from app.models.document import Document
from typing import List
import os
import uuid
import shutil

router = APIRouter()
rag_engine = RAGEngine()

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "DocuChat API is running",
        "databases": {
            "postgresql": "connected",
            "mongodb": "connected",
            "chromadb": "connected"
        }
    }

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(default="default_user")
):
    """
    Upload a PDF document
    
    Args:
        file: PDF file to upload
        user_id: User identifier
        
    Returns:
        Upload status and document information
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Process PDF with RAG engine
        result = rag_engine.process_and_store_pdf(
            pdf_path=file_path,
            doc_id=doc_id,
            metadata={"user_id": user_id, "original_filename": file.filename}
        )
        
        if not result["success"]:
            # Clean up file if processing failed
            os.remove(file_path)
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to process PDF"))
        
        # Save to PostgreSQL
        with postgres_db.get_session() as session:
            doc = Document(
                id=doc_id,
                filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                num_pages=result["num_pages"],
                doc_hash=result.get("doc_hash"),
                full_text="",  # We could store this if needed
                num_chunks=result["num_chunks"],
                doc_metadata={"user_id": user_id}
            )
            session.add(doc)
            session.commit()
        
        return DocumentUploadResponse(
            success=True,
            doc_id=doc_id,
            filename=file.filename,
            num_pages=result["num_pages"],
            num_chunks=result["num_chunks"],
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question about uploaded documents
    
    Args:
        request: Query request with question and optional doc_id
        
    Returns:
        Answer and relevant information
    """
    try:
        # Query using RAG engine
        result = rag_engine.query(
            question=request.question,
            doc_id=request.doc_id,
            n_results=3
        )
        
        if not result["success"]:
            return QueryResponse(
                success=False,
                answer=result.get("answer", "Failed to generate answer"),
                question=request.question,
                doc_id=request.doc_id
            )
        
        # Save query to MongoDB
        query_data = {
            "user_id": request.user_id,
            "question": request.question,
            "answer": result["answer"],
            "doc_id": request.doc_id,
            "retrieved_chunks": result.get("retrieved_chunks", []),
            "model_used": result.get("model"),
            "tokens_used": result.get("tokens_used")
        }
        mongodb.save_query(query_data)
        
        return QueryResponse(
            success=True,
            answer=result["answer"],
            question=request.question,
            retrieved_chunks=result.get("retrieved_chunks"),
            num_chunks_used=result.get("num_chunks_used"),
            model=result.get("model"),
            tokens_used=result.get("tokens_used"),
            doc_id=request.doc_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(user_id: str = "default_user"):
    """
    Get list of uploaded documents
    
    Args:
        user_id: User identifier
        
    Returns:
        List of documents
    """
    try:
        with postgres_db.get_session() as session:
            documents = session.query(Document).all()
            
            return [
                DocumentInfo(
                    id=doc.id,
                    filename=doc.filename,
                    num_pages=doc.num_pages,
                    num_chunks=doc.num_chunks,
                    created_at=doc.created_at.isoformat() if doc.created_at else "",
                    file_size=doc.file_size
                )
                for doc in documents
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/history/{user_id}")
async def get_query_history(user_id: str, limit: int = 10):
    """
    Get query history for a user
    
    Args:
        user_id: User identifier
        limit: Maximum number of queries to return
        
    Returns:
        List of recent queries
    """
    try:
        queries = mongodb.get_user_queries(user_id, limit=limit)
        
        # Convert ObjectId to string for JSON serialization
        for query in queries:
            query["_id"] = str(query["_id"])
        
        return {"queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")
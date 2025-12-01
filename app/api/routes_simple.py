from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.api.schemas import (
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    HealthResponse
)
from app.core.rag_engine import RAGEngine
import os
import uuid
import shutil

router = APIRouter()
rag_engine = RAGEngine()

# Use /tmp for Railway
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory document storage
documents_store = {}

@router.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "DocuChat API is running on Railway! 🚂",
        "databases": {
            "chromadb": "connected"
        }
    }

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(default="default_user")
):
    """Upload a PDF document"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        result = rag_engine.process_and_store_pdf(
            pdf_path=file_path,
            doc_id=doc_id,
            metadata={"user_id": user_id, "original_filename": file.filename}
        )
        
        if not result["success"]:
            os.remove(file_path)
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to process PDF"))
        
        # Store in memory
        documents_store[doc_id] = {
            "id": doc_id,
            "filename": file.filename,
            "num_pages": result["num_pages"],
            "num_chunks": result["num_chunks"],
            "file_size": file_size,
            "created_at": "2025-01-14"
        }
        
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
    """Ask a question about uploaded documents"""
    try:
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

@router.get("/documents")
async def list_documents(user_id: str = "default_user"):
    """Get list of uploaded documents"""
    return list(documents_store.values())
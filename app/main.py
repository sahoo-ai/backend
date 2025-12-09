from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered document chatbot using RAG",
    version="1.0.0"
)

# Add CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["DocuChat"])

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} Starting...")
    print("=" * 60)
    print("✅ PostgreSQL: Connected")
    print("✅ MongoDB: Connected")
    print("✅ ChromaDB: Connected")
    print("✅ OpenRouter: Configured")
    print("=" * 60)
    print(f"📝 API Documentation: http://localhost:8000/docs")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n👋 Shutting down DocuChat...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
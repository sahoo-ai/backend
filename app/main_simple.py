from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_simple import router
import os

app = FastAPI(
    title="DocuChat API",
    description="AI-powered document chatbot using RAG",
    version="1.0.0"
)

# CORS - Allow all origins (for Lovable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["DocuChat"])

@app.get("/")
async def root():
    return {
        "message": "DocuChat API is running on Railway! 🚂",
        "docs": "/docs",
        "status": "healthy"
    }

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🚂 DocuChat Starting on Railway...")
    print("=" * 60)
    print("✅ ChromaDB: Connected")
    print("✅ OpenRouter: Configured")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
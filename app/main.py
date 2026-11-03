
from datetime import datetime, timezone

from fastapi import FastAPI

# Import our PDF document endpoints
from app.api.documents import router as documents_router
from app.api.search import router as search_router

app = FastAPI(
    title="AI Knowledge Assistant",
    description="A document-based AI assistant powered by RAG",
    version="0.2.0"
)

# Register document upload endpoints
app.include_router(documents_router)
app.include_router(search_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Knowledge Assistant",
        "version": "0.2.0"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Knowledge Assistant",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

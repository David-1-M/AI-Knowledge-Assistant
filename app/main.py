
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="AI Knowledge Assistant",
    description="A document-based AI assistant powered by RAG",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Knowledge Assistant",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Knowledge Assistant",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

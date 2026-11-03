
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.pdf_service import extract_pdf_text
from app.services.chunking_service import chunk_pages
from app.services.vector_service import (
    index_document,
    semantic_search
)


router = APIRouter(
    prefix="/api",
    tags=["Semantic Search"]
)

UPLOAD_DIR = Path("data/uploads")


class SearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)
    document_id: UUID | None = None


@router.post("/documents/{document_id}/index")
def index_uploaded_document(document_id: UUID):

    document_id_str = str(document_id)

    pdf_path = UPLOAD_DIR / f"{document_id_str}.pdf"

    if not pdf_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    pdf_bytes = pdf_path.read_bytes()

    try:
        extracted = extract_pdf_text(pdf_bytes)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    chunks = chunk_pages(extracted.pages)

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="No text chunks found."
        )

    count = index_document(
        document_id=document_id_str,
        filename=pdf_path.name,
        chunks=chunks
    )

    return {
        "message": "Document indexed successfully",
        "document_id": document_id_str,
        "page_count": extracted.page_count,
        "chunk_count": count
    }


@router.post("/search")
def search_documents(request: SearchRequest):

    matches = semantic_search(
        question=request.question,
        top_k=request.top_k,
        document_id=(
            str(request.document_id)
            if request.document_id else None
        )
    )

    return {
        "question": request.question,
        "total_results": len(matches),
        "results": matches
    }

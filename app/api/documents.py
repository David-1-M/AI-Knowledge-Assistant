
from pathlib import Path
from uuid import uuid4

import pymupdf
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.pdf_service import extract_pdf_text


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("data/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...)
):
    # 1. Check filename extension
    if not file.filename or not (
        file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # 2. Read with a strict size limit
    try:
        contents = await file.read(MAX_FILE_SIZE + 1)
    finally:
        await file.close()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 10 MB upload limit."
        )

    # 3. Check file signature
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="File is not a valid PDF."
        )

    # 4. Extract PDF text
    try:
        result = extract_pdf_text(contents)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc
    except (pymupdf.FileDataError, RuntimeError) as exc:
        raise HTTPException(
            status_code=422,
            detail="PDF could not be processed."
        ) from exc

    # 5. Generate a safe document ID
    document_id = str(uuid4())

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    saved_path = UPLOAD_DIR / f"{document_id}.pdf"

    # Never use the user-supplied filename as a path
    saved_path.write_bytes(contents)

    # 6. Return extracted information
    return {
        "document_id": document_id,
        "filename": file.filename,
        "page_count": result.page_count,
        "character_count": len(result.text),
        "text": result.text,
        "pages": result.pages
    }


from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/api/chat",
    tags=["RAG Chat"]
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500
    )

    document_id: UUID | None = None

    top_k: int = Field(
        default=3,
        ge=1,
        le=5
    )


@router.post("/ask")
async def ask_question(request: ChatRequest):
    try:
        result = await answer_question(
            question=request.question,
            document_id=(
                str(request.document_id)
                if request.document_id else None
            ),
            top_k=request.top_k
        )

        return result

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code

        raise HTTPException(
            status_code=503,
            detail=(
                "The local language model could not "
                f"complete the request (Ollama HTTP {status}). "
                "Check that the model is installed."
            )
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running."
            )
        ) from exc

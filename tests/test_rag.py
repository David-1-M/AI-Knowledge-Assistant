
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import rag_service


client = TestClient(app)


def sample_source():
    return {
        "document_id": "test-document",
        "filename": "lecture-notes.pdf",
        "page_number": 3,
        "chunk_index": 0,
        "text": (
            "Supervised learning uses labelled "
            "examples to train prediction models."
        ),
        "distance": 0.2
    }


def test_prompt_contains_question():
    prompt = rag_service.build_prompt(
        "What is supervised learning?",
        [sample_source()]
    )

    assert "What is supervised learning?" in prompt


def test_prompt_contains_source_reference():
    prompt = rag_service.build_prompt(
        "Explain supervised learning",
        [sample_source()]
    )

    assert "[1]" in prompt
    assert "Page: 3" in prompt
    assert "labelled examples" in prompt


@pytest.mark.asyncio
async def test_rag_returns_cited_answer(monkeypatch):

    monkeypatch.setattr(
        rag_service,
        "semantic_search",
        lambda **kwargs: [sample_source()]
    )

    async def fake_generate(prompt):
        return (
            "Supervised learning uses "
            "labelled examples. [1]"
        )

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        fake_generate
    )

    result = await rag_service.answer_question(
        "Explain supervised learning"
    )

    assert "[1]" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["page_number"] == 3


@pytest.mark.asyncio
async def test_no_sources_returns_no_evidence(monkeypatch):

    monkeypatch.setattr(
        rag_service,
        "semantic_search",
        lambda **kwargs: []
    )

    async def should_not_generate(prompt):
        raise AssertionError(
            "LLM should not run without sources"
        )

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        should_not_generate
    )

    result = await rag_service.answer_question(
        "What does the document say?"
    )

    assert result["answer"] == rag_service.NO_EVIDENCE
    assert result["sources"] == []


def test_chat_endpoint(monkeypatch):

    async def fake_answer(**kwargs):
        return {
            "question": kwargs["question"],
            "answer": "A grounded test answer. [1]",
            "sources": [{
                "reference": "[1]",
                "page_number": 3
            }],
            "model": "test-model"
        }

    from app.api import chat

    monkeypatch.setattr(
        chat,
        "answer_question",
        fake_answer
    )

    response = client.post(
        "/api/chat/ask",
        json={
            "question": "What is supervised learning?",
            "top_k": 3
        }
    )

    assert response.status_code == 200
    assert response.json()["sources"][0]["reference"] == "[1]"


@pytest.mark.asyncio
async def test_no_retrieved_context_skips_llm(monkeypatch):
    # Arrange
    monkeypatch.setattr(
        rag_service,
        "semantic_search",
        lambda **kwargs: []
    )

    called = False

    async def fake_generate(prompt):
        nonlocal called
        called = True
        return "An unsupported answer"

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        fake_generate
    )

    # Act
    result = await rag_service.answer_question(
        question="What does the document say?"
    )

    # Assert
    assert called is False
    assert result["answer"] == rag_service.NO_EVIDENCE
    assert result["sources"] == []

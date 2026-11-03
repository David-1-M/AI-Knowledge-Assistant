
from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.services.chunking_service import TextChunk


VECTOR_PATH = Path("data/vector_store")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


@lru_cache(maxsize=1)
def get_collection():
    VECTOR_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(VECTOR_PATH)
    )

    return client.get_or_create_collection(
        name="knowledge_documents",
        embedding_function=None,
        metadata={"hnsw:space": "cosine"}
    )


def index_document(
    document_id: str,
    filename: str,
    chunks: list[TextChunk]
) -> int:

    if not chunks:
        raise ValueError("No text chunks to index")

    model = get_embedding_model()
    collection = get_collection()

    texts = [chunk.text for chunk in chunks]

    vectors = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False
    ).tolist()

    ids = [
        f"{document_id}_{chunk.chunk_index}"
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index
        }
        for chunk in chunks
    ]

    # Re-indexing replaces old chunks.
    collection.delete(
        where={"document_id": document_id}
    )

    collection.upsert(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas
    )

    return len(chunks)


def semantic_search(
    question: str,
    top_k: int = 3,
    document_id: str | None = None
) -> list[dict]:

    collection = get_collection()

    if collection.count() == 0:
        return []

    model = get_embedding_model()

    vector = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    filters = (
        {"document_id": document_id}
        if document_id else None
    )

    results = collection.query(
        query_embeddings=vector,
        n_results=min(top_k, collection.count()),
        where=filters,
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        matches.append({
            "document_id": metadata["document_id"],
            "filename": metadata["filename"],
            "page_number": metadata["page_number"],
            "chunk_index": metadata["chunk_index"],
            "text": text,
            "distance": round(float(distance), 4)
        })

    return matches

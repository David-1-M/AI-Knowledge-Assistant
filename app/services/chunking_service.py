
from dataclasses import dataclass


@dataclass
class TextChunk:
    page_number: int
    chunk_index: int
    text: str


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 160,
    overlap: int = 30
) -> list[TextChunk]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if not 0 <= overlap < chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []
    chunk_index = 0
    step = chunk_size - overlap

    for page in pages:
        words = page["text"].split()

        for start in range(0, len(words), step):
            selected = words[start:start + chunk_size]

            if not selected:
                break

            chunks.append(
                TextChunk(
                    page_number=page["page_number"],
                    chunk_index=chunk_index,
                    text=" ".join(selected)
                )
            )

            chunk_index += 1

            if start + chunk_size >= len(words):
                break

    return chunks

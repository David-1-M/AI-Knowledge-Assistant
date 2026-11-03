
from app.services.chunking_service import chunk_pages


def test_short_page_creates_one_chunk():
    pages = [{
        "page_number": 1,
        "text": "Machine learning uses data."
    }]

    chunks = chunk_pages(pages)

    assert len(chunks) == 1
    assert chunks[0].page_number == 1


def test_long_text_creates_multiple_chunks():
    pages = [{
        "page_number": 1,
        "text": " ".join(["learning"] * 400)
    }]

    chunks = chunk_pages(
        pages,
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) > 1


def test_chunk_preserves_page_numbers():
    pages = [
        {"page_number": 1, "text": "First page text"},
        {"page_number": 2, "text": "Second page text"}
    ]

    chunks = chunk_pages(pages)

    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2


def test_chunks_overlap():
    words = [f"word{i}" for i in range(15)]

    pages = [{
        "page_number": 1,
        "text": " ".join(words)
    }]

    chunks = chunk_pages(
        pages,
        chunk_size=10,
        overlap=3
    )

    first = chunks[0].text.split()
    second = chunks[1].text.split()

    assert first[-3:] == second[:3]


def test_empty_page_creates_no_chunks():
    pages = [{
        "page_number": 1,
        "text": ""
    }]

    assert chunk_pages(pages) == []

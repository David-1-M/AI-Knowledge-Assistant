
from dataclasses import dataclass

import pymupdf


@dataclass
class ExtractedPDF:
    page_count: int
    text: str
    pages: list[dict]


def extract_pdf_text(pdf_bytes: bytes) -> ExtractedPDF:
    """
    Extract text from a PDF, keeping page numbers.
    """
    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        if document.needs_pass:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        if document.page_count > 50:
            raise ValueError(
                "PDF exceeds the 50-page limit."
            )

        for page_number, page in enumerate(
            document, start=1
        ):
            text = page.get_text(
                "text", sort=True
            ).strip()

            pages.append({
                "page_number": page_number,
                "text": text
            })

    full_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    if not full_text.strip():
        raise ValueError(
            "No extractable text found. "
            "This PDF may contain scanned images."
        )

    if len(full_text) > 200_000:
        raise ValueError(
            "Extracted text exceeds the current limit."
        )

    return ExtractedPDF(
        page_count=len(pages),
        text=full_text,
        pages=pages
    )

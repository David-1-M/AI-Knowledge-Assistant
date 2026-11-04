# AI-Powered Knowledge Assistant

**A document-grounded AI assistant built with Python, FastAPI, Streamlit, ChromaDB, Sentence Transformers and Ollama.**

## Overview

AI-Powered Knowledge Assistant is a locally running Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask natural-language questions about their content.

The application extracts text, divides it into manageable chunks, generates vector embeddings and retrieves relevant passages through semantic search.

A locally hosted language model then generates an answer using the retrieved context and returns supporting document passages with page references.

The project demonstrates applied AI engineering, backend development, vector databases, LLM integration and automated testing.

## Features

- PDF upload and text extraction using PyMuPDF
- Document validation and upload-size limits
- Page-aware text chunking with overlapping passages
- Local embedding generation using Sentence Transformers
- Persistent semantic search with ChromaDB
- Retrieval-Augmented Generation using Ollama
- AI-generated answers with source references
- Document selection and conversational interface with Streamlit
- Automated testing using pytest
- GitHub Actions continuous integration

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| PDF processing | PyMuPDF |
| Embedding model | all-MiniLM-L6-v2 |
| Vector database | ChromaDB |
| Language model | Qwen3 0.6B via Ollama |
| HTTP client | HTTPX |
| Testing | pytest |
| Continuous Integration | GitHub Actions |
| Version control | Git and GitHub |

## System Architecture

The application follows a document-based RAG pipeline:

```text
PDF Upload
    |
    v
PDF Text Extraction
    |
    v
Page-Aware Text Chunking
    |
    v
Sentence Transformer Embeddings
    |
    v
ChromaDB Vector Storage
    |
    v
User Question
    |
    v
Semantic Retrieval
    |
    v
Retrieved Document Passages
    |
    v
Ollama Language Model
    |
    v
Generated Answer + Supporting Sources
```

### Document Processing

Uploaded PDF files are validated and assigned unique document identifiers. The system extracts text from individual pages and divides it into overlapping text chunks.

Each chunk retains metadata such as the document ID, page number and chunk index.

### Embeddings and Retrieval

The application uses the `all-MiniLM-L6-v2` model to represent document passages and user questions as numerical vectors.

ChromaDB stores these vectors and retrieves similar passages using vector similarity search.

### RAG Question Answering

Relevant passages are supplied to a locally hosted language model with instructions to answer using the available document content.

The API returns the generated answer and the retrieved passages, including page references.

Source references help users inspect supporting text, but they do not guarantee that every generated statement is accurate.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/api/health` | Health check |
| POST | `/api/documents/upload` | Upload and extract PDF text |
| POST | `/api/documents/{document_id}/index` | Generate and store embeddings |
| POST | `/api/search` | Perform semantic search |
| POST | `/api/chat/ask` | Generate a document-grounded answer |

## Installation and Local Setup

### Prerequisites

- Python with compatible project dependencies
- Ollama installed locally
- Git
- Sufficient storage and memory for the embedding model and local LLM

### 1. Clone the repository

```powershell
git clone https://github.com/David-1-M/AI-Knowledge-Assistant.git
cd AI-Knowledge-Assistant
```

### 2. Create and activate a virtual environment

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If using a different supported Python version, change the `py` version argument accordingly.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Download the local LLM

```powershell
ollama pull qwen3:0.6b
```

Ensure the Ollama service is running.

### 5. Start the FastAPI backend

```powershell
python -m uvicorn app.main:app --reload
```

FastAPI will normally be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the Streamlit frontend

In a separate terminal:

```powershell
python -m streamlit run streamlit_app.py
```

Open:

`http://localhost:8501`

## How to Use

1. Open the Streamlit interface.
2. Upload a text-based PDF.
3. Click **Upload and Index**.
4. Select the indexed document.
5. Enter a question in the chat interface.
6. Review the AI-generated answer.
7. Expand the supporting sources to inspect relevant passages and page numbers.

## Testing

Run the automated test suite:

```powershell
python -m pytest -v
```

Tests cover PDF validation, upload processing, chunking and mocked RAG behaviour, together with basic frontend checks.

GitHub Actions runs the automated test suite on pushes and pull requests targeting the main branch.

## Limitations

- The application is intended for local, single-user use.
- It does not implement account authentication or document-level access control.
- Scanned PDFs without selectable text are not supported.
- Complex PDF layouts may affect text extraction quality.
- A small local language model may produce incomplete or incorrect answers.
- Retrieved passages may be irrelevant even when semantic search returns results.
- Citation references identify retrieved passages but are not proof of factual correctness.
- Document selection and chat history are maintained within the Streamlit session.
- Public cloud deployment has not been implemented.

## Future Improvements

- Retrieval relevance thresholds and reranking
- More systematic RAG evaluation
- OCR for scanned PDF documents
- Persistent document library and chat history
- Account authentication and document permissions
- Secure deployment with a managed language model endpoint
- Larger or more capable LLM options

## Author

**David Mdluli**

BSc Information Technology — North-West University

Software Engineering | AI Engineering | Backend Development | Machine Learning
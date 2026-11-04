
import os
from uuid import UUID

import httpx
import streamlit as st


API_URL = os.getenv(
    "KNOWLEDGE_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- Application state ----------

if "documents" not in st.session_state:
    st.session_state.documents = {}

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- API helper ----------

def api_request(
    method: str,
    endpoint: str,
    timeout: float = 60,
    **kwargs
):
    with httpx.Client(
        timeout=httpx.Timeout(
            timeout,
            connect=10.0
        )
    ) as client:

        response = client.request(
            method,
            f"{API_URL}{endpoint}",
            **kwargs
        )

        response.raise_for_status()
        return response.json()


def show_api_error(error):
    if isinstance(error, httpx.HTTPStatusError):
        try:
            detail = error.response.json().get(
                "detail",
                "Request failed."
            )
        except ValueError:
            detail = error.response.text[:300]

        st.error(
            f"API error {error.response.status_code}: "
            f"{detail}"
        )

    elif isinstance(error, httpx.RequestError):
        st.error(
            "Cannot connect to the backend. "
            "Make sure FastAPI is running."
        )

    else:
        st.error("An unexpected error occurred.")


def valid_document_id(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        return None


# ---------- Sidebar ----------

with st.sidebar:
    st.title("📚 Knowledge Assistant")
    st.caption("Ask questions about your PDF documents.")

    st.divider()

    st.subheader("Upload a document")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        accept_multiple_files=False,
        max_upload_size=10
    )

    if uploaded_file is not None:
        st.caption(
            f"Selected: {uploaded_file.name}"
        )

        if st.button(
            "Upload and Index",
            type="primary",
            use_container_width=True
        ):

            try:
                with st.spinner(
                    "Uploading and extracting PDF..."
                ):
                    upload_result = api_request(
                        "POST",
                        "/api/documents/upload",
                        timeout=90,
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf"
                            )
                        }
                    )

                document_id = upload_result[
                    "document_id"
                ]

                with st.spinner(
                    "Creating embeddings and indexing..."
                ):
                    index_result = api_request(
                        "POST",
                        f"/api/documents/{document_id}/index",
                        timeout=300
                    )

                st.session_state.documents[
                    document_id
                ] = {
                    "filename": uploaded_file.name,
                    "pages": upload_result[
                        "page_count"
                    ],
                    "chunks": index_result[
                        "chunk_count"
                    ]
                }

                st.session_state.selected_document = (
                    document_id
                )

                st.session_state.messages = []

                st.success(
                    "Document uploaded and indexed!"
                )

            except (
                httpx.HTTPError,
                ValueError,
                KeyError
            ) as error:
                show_api_error(error)

    st.divider()

    st.subheader("Your documents")

    documents = st.session_state.documents

    if documents:
        document_ids = list(documents.keys())

        current = st.session_state.selected_document

        if current not in document_ids:
            current = document_ids[0]

        selected = st.selectbox(
            "Choose a document",
            options=document_ids,
            index=document_ids.index(current),
            format_func=lambda doc_id: (
                documents[doc_id]["filename"]
            )
        )

        if selected != st.session_state.selected_document:
            st.session_state.selected_document = selected
            st.session_state.messages = []

        info = documents[selected]

        st.caption(
            f"{info['pages']} pages · "
            f"{info['chunks']} text chunks"
        )

        st.success("Ready for questions")

    else:
        st.info(
            "Upload and index your first PDF."
        )

    st.divider()

    with st.expander("Open an existing document"):
        st.caption(
            "Use a document ID from an earlier upload. "
            "The original file must still exist and "
            "already be indexed."
        )

        existing_id = st.text_input(
            "Document UUID"
        )

        if st.button(
            "Select existing document",
            use_container_width=True
        ):
            parsed_id = valid_document_id(
                existing_id.strip()
            )

            if parsed_id is None:
                st.error("Enter a valid document UUID.")
            else:
                st.session_state.documents.setdefault(
                    parsed_id,
                    {
                        "filename": parsed_id,
                        "pages": "?",
                        "chunks": "?"
                    }
                )
                st.session_state.selected_document = (
                    parsed_id
                )
                st.session_state.messages = []
                st.rerun()

    if st.button(
        "Clear conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ---------- Main content ----------

st.title("AI-Powered Knowledge Assistant")

st.write(
    "Upload a PDF, ask questions, and explore "
    "answers grounded in your documents."
)

if st.session_state.selected_document:
    selected_info = st.session_state.documents[
        st.session_state.selected_document
    ]

    st.caption(
        f"Current document: "
        f"{selected_info['filename']}"
    )
else:
    st.info(
        "Start by uploading a PDF in the sidebar."
    )


# ---------- Chat history ----------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("sources"):
            with st.expander(
                "View supporting sources"
            ):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['reference']} — "
                        f"Page {source['page_number']}**"
                    )

                    st.caption(
                        source["filename"]
                    )

                    st.write(source["text"])

                    st.divider()


# ---------- Question input ----------

question = st.chat_input(
    "Ask a question about your PDF...",
    disabled=(
        st.session_state.selected_document is None
    )
)

if question:
    document_id = (
        st.session_state.selected_document
    )

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        try:
            with st.spinner(
                "Searching documents and generating answer..."
            ):
                result = api_request(
                    "POST",
                    "/api/chat/ask",
                    timeout=300,
                    json={
                        "question": question,
                        "document_id": document_id,
                        "top_k": 3
                    }
                )

            answer = result.get(
                "answer",
                "No answer was returned."
            )

            sources = result.get(
                "sources", []
            )

            st.write(answer)

            if sources:
                with st.expander(
                    "View supporting sources",
                    expanded=True
                ):
                    for source in sources:
                        st.markdown(
                            f"**{source['reference']} — "
                            f"Page {source['page_number']}**"
                        )

                        st.caption(
                            source["filename"]
                        )

                        st.write(source["text"])

                        st.divider()

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        except (
            httpx.HTTPError,
            ValueError,
            KeyError
        ) as error:
            show_api_error(error)

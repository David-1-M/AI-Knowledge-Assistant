
import ast
from pathlib import Path


def test_streamlit_app_has_valid_python_syntax():
    app_file = (
        Path(__file__).resolve().parents[1]
        / "streamlit_app.py"
    )

    source = app_file.read_text(encoding="utf-8")

    ast.parse(source)


def test_frontend_uses_chat_and_upload_widgets():
    app_file = (
        Path(__file__).resolve().parents[1]
        / "streamlit_app.py"
    )

    source = app_file.read_text(encoding="utf-8")

    assert "st.file_uploader" in source
    assert "st.chat_input" in source
    assert "/api/chat/ask" in source

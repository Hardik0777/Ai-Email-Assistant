"""Turns an uploaded PDF or DOCX resume into plain text, keeping line breaks so sections survive."""
import io

from docx import Document
from pypdf import PdfReader


class UnsupportedFile(ValueError):
    pass


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise UnsupportedFile("Only .pdf and .docx files are supported")

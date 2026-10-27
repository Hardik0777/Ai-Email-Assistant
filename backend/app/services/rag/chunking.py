"""Section-aware chunking: split the resume into sections first, then into overlapping chunks.

Keeping sections intact means a chunk about "Projects" never gets mixed with "Education",
which makes retrieval much more accurate.
"""
import re
from dataclasses import dataclass

KNOWN_SECTIONS = {
    "summary", "professional summary", "profile", "objective", "education", "experience",
    "work experience", "internship experience", "internships", "projects", "skills",
    "technical skills", "certifications", "achievements", "leadership", "leadership experience",
    "publications", "awards", "activities", "extracurricular activities",
}


@dataclass
class Chunk:
    section: str
    text: str


def _is_heading(line: str) -> bool:
    clean = line.strip().rstrip(":").lower()
    if clean in KNOWN_SECTIONS:
        return True
    # Short, all-caps lines like "TECHNICAL SKILLS" are usually headings too.
    return 3 <= len(line.strip()) <= 40 and line.strip().isupper() and not re.search(r"\d", line)


def split_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = [("General", [])]
    for line in text.splitlines():
        if not line.strip():
            continue
        if _is_heading(line):
            sections.append((line.strip().rstrip(":").title(), []))
        else:
            sections[-1][1].append(line.strip())
    return [(name, " ".join(lines)) for name, lines in sections if lines]


def _window(text: str, size: int, overlap: int) -> list[str]:
    """Fixed-size windows that try to end on a sentence or word boundary."""
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = max(text.rfind(". ", start, end), text.rfind(" ", start, end))
            if cut > start + size // 2:
                end = cut + 1
        pieces.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
        space = text.find(" ", start, end)  # don't start the next chunk mid-word
        if space != -1:
            start = space + 1
    return [p for p in pieces if p]


def chunk_resume(text: str, size: int = 700, overlap: int = 120) -> list[Chunk]:
    chunks = []
    for section, body in split_sections(text):
        for piece in _window(body, size, overlap):
            chunks.append(Chunk(section=section, text=piece))
    return chunks

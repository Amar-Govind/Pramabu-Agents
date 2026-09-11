from __future__ import annotations

import mimetypes
import re
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
TEXT_EXTS = {".txt", ".md", ".markdown", ".csv", ".json", ".yaml", ".yml", ".log"}
DOC_EXTS = {".pdf", ".docx", ".doc"}


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w.\-() ]+", "_", name).strip().replace(" ", "_")
    return cleaned[:180] or "upload.bin"


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in TEXT_EXTS:
        return "text"
    if ext in DOC_EXTS:
        return "document"
    mime, _ = mimetypes.guess_type(str(path))
    if mime and mime.startswith("image/"):
        return "image"
    if mime and mime.startswith("text/"):
        return "text"
    return "file"


def extract_text(path: Path, max_chars: int = 12000) -> str:
    ext = path.suffix.lower()
    try:
        if ext in TEXT_EXTS:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]

        if ext == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            chunks = []
            for page in reader.pages[:20]:
                chunks.append(page.extract_text() or "")
            return "\n".join(chunks)[:max_chars]

        if ext in {".docx", ".doc"}:
            from docx import Document

            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs if p.text)[:max_chars]
    except Exception as exc:  # noqa: BLE001
        return f"[Could not extract text from {path.name}: {exc}]"

    return f"[Binary file attached: {path.name}]"


def summarize_attachments(paths: list[Path]) -> dict:
    images: list[str] = []
    docs: list[dict] = []
    notes: list[str] = []

    for path in paths:
        kind = classify(path)
        if kind == "image":
            images.append(str(path))
            notes.append(f"Image attached: {path.name}")
        elif kind in {"text", "document"}:
            text = extract_text(path)
            docs.append({"name": path.name, "path": str(path), "text": text})
            notes.append(f"Document attached: {path.name} ({len(text)} chars extracted)")
        else:
            docs.append({"name": path.name, "path": str(path), "text": f"[File: {path.name}]"})
            notes.append(f"File attached: {path.name}")

    combined_doc_text = "\n\n".join(
        f"### {item['name']}\n{item['text']}" for item in docs if item.get("text")
    )
    return {
        "images": images,
        "documents": docs,
        "notes": notes,
        "combined_text": combined_doc_text[:16000],
    }

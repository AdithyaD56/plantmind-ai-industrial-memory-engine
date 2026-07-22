from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple
import csv
import json
import os

try:
    import fitz
except Exception:  # pragma: no cover - optional dependency
    fitz = None

try:
    import pandas as pd
except Exception:  # pragma: no cover - optional dependency
    pd = None

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    Image = None

from ..core.models import DocumentChunk, make_id
from ..core.text_utils import chunk_text, normalize_spaces

try:
    import easyocr
except Exception:  # pragma: no cover - optional dependency
    easyocr = None


@dataclass
class ParsedDocument:
    full_text: str
    chunks: List[DocumentChunk]
    pages: int
    source_type: str
    metadata: Dict[str, str]


class DocumentParser:
    def __init__(self, use_ocr: bool = True):
        self.use_ocr = use_ocr and easyocr is not None
        self._ocr_reader = None

    def _reader(self):
        if self._ocr_reader is None and self.use_ocr and easyocr is not None:
            self._ocr_reader = easyocr.Reader(["en"], gpu=False)
        return self._ocr_reader

    def parse(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        suffix = file_path.suffix.lower()
        if suffix in {".pdf"}:
            return self._parse_pdf(file_path, document_id, document_name)
        if suffix in {".xlsx", ".xls"}:
            return self._parse_excel(file_path, document_id, document_name)
        if suffix in {".csv"}:
            return self._parse_csv(file_path, document_id, document_name)
        if suffix in {".json"}:
            return self._parse_json(file_path, document_id, document_name)
        return self._parse_text(file_path, document_id, document_name)

    def _make_chunks(self, document_id: str, document_name: str, text: str, source_type: str, page_number: int | None, extra: Dict[str, str]) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        for index, chunk in enumerate(chunk_text(text)):
            chunks.append(
                DocumentChunk(
                    chunk_id=make_id("chunk"),
                    document_id=document_id,
                    document_name=document_name,
                    content=chunk,
                    page_number=page_number,
                    source_type=source_type,
                    metadata={**extra, "chunk_index": index},
                    citations=[f"{document_name} p.{page_number}" if page_number else document_name],
                )
            )
        return chunks

    def _parse_pdf(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        if fitz is None:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            chunks = self._make_chunks(document_id, document_name, text, "pdf", None, {"fallback": "text"})
            return ParsedDocument(full_text=text, chunks=chunks, pages=1, source_type="pdf", metadata={"file_name": file_path.name, "fallback": "text"})
        doc = fitz.open(file_path)
        chunks: List[DocumentChunk] = []
        pages_text: List[str] = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = normalize_spaces(page.get_text("text"))
            if not text and self.use_ocr and self._reader() is not None and Image is not None and np is not None:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_result = self._reader().readtext(np.array(image), detail=0, paragraph=True)
                text = normalize_spaces(" ".join(ocr_result))
            pages_text.append(text)
            chunks.extend(self._make_chunks(document_id, document_name, text, "pdf", page_index + 1, {"page": page_index + 1}))
        full_text = "\n".join(t for t in pages_text if t)
        return ParsedDocument(full_text=full_text, chunks=chunks, pages=len(doc), source_type="pdf", metadata={"file_name": file_path.name})

    def _parse_excel(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        if pd is None:
            return self._parse_text(file_path, document_id, document_name)
        sheets = pd.read_excel(file_path, sheet_name=None)
        chunks: List[DocumentChunk] = []
        parts: List[str] = []
        for sheet_name, frame in sheets.items():
            text = frame.to_csv(index=False)
            parts.append(f"Sheet: {sheet_name}\n{text}")
            chunks.extend(self._make_chunks(document_id, document_name, text, "excel", None, {"sheet": sheet_name}))
        return ParsedDocument(full_text="\n".join(parts), chunks=chunks, pages=max(len(sheets), 1), source_type="excel", metadata={"file_name": file_path.name})

    def _parse_csv(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        if pd is not None:
            frame = pd.read_csv(file_path)
            text = frame.to_csv(index=False)
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = self._make_chunks(document_id, document_name, text, "csv", None, {})
        return ParsedDocument(full_text=text, chunks=chunks, pages=1, source_type="csv", metadata={"file_name": file_path.name})

    def _parse_json(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        raw = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
        text = json.dumps(raw, indent=2, ensure_ascii=True)
        chunks = self._make_chunks(document_id, document_name, text, "json", None, {})
        return ParsedDocument(full_text=text, chunks=chunks, pages=1, source_type="json", metadata={"file_name": file_path.name})

    def _parse_text(self, file_path: Path, document_id: str, document_name: str) -> ParsedDocument:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = self._make_chunks(document_id, document_name, text, "text", None, {})
        return ParsedDocument(full_text=text, chunks=chunks, pages=1, source_type="text", metadata={"file_name": file_path.name})

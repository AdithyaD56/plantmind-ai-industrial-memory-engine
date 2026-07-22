from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from ..core.models import DocumentRecord, IngestionResult, make_id, utc_now_iso
from ..core.storage import SQLiteStore
from ..core.text_utils import extract_entities, normalize_spaces
from ..graph.builder import KnowledgeGraphBuilder
from ..parsers.document_parser import DocumentParser
from ..retrieval.chroma_store import ChromaMemory


class DocumentIntelligenceAgent:
    def __init__(self, store: SQLiteStore, memory: ChromaMemory, graph_builder: KnowledgeGraphBuilder):
        self.store = store
        self.memory = memory
        self.graph_builder = graph_builder
        self.parser = DocumentParser()

    def ingest(self, file_path: Path, document_name: str, document_type: str | None = None) -> IngestionResult:
        document_id = make_id("doc")
        parsed = self.parser.parse(file_path, document_id, document_name)
        entities = extract_entities(parsed.full_text)
        summary = self._summarize(parsed.full_text)

        record = DocumentRecord(
            document_id=document_id,
            document_name=document_name,
            document_type=document_type or parsed.source_type,
            uploaded_at=utc_now_iso(),
            pages=parsed.pages,
            chunks=len(parsed.chunks),
            summary=summary,
        )

        self.store.upsert_document(record)
        self.store.add_chunks(parsed.chunks)
        self.store.add_entities(document_id, entities)
        self.memory.add_many(
            [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "document_name": chunk.document_name,
                        "page_number": chunk.page_number,
                        **chunk.metadata,
                    },
                }
                for chunk in parsed.chunks
            ]
        )

        graph_summary = self.graph_builder.build_from_document(document_id, document_name, parsed.full_text, entities, [asdict(chunk) for chunk in parsed.chunks])
        return IngestionResult(
            document=record,
            chunks=parsed.chunks,
            entities=entities,
            graph_summary=graph_summary.__dict__,
            failure_insights=[],
            compliance=None,  # set by orchestration layer
        )

    def _summarize(self, text: str, max_chars: int = 280) -> str:
        text = normalize_spaces(text)
        return text[:max_chars] + ("..." if len(text) > max_chars else "")

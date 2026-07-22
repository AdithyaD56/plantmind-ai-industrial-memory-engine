from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import DocumentChunk, DocumentRecord, utc_now_iso


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    status TEXT NOT NULL,
    pages INTEGER NOT NULL DEFAULT 0,
    chunks INTEGER NOT NULL DEFAULT 0,
    summary TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    document_name TEXT NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    source_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    citations_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_value TEXT NOT NULL,
    extra_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    incident_date TEXT NOT NULL,
    title TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    severity REAL NOT NULL DEFAULT 0,
    details_json TEXT NOT NULL
);
"""


class SQLiteStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def upsert_document(self, record: DocumentRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (document_id, document_name, document_type, uploaded_at, status, pages, chunks, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    document_name=excluded.document_name,
                    document_type=excluded.document_type,
                    uploaded_at=excluded.uploaded_at,
                    status=excluded.status,
                    pages=excluded.pages,
                    chunks=excluded.chunks,
                    summary=excluded.summary
                """,
                (
                    record.document_id,
                    record.document_name,
                    record.document_type,
                    record.uploaded_at,
                    record.status,
                    record.pages,
                    record.chunks,
                    record.summary,
                ),
            )
            conn.commit()

    def add_chunks(self, chunks: Iterable[DocumentChunk]) -> None:
        rows = []
        for chunk in chunks:
            rows.append(
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.document_name,
                    chunk.content,
                    chunk.page_number,
                    chunk.source_type,
                    json.dumps(chunk.metadata, ensure_ascii=True),
                    json.dumps(chunk.citations, ensure_ascii=True),
                )
            )
        if not rows:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO chunks
                (chunk_id, document_id, document_name, content, page_number, source_type, metadata_json, citations_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()

    def add_entities(self, document_id: str, entities: Dict[str, Any]) -> None:
        rows = []
        for entity_type, values in entities.items():
            for value in values:
                if isinstance(value, dict):
                    entity_value = str(value.get("value") or value.get("text") or value.get("name") or "")
                    extra = value
                else:
                    entity_value = str(value)
                    extra = {"value": entity_value}
                rows.append((document_id, entity_type, entity_value, json.dumps(extra, ensure_ascii=True)))
        if not rows:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO entities (document_id, entity_type, entity_value, extra_json)
                VALUES (?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()

    def add_incident(
        self,
        document_id: str,
        equipment_id: str,
        incident_date: str,
        title: str,
        root_cause: str,
        severity: float,
        details: Dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incidents (document_id, equipment_id, incident_date, title, root_cause, severity, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (document_id, equipment_id, incident_date, title, root_cause, severity, json.dumps(details, ensure_ascii=True)),
            )
            conn.commit()

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY uploaded_at DESC").fetchall()
        return [dict(row) for row in rows]

    def list_chunks(self, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if document_id:
                rows = conn.execute("SELECT * FROM chunks WHERE document_id = ? ORDER BY page_number, chunk_id", (document_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM chunks ORDER BY document_name, page_number, chunk_id").fetchall()
        return [dict(row) for row in rows]

    def list_entities(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM entities ORDER BY entity_type, entity_value").fetchall()
        return [dict(row) for row in rows]

    def list_incidents(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM incidents ORDER BY incident_date DESC").fetchall()
        return [dict(row) for row in rows]

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,)).fetchone()
        return dict(row) if row else None

    def summary_counts(self) -> Dict[str, Any]:
        with self._connect() as conn:
            doc_count = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
            entity_count = conn.execute("SELECT COUNT(*) AS n FROM entities").fetchone()["n"]
            incident_count = conn.execute("SELECT COUNT(*) AS n FROM incidents").fetchone()["n"]
        return {"documents": doc_count, "entities": entity_count, "incidents": incident_count}

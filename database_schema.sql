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


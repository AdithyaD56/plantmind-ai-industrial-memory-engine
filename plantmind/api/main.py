from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ..core.config import CONFIG
from ..services.industrial_service import IndustrialService


service = IndustrialService()

app = FastAPI(title=CONFIG.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "app": CONFIG.app_name}


@app.get("/overview")
def overview() -> Dict[str, Any]:
    return service.overview()


@app.get("/graph")
def graph() -> Dict[str, Any]:
    return service.graph_payload()


@app.get("/equipment/{equipment_id}")
def equipment_passport(equipment_id: str) -> Dict[str, Any]:
    return service.equipment_passport(equipment_id)


@app.get("/failure-intelligence")
def failure_intelligence(equipment_id: Optional[str] = None) -> Dict[str, Any]:
    return service.failure_dashboard(equipment_id)


@app.get("/compliance")
def compliance() -> Dict[str, Any]:
    return service.compliance_dashboard()


@app.post("/ask")
def ask(payload: Dict[str, Any]) -> Dict[str, Any]:
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    return service.ask(question)


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> Dict[str, Any]:
    suffix = Path(file.filename or "document.txt").suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        result = service.ingest_file(tmp_path, document_name=file.filename or tmp_path.name, document_type=suffix.lstrip("."))
        return result
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


@app.get("/documents")
def documents() -> Dict[str, Any]:
    return {"documents": service.store.list_documents()}


@app.get("/timeline/{equipment_id}")
def timeline(equipment_id: str) -> Dict[str, Any]:
    incidents = [row for row in service.store.list_incidents() if row.get("equipment_id") == equipment_id or equipment_id in str(row.get("details_json"))]
    chunks = [row for row in service.store.list_chunks() if equipment_id in row.get("content", "") or equipment_id in str(row.get("metadata_json", ""))]
    timeline_items = []
    for incident in incidents:
        timeline_items.append(
            {
                "date": incident.get("incident_date"),
                "type": "Incident",
                "title": incident.get("title"),
                "detail": incident.get("root_cause"),
            }
        )
    for chunk in chunks[:20]:
        timeline_items.append(
            {
                "date": chunk.get("page_number") or "N/A",
                "type": chunk.get("source_type"),
                "title": chunk.get("document_name"),
                "detail": chunk.get("content", "")[:140],
            }
        )
    return {"equipment_id": equipment_id, "items": timeline_items}


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("plantmind.api.main:app", host=CONFIG.host, port=CONFIG.port, reload=True)


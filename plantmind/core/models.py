from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    page_number: Optional[int] = None
    source_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)


@dataclass
class DocumentRecord:
    document_id: str
    document_name: str
    document_type: str
    uploaded_at: str
    status: str = "processed"
    pages: int = 0
    chunks: int = 0
    summary: str = ""


@dataclass
class EvidenceMatch:
    document_id: str
    document_name: str
    chunk_id: str
    excerpt: str
    score: float
    page_number: Optional[int] = None


@dataclass
class FailureInsight:
    equipment_id: str
    risk_score: float
    similarity_score: float
    alert_level: str
    root_cause_suggestions: List[str]
    similar_incidents: List[Dict[str, Any]]
    lessons_learned: List[str]
    recommended_actions: List[str]


@dataclass
class ComplianceResult:
    compliance_percent: float
    audit_readiness_score: float
    missing_requirements: List[str]
    recommendations: List[str]


@dataclass
class CopilotAnswer:
    answer: str
    citations: List[Dict[str, Any]]
    follow_up_questions: List[str] = field(default_factory=list)


@dataclass
class IngestionResult:
    document: DocumentRecord
    chunks: List[DocumentChunk]
    entities: Dict[str, Any]
    graph_summary: Dict[str, Any]
    failure_insights: List[FailureInsight]
    compliance: Optional[ComplianceResult]


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def serialize_dataclass(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [serialize_dataclass(item) for item in value]
    if isinstance(value, dict):
        return {k: serialize_dataclass(v) for k, v in value.items()}
    return value

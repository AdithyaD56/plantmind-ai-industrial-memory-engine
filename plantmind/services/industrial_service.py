from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..agents.compliance_agent import ComplianceAgent
from ..agents.document_intelligence import DocumentIntelligenceAgent
from ..agents.engineer_copilot import EngineerCopilotAgent
from ..agents.failure_intelligence import FailureIntelligenceAgent
from ..agents.workflows import PlantMindWorkflow
from ..core.config import CONFIG
from ..core.models import serialize_dataclass
from ..core.storage import SQLiteStore
from ..graph.builder import KnowledgeGraphBuilder
from ..retrieval.chroma_store import ChromaMemory


class IndustrialService:
    def __init__(self):
        self.store = SQLiteStore(CONFIG.sqlite_path)
        self.memory = ChromaMemory(CONFIG.chroma_dir)
        self.graph_builder = KnowledgeGraphBuilder()
        self.doc_agent = DocumentIntelligenceAgent(self.store, self.memory, self.graph_builder)
        self.failure_agent = FailureIntelligenceAgent()
        self.compliance_agent = ComplianceAgent()
        self.copilot = EngineerCopilotAgent(self.memory, self.store)
        self.workflow = PlantMindWorkflow(self.doc_agent, self.failure_agent, self.compliance_agent, self.copilot)
        self._hydrate_memory()

    def ingest_file(self, file_path: Path, document_name: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        result = self.workflow.run_ingestion(file_path, document_name, document_type)
        self._maybe_store_incident(result, document_name, document_type)
        equipment_id = (result.get("entities", {}).get("equipment_ids") or ["UNKNOWN"])[0]
        docs = self.store.list_documents()
        incidents = self.store.list_incidents()
        chunks = self.store.list_chunks()
        result["failure_insights"] = [serialize_dataclass(self.failure_agent.analyze(equipment_id, docs, incidents, chunks))]
        return result

    def ask(self, question: str) -> Dict[str, Any]:
        return self.workflow.ask(question)

    def overview(self) -> Dict[str, Any]:
        counts = self.store.summary_counts()
        incidents = self.store.list_incidents()
        docs = self.store.list_documents()
        entities = self.store.list_entities()
        risk_scores = []
        for incident in incidents:
            sev = float(incident.get("severity", 0))
            risk_scores.append(min(100.0, sev * 100))
        average_risk = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0.0
        equipment_tracked = len({row.get("entity_value") for row in entities if row.get("entity_type") == "equipment_ids"})
        compliance_score = self.compliance_dashboard().get("compliance_percent", 0.0)
        return {
            "documents_processed": counts["documents"],
            "equipment_tracked": equipment_tracked or counts["entities"],
            "incidents_identified": counts["incidents"],
            "risk_alerts": sum(1 for row in incidents if float(row.get("severity", 0)) >= 0.6),
            "compliance_score": round(compliance_score, 1),
            "average_risk": average_risk,
            "graph_summary": self.graph_builder.summary().__dict__,
            "recent_documents": docs[:8],
            "recent_incidents": incidents[:8],
        }

    def graph_payload(self) -> Dict[str, Any]:
        return self.graph_builder.to_payload()

    def equipment_passport(self, equipment_id: str) -> Dict[str, Any]:
        incidents = [row for row in self.store.list_incidents() if row.get("equipment_id") == equipment_id or equipment_id in str(row.get("details_json"))]
        chunks = [row for row in self.store.list_chunks() if equipment_id in row.get("content", "") or equipment_id in str(row.get("metadata_json", ""))]
        docs = self.store.list_documents()
        insight = self.failure_agent.analyze(equipment_id, docs, incidents, chunks)
        return {
            "equipment_id": equipment_id,
            "incidents": incidents,
            "chunks": chunks[:20],
            "failure_insight": serialize_dataclass(insight),
        }

    def failure_dashboard(self, equipment_id: Optional[str] = None) -> Dict[str, Any]:
        incidents = self.store.list_incidents()
        docs = self.store.list_documents()
        chunks = self.store.list_chunks()
        tracked_ids = equipment_id and [equipment_id] or sorted({row.get("equipment_id") for row in incidents if row.get("equipment_id")})
        insights = [serialize_dataclass(self.failure_agent.analyze(eq, docs, incidents, chunks)) for eq in tracked_ids[:10]]
        clusters = self._cluster_incidents(incidents)
        return {"insights": insights, "clusters": clusters, "incidents": incidents}

    def compliance_dashboard(self) -> Dict[str, Any]:
        docs = self.store.list_documents()
        chunks = self.store.list_chunks()
        text = "\n".join([doc.get("summary", "") for doc in docs] + [row.get("content", "") for row in chunks])
        result = self.compliance_agent.evaluate(text)
        return serialize_dataclass(result)

    def _cluster_incidents(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for item in incidents:
            key = item.get("root_cause", "Unknown")
            buckets.setdefault(key, []).append(item)
        return [{"root_cause": key, "count": len(rows), "examples": rows[:3]} for key, rows in buckets.items()]

    def _hydrate_memory(self) -> None:
        # Rebuild the graph and retrieval index from the persistent store on startup.
        entities_by_doc: Dict[str, Dict[str, List[str]]] = {}
        for row in self.store.list_entities():
            entities_by_doc.setdefault(row["document_id"], {}).setdefault(row["entity_type"], []).append(row["entity_value"])
        for doc in self.store.list_documents():
            chunks = self.store.list_chunks(doc.get("document_id"))
            if chunks:
                self.memory.add_many(
                    [
                        {
                            "chunk_id": row["chunk_id"],
                            "content": row["content"],
                            "metadata": {
                                "document_id": row["document_id"],
                                "document_name": row["document_name"],
                                "page_number": row.get("page_number"),
                                "source_type": row.get("source_type"),
                            },
                        }
                        for row in chunks
                    ]
                )
            entities = entities_by_doc.get(doc["document_id"], {})
            self.graph_builder.build_from_document(
                doc["document_id"],
                doc["document_name"],
                doc.get("summary", ""),
                entities,
                chunks,
            )
        for incident in self.store.list_incidents():
            self.graph_builder.add_incident(
                incident_id=f"incident:{incident['incident_id']}",
                equipment_id=incident.get("equipment_id", "UNKNOWN"),
                root_cause=incident.get("root_cause", "Unknown"),
                severity=float(incident.get("severity", 0)),
                incident_date=incident.get("incident_date", ""),
                title=incident.get("title", "Incident"),
            )

    def _maybe_store_incident(self, result: Dict[str, Any], document_name: str, document_type: Optional[str]) -> None:
        name = document_name.lower()
        if not any(token in name for token in ["incident", "near-miss", "failure", "breakdown"]):
            return
        entities = result.get("entities", {})
        equipment_id = (entities.get("equipment_ids") or ["UNKNOWN"])[0]
        root_cause = ", ".join(entities.get("failure_modes", [])) or "Operational anomaly"
        severity = 0.7 if "incident" in name or "failure" in name else 0.45
        incident_date = (entities.get("dates") or ["2026-01-01"])[0]
        self.store.add_incident(
            document_id=result["document"]["document_id"],
            equipment_id=equipment_id,
            incident_date=incident_date,
            title=document_name,
            root_cause=root_cause,
            severity=severity,
            details=result,
        )
        self.graph_builder.add_incident(
            incident_id=f"incident:{result['document']['document_id']}",
            equipment_id=equipment_id,
            root_cause=root_cause,
            severity=severity,
            incident_date=incident_date,
            title=document_name,
        )

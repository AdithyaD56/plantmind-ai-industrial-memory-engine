from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

try:
    from langgraph.graph import StateGraph, END
except Exception:  # pragma: no cover - optional dependency
    StateGraph = None
    END = None

from .document_intelligence import DocumentIntelligenceAgent
from .failure_intelligence import FailureIntelligenceAgent
from .compliance_agent import ComplianceAgent
from .engineer_copilot import EngineerCopilotAgent
from ..core.models import serialize_dataclass


class PlantMindWorkflow:
    def __init__(self, doc_agent: DocumentIntelligenceAgent, failure_agent: FailureIntelligenceAgent, compliance_agent: ComplianceAgent, copilot: EngineerCopilotAgent):
        self.doc_agent = doc_agent
        self.failure_agent = failure_agent
        self.compliance_agent = compliance_agent
        self.copilot = copilot

    def run_ingestion(self, file_path, document_name: str, document_type: str | None = None) -> Dict[str, Any]:
        ingested = self.doc_agent.ingest(file_path, document_name, document_type)
        text = "\n".join(chunk.content for chunk in ingested.chunks)
        compliance = self.compliance_agent.evaluate(text)
        ingested.compliance = compliance
        incidents = self.doc_agent.store.list_incidents()
        docs = self.doc_agent.store.list_documents()
        chunks = self.doc_agent.store.list_chunks()
        equipment_id = ingested.entities.get("equipment_ids", ["UNKNOWN"])[0] if ingested.entities.get("equipment_ids") else "UNKNOWN"
        failure_insight = self.failure_agent.analyze(equipment_id, docs, incidents, chunks)
        ingested.failure_insights = [failure_insight]
        return {
            "document": serialize_dataclass(ingested.document),
            "entities": ingested.entities,
            "graph_summary": ingested.graph_summary,
            "failure_insights": [serialize_dataclass(failure_insight)],
            "compliance": serialize_dataclass(compliance),
        }

    def ask(self, question: str) -> Dict[str, Any]:
        return serialize_dataclass(self.copilot.answer(question))


def build_langgraph_workflow(runtime: PlantMindWorkflow):
    if StateGraph is None:
        return runtime

    class WorkflowState(dict):
        pass

    graph = StateGraph(WorkflowState)

    def ingest_node(state):
        result = runtime.run_ingestion(state["file_path"], state["document_name"], state.get("document_type"))
        state.update(result)
        return state

    def ask_node(state):
        state["copilot"] = runtime.ask(state["question"])
        return state

    graph.add_node("ingest", ingest_node)
    graph.add_node("ask", ask_node)
    graph.set_entry_point("ingest")
    graph.add_edge("ingest", END)
    return graph.compile()


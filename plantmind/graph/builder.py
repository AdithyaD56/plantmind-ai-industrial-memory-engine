from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List

try:
    import networkx as nx
except Exception:  # pragma: no cover - optional dependency
    nx = None


class _FallbackMultiDiGraph:
    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[tuple[str, str, Dict[str, Any]]] = []

    def add_node(self, node_id: str, **data: Any) -> None:
        self._nodes.setdefault(node_id, {}).update(data)

    def add_edge(self, source: str, target: str, **data: Any) -> None:
        self._edges.append((source, target, dict(data)))

    def nodes(self, data: bool = False):
        items = list(self._nodes.items())
        return items if data else [node_id for node_id, _ in items]

    def edges(self, data: bool = False):
        return self._edges if data else [(source, target) for source, target, _ in self._edges]

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def to_undirected(self):
        return self


GraphBackend = nx.MultiDiGraph if nx is not None else _FallbackMultiDiGraph

from ..core.text_utils import extract_entities


@dataclass
class GraphSummary:
    nodes: int
    edges: int
    node_types: Dict[str, int] = field(default_factory=dict)
    edge_types: Dict[str, int] = field(default_factory=dict)


class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = GraphBackend()

    def build_from_document(self, document_id: str, document_name: str, text: str, entities: Dict[str, Any], chunks: List[Dict[str, Any]]) -> GraphSummary:
        extracted = entities or extract_entities(text)
        self._add_document(document_id, document_name)
        self._add_entities(document_id, document_name, extracted)
        self._add_chunk_links(document_id, chunks)
        return self.summary()

    def _add_document(self, document_id: str, document_name: str) -> None:
        self.graph.add_node(document_id, type="document", label=document_name)

    def _node_id(self, prefix: str, value: str) -> str:
        return f"{prefix}:{value}".replace(" ", "_")

    def _add_entities(self, document_id: str, document_name: str, entities: Dict[str, Any]) -> None:
        equipment_ids = entities.get("equipment_ids", [])
        locations = entities.get("locations", [])
        dates = entities.get("dates", [])
        personnel = entities.get("personnel", [])
        failure_modes = entities.get("failure_modes", [])
        procedures = entities.get("procedures", [])
        regulations = entities.get("regulations", [])

        for equipment in equipment_ids:
            eq_id = self._node_id("equipment", equipment)
            self.graph.add_node(eq_id, type="equipment", label=equipment)
            self.graph.add_edge(document_id, eq_id, type="mentions")
            self.graph.add_edge(eq_id, document_id, type="documented_in")

        for location in locations:
            loc_id = self._node_id("location", location)
            self.graph.add_node(loc_id, type="location", label=location)
            self.graph.add_edge(document_id, loc_id, type="references")

        for date in dates:
            date_id = self._node_id("date", date)
            self.graph.add_node(date_id, type="date", label=date)
            self.graph.add_edge(document_id, date_id, type="dated")

        for person in personnel:
            person_id = self._node_id("person", person)
            self.graph.add_node(person_id, type="person", label=person)
            self.graph.add_edge(document_id, person_id, type="authored_by")

        for mode in failure_modes:
            mode_id = self._node_id("failure_mode", mode)
            self.graph.add_node(mode_id, type="failure_mode", label=mode)
            self.graph.add_edge(document_id, mode_id, type="describes")

        for procedure in procedures:
            proc_id = self._node_id("procedure", procedure[:60])
            self.graph.add_node(proc_id, type="procedure", label=procedure)
            self.graph.add_edge(document_id, proc_id, type="contains_procedure")
            for equipment in equipment_ids:
                self.graph.add_edge(self._node_id("equipment", equipment), proc_id, type="governed_by")

        for regulation in regulations:
            reg_id = self._node_id("regulation", regulation)
            self.graph.add_node(reg_id, type="regulation", label=regulation)
            self.graph.add_edge(document_id, reg_id, type="references_regulation")

        for equipment in equipment_ids:
            for mode in failure_modes:
                self.graph.add_edge(
                    self._node_id("equipment", equipment),
                    self._node_id("failure_mode", mode),
                    type="associated_failure",
                )

    def _add_chunk_links(self, document_id: str, chunks: List[Dict[str, Any]]) -> None:
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            self.graph.add_node(chunk_id, type="chunk", label=chunk.get("document_name", "chunk"))
            self.graph.add_edge(document_id, chunk_id, type="contains")

    def add_incident(self, incident_id: str, equipment_id: str, root_cause: str, severity: float, incident_date: str, title: str) -> None:
        self.graph.add_node(incident_id, type="incident", label=title, severity=severity, date=incident_date, root_cause=root_cause)
        eq_node = self._node_id("equipment", equipment_id)
        self.graph.add_node(eq_node, type="equipment", label=equipment_id)
        self.graph.add_edge(eq_node, incident_id, type="experienced")
        rc_node = self._node_id("root_cause", root_cause)
        self.graph.add_node(rc_node, type="root_cause", label=root_cause)
        self.graph.add_edge(incident_id, rc_node, type="caused_by")

    def summary(self) -> GraphSummary:
        node_types: Dict[str, int] = defaultdict(int)
        edge_types: Dict[str, int] = defaultdict(int)
        for _, data in self.graph.nodes(data=True):
            node_types[data.get("type", "unknown")] += 1
        for _, _, data in self.graph.edges(data=True):
            edge_types[data.get("type", "related")] += 1
        return GraphSummary(nodes=self.graph.number_of_nodes(), edges=self.graph.number_of_edges(), node_types=dict(node_types), edge_types=dict(edge_types))

    def to_payload(self, limit: int = 250) -> Dict[str, Any]:
        nodes = []
        for node, data in list(self.graph.nodes(data=True))[:limit]:
            nodes.append({"id": node, **data})
        edges = []
        for source, target, data in list(self.graph.edges(data=True))[:limit]:
            edges.append({"source": source, "target": target, **data})
        return {"nodes": nodes, "edges": edges, "summary": self.summary().__dict__}

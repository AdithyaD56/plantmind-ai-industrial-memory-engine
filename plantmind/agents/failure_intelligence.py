from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Any, Dict, List

import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - optional dependency
    TfidfVectorizer = None
    cosine_similarity = None

from ..core.models import FailureInsight


class FailureIntelligenceAgent:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english") if TfidfVectorizer is not None else None

    def analyze(self, equipment_id: str, documents: List[Dict[str, Any]], incidents: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> FailureInsight:
        incident_texts = [f"{row['title']} {row['root_cause']} {row['details_json']}" for row in incidents if row.get("equipment_id") in {equipment_id, "UNKNOWN"} or equipment_id in str(row.get("details_json"))]
        similarity_score = self._similarity_score(equipment_id, incident_texts, chunks)
        risk_score = self._risk_score(incidents, incident_texts, similarity_score)
        similar_incidents = self._similar_incidents(equipment_id, incidents)
        suggestions = self._root_cause_suggestions(incidents, chunks)
        lessons = self._lessons_learned(incidents)
        actions = self._actions_from_risk(risk_score, suggestions)
        alert_level = "High" if risk_score >= 0.7 else "Medium" if risk_score >= 0.45 else "Low"
        return FailureInsight(
            equipment_id=equipment_id,
            risk_score=round(risk_score, 2),
            similarity_score=round(similarity_score, 2),
            alert_level=alert_level,
            root_cause_suggestions=suggestions,
            similar_incidents=similar_incidents,
            lessons_learned=lessons,
            recommended_actions=actions,
        )

    def _similarity_score(self, equipment_id: str, incident_texts: List[str], chunks: List[Dict[str, Any]]) -> float:
        if not incident_texts or not chunks:
            return 0.0
        corpus = incident_texts + [chunk["content"] for chunk in chunks]
        if len(corpus) < 2:
            return 0.0
        if self.vectorizer is not None and cosine_similarity is not None:
            matrix = self.vectorizer.fit_transform(corpus)
            sim = cosine_similarity(matrix[: len(incident_texts)], matrix[len(incident_texts):]).max()
            return float(sim)
        query_tokens = set()
        for text in incident_texts:
            query_tokens.update(re.findall(r"\w+", text.lower()))
        best = 0.0
        for chunk in chunks:
            chunk_tokens = set(re.findall(r"\w+", chunk.get("content", "").lower()))
            union = len(query_tokens | chunk_tokens) or 1
            best = max(best, len(query_tokens & chunk_tokens) / union)
        return float(best)

    def _risk_score(self, incidents: List[Dict[str, Any]], incident_texts: List[str], similarity_score: float) -> float:
        if not incidents:
            return min(0.25 + similarity_score * 0.5, 0.6)
        severity_avg = sum(float(row.get("severity", 0)) for row in incidents) / max(len(incidents), 1)
        recurrence_bonus = min(len(incidents) / 5.0, 0.35)
        return min(1.0, 0.2 + severity_avg * 0.4 + recurrence_bonus + similarity_score * 0.35)

    def _similar_incidents(self, equipment_id: str, incidents: List[Dict[str, Any]], limit: int = 4) -> List[Dict[str, Any]]:
        matches = [row for row in incidents if row.get("equipment_id") == equipment_id or equipment_id in str(row.get("details_json"))]
        matches = sorted(matches, key=lambda row: row.get("incident_date", ""), reverse=True)[:limit]
        return [
            {
                "incident_date": row.get("incident_date"),
                "title": row.get("title"),
                "root_cause": row.get("root_cause"),
                "severity": row.get("severity"),
            }
            for row in matches
        ]

    def _root_cause_suggestions(self, incidents: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> List[str]:
        causes = Counter()
        for row in incidents:
            cause = str(row.get("root_cause", "")).strip()
            if cause:
                causes[cause] += 1
        for chunk in chunks:
            content = chunk.get("content", "").lower()
            if "lubrication" in content:
                causes["Lubrication deficiency"] += 1
            if "vibration" in content:
                causes["Mechanical wear or imbalance"] += 1
            if "corrosion" in content:
                causes["Corrosion or material degradation"] += 1
            if "seal" in content:
                causes["Seal degradation or leakage"] += 1
        return [cause for cause, _ in causes.most_common(4)] or ["Insufficient historical evidence"]

    def _lessons_learned(self, incidents: List[Dict[str, Any]]) -> List[str]:
        cause_counts = Counter(str(row.get("root_cause", "Unknown")) for row in incidents)
        lessons = []
        for cause, count in cause_counts.most_common(3):
            lessons.append(f"{count} historical incident(s) indicate recurring cause: {cause}.")
        if not lessons:
            lessons.append("No prior failures stored yet. The memory engine will strengthen with every upload.")
        return lessons

    def _actions_from_risk(self, risk_score: float, suggestions: List[str]) -> List[str]:
        if risk_score >= 0.75:
            return [
                "Inspect critical components within 48 hours.",
                "Compare vibration, temperature, and lubrication trends against the last failure window.",
                "Schedule a root-cause review before the next production cycle.",
            ]
        if risk_score >= 0.45:
            return [
                "Increase inspection frequency and verify maintenance completion records.",
                "Check the top suspected failure modes and document findings.",
            ]
        return [
            "Continue monitoring and retain the evidence trail for future comparison.",
        ]

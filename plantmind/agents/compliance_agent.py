from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from ..core.models import ComplianceResult


class ComplianceAgent:
    def __init__(self):
        self.requirements = {
            "Factory Act": ["safety", "inspection", "training", "emergency"],
            "OISD": ["permit to work", "hazard", "isolation", "ppe", "inspection"],
            "Safety SOP": ["procedure", "lockout", "tagout", "responsibility", "emergency"],
        }

    def evaluate(self, text: str) -> ComplianceResult:
        lower = text.lower()
        missing = []
        matches = 0
        total = 0
        for framework, terms in self.requirements.items():
            for term in terms:
                total += 1
                if term in lower:
                    matches += 1
                else:
                    missing.append(f"{framework}: missing '{term}'")
        compliance_percent = round((matches / total) * 100 if total else 0.0, 1)
        audit_readiness = round(min(100.0, compliance_percent + 12.0), 1)
        recommendations = [
            "Close the missing safety controls before release to operations.",
            "Add explicit evidence references to inspection and training records.",
        ] if missing else ["Coverage looks healthy. Keep audit evidence current."]
        return ComplianceResult(
            compliance_percent=compliance_percent,
            audit_readiness_score=audit_readiness,
            missing_requirements=missing[:8],
            recommendations=recommendations,
        )


from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from ..core.models import CopilotAnswer
from ..llm import GeminiOrchestrator


class EngineerCopilotAgent:
    def __init__(self, memory, store):
        self.memory = memory
        self.store = store
        self.llm = GeminiOrchestrator()

    def answer(self, question: str, top_k: int = 5) -> CopilotAnswer:
        matches = self.memory.query(question, top_k=top_k)
        if not matches:
            return CopilotAnswer(
                answer="I could not find relevant evidence yet. Upload maintenance, inspection, or incident records and I will start building the memory graph.",
                citations=[],
                follow_up_questions=["Which equipment asset should I inspect?", "Do you want a failure comparison or compliance review?"],
            )

        evidence_lines = []
        citations = []
        for item in matches:
            meta = item.get("metadata", {})
            source_name = meta.get("document_name", "Unknown source")
            page = meta.get("page_number")
            excerpt = item.get("content", "")[:220]
            citations.append(
                {
                    "document_name": source_name,
                    "page_number": page,
                    "chunk_id": item.get("chunk_id"),
                    "excerpt": excerpt,
                }
            )
            evidence_lines.append(f"- {source_name}{f' p.{page}' if page else ''}: {excerpt}")

        answer = (
            "I found the most relevant industrial memory signals:\n"
            + "\n".join(evidence_lines)
            + "\n\nUse these records to validate the failure hypothesis and confirm the latest maintenance actions."
        )
        answer = self.llm.enhance_answer(question, evidence_lines, answer)
        return CopilotAnswer(
            answer=answer,
            citations=citations,
            follow_up_questions=["What is the most likely root cause?", "Show me similar incidents for this equipment."],
        )

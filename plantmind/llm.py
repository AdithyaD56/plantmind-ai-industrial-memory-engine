from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .core.config import CONFIG

try:
    from groq import Groq
except Exception:  # pragma: no cover - optional dependency
    Groq = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None

try:
    from langchain_core.prompts import ChatPromptTemplate
except Exception:  # pragma: no cover - optional dependency
    ChatPromptTemplate = None


@dataclass
class LLMResponse:
    text: str


class GeminiOrchestrator:
    def __init__(self):
        self.provider = None
        self.model_name = None
        self.client = None
        if CONFIG.groq_api_key and Groq is not None:
            self.provider = "groq"
            self.model_name = CONFIG.groq_model
            self.client = Groq(api_key=CONFIG.groq_api_key)
        elif CONFIG.gemini_api_key and genai is not None:
            self.provider = "gemini"
            self.model_name = CONFIG.gemini_model
            genai.configure(api_key=CONFIG.gemini_api_key)
            self.client = genai.GenerativeModel(self.model_name)

    def enhance_answer(self, question: str, evidence: List[str], fallback_answer: str) -> str:
        if not self.provider or not self.client:
            return fallback_answer
        prompt = self._build_prompt(question, evidence, fallback_answer)
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are PlantMind AI, an industrial reliability assistant. Answer concisely and cite evidence from the provided excerpts."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                text = response.choices[0].message.content or fallback_answer
            else:
                response = self.client.generate_content(prompt)
                text = getattr(response, "text", "") or fallback_answer
            return text.strip() or fallback_answer
        except Exception:
            return fallback_answer

    def _build_prompt(self, question: str, evidence: List[str], fallback_answer: str) -> str:
        evidence_block = "\n".join(f"- {item}" for item in evidence[:6])
        if ChatPromptTemplate is not None:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are PlantMind AI, an industrial reliability assistant. Answer concisely and cite evidence from the provided excerpts."),
                    ("user", "Question: {question}\nEvidence:\n{evidence}\nFallback:\n{fallback}"),
                ]
            )
            return prompt.format(question=question, evidence=evidence_block, fallback=fallback_answer)
        return (
            "You are PlantMind AI, an industrial reliability assistant. "
            f"Question: {question}\nEvidence:\n{evidence_block}\nFallback:\n{fallback_answer}"
        )

from __future__ import annotations

import re
from typing import Iterable, List


EQUIPMENT_PATTERN = re.compile(r"\b([A-Z]{1,3}[- ]?\d{2,4}[A-Z]?)\b")
LOCATION_PATTERN = re.compile(r"\b(?:Unit|Area|Plant|Line|Train|Block|Section)\s+[A-Z0-9\-]+\b", re.I)
DATE_PATTERN = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4})\b",
    re.I,
)
PERSON_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b")
FAILURE_PATTERN = re.compile(r"\b(vibration|leak|trip|overheat|corrosion|bearing failure|seal failure|downtime|alarm|pressure drop|jam|crack)\b", re.I)
REGULATION_PATTERN = re.compile(r"\b(Factory Act|OISD|OSHA|permit to work|lockout tagout|LOTO|NFPA)\b", re.I)


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> List[str]:
    text = normalize_spaces(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    text = normalize_spaces(text)
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(0, end - overlap)
    return [chunk for chunk in chunks if chunk]


def unique_matches(pattern: re.Pattern[str], text: str) -> List[str]:
    seen = []
    for match in pattern.findall(text):
        value = match.strip()
        if value and value not in seen:
            seen.append(value)
    return seen


def extract_entities(text: str) -> dict:
    procedures = []
    for line in text.splitlines():
        clean = normalize_spaces(line)
        if re.search(r"\b(procedure|sop|steps?)\b", clean, re.I):
            procedures.append(clean[:120])
    return {
        "equipment_ids": unique_matches(EQUIPMENT_PATTERN, text),
        "locations": unique_matches(LOCATION_PATTERN, text),
        "dates": unique_matches(DATE_PATTERN, text),
        "personnel": unique_matches(PERSON_PATTERN, text),
        "failure_modes": unique_matches(FAILURE_PATTERN, text),
        "procedures": procedures[:5],
        "regulations": unique_matches(REGULATION_PATTERN, text),
    }

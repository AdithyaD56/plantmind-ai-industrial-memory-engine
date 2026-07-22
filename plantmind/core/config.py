from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "plantmind.db"
CHROMA_DIR = DATA_DIR / "chroma"
SAMPLE_DIR = BASE_DIR / "sample_data"

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "PlantMind AI"
    host: str = os.getenv("PLANTMIND_HOST", "0.0.0.0")
    port: int = int(os.getenv("PLANTMIND_PORT", "8000"))
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    sqlite_path: Path = DB_PATH
    chroma_dir: Path = CHROMA_DIR
    upload_dir: Path = UPLOAD_DIR
    sample_dir: Path = SAMPLE_DIR
    default_top_k: int = int(os.getenv("PLANTMIND_TOP_K", "5"))


CONFIG = AppConfig()

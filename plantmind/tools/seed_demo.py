from __future__ import annotations

from pathlib import Path
import tempfile


def seed_demo_data(service) -> None:
    demo_dir = Path(__file__).resolve().parents[2] / "sample_data"
    if not demo_dir.exists():
        return
    for path in sorted(demo_dir.glob("*")):
        if path.is_file():
            service.ingest_file(path, path.name, path.suffix.lstrip("."))


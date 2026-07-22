# PlantMind AI Architecture

## Core Principle

PlantMind AI is built as an industrial memory system first, and a conversational assistant second.

## Layers

1. Ingestion Layer
   - PDFs, drawings, reports, SOPs, spreadsheets, CSV, and JSON
   - OCR fallback for scanned content

2. Intelligence Layer
   - Entity extraction
   - Chunking and embeddings
   - Incident and failure pattern recognition
   - Compliance checks

3. Memory Layer
   - SQLite for persistent records
   - ChromaDB for semantic memory
   - NetworkX for industrial graph relationships

4. Experience Layer
   - Streamlit dashboard
   - Proactive alerts
   - Engineer copilot with citations

## Main Data Flow

Document Upload -> OCR/Text Parsing -> Entity Extraction -> Knowledge Graph -> Failure Intelligence -> Risk Alerts -> Engineer Copilot

## Design Choices

- TF-IDF fallback keeps the app low-cost and fast
- Optional Groq or Gemini can improve the copilot response quality when available
- Graph and vector stores persist across sessions

## Future Scope

- Add P&ID parsing and symbol detection with computer vision
- Add a formal industrial ontology for stronger reasoning across plant assets
- Connect the system to CMMS and ERP tools for work-order awareness
- Expand trend analysis for predictive maintenance on rotating equipment
- Support multi-site deployment so lessons learned can be shared across plants

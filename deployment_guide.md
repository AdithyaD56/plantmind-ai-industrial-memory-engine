# Deployment Guide

## Streamlit Cloud

1. Push the repository to GitHub.
2. Set the main file to `streamlit_app.py`.
3. Add secrets or environment variables if Gemini is enabled.
4. Ensure `requirements.txt` is present.

## Local / Container

Backend:

```bash
uvicorn plantmind.api.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
streamlit run streamlit_app.py
```

## Environment Variables

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `PLANTMIND_HOST`
- `PLANTMIND_PORT`

## Operational Notes

- SQLite database is created automatically under `data/`
- ChromaDB persistence is created under `data/chroma/`
- Uploaded files are temporarily stored and cleaned up after ingestion

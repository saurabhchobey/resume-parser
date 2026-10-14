# Resume Parser

Production-oriented resume parsing service with a FastAPI REST API and Streamlit web UI. It accepts PDF and DOCX files, extracts their text safely, sends the content to an LLM for schema-constrained extraction, and stores the normalized result for retrieval.

## Features

- `POST /api/upload` for PDF/DOCX uploads.
- `GET /api/resume/{document_id}` for retrieval.
- Gemini structured output with a configurable model.
- PyMuPDF and python-docx text extraction.
- Pydantic validation, request limits, extension/content checks, UUID document IDs, structured logs, and clear HTTP errors.
- Streamlit interface for upload, processing, and organized result display.
- Unit tests that do not require an API key.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Set GEMINI_API_KEY in .env
uvicorn app.main:app --reload
```

In another terminal:

```powershell
streamlit run ui/streamlit_app.py
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/upload \
  -F "file=@resume.pdf"
curl http://127.0.0.1:8000/api/resume/<document_id>
```

The default repository is an in-memory store, suitable for a single-process take-home deployment. The repository interface is deliberately isolated so it can be replaced with Postgres/Redis without changing routes or parsing logic.

## Configuration

See `.env.example`. The default is `gemini-3.5-flash-lite`; `GEMINI_MODEL` can be changed to another supported Gemini model. The API key is never hardcoded or returned in responses.

## Testing

```powershell
pytest
```

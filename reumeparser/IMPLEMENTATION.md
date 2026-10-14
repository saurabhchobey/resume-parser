# Implementation walkthrough

## 1. Requirements mapped to the product

The take-home asks for PDF/DOCX uploads, LLM-based extraction, a FastAPI API, a Streamlit UI, validation, logging, error handling, and setup documentation. The project implements all of these in separate modules so each concern can be tested independently.

## 2. Processing flow

1. FastAPI receives a multipart upload and validates the filename, extension, and configured size limit.
2. The parser extracts text using PyMuPDF for PDF files or `python-docx` for DOCX files.
3. Empty or unreadable documents are rejected with a client-safe error.
4. `GeminiResumeExtractor` sends the text to Gemini using JSON structured output and the strict Pydantic response schema. The prompt explicitly requests only evidence found in the resume and empty arrays/nulls when information is absent.
5. The validated result receives a UUID document ID, source filename, and UTC creation timestamp.
6. The repository stores the result and the API returns it. Retrieval returns HTTP 404 for an unknown ID.

## 3. Architecture

- `app/config.py`: environment-backed settings and limits.
- `app/models.py`: request-independent domain schemas and API response models.
- `app/services/document_extractor.py`: PDF/DOCX text extraction.
- `app/services/llm_service.py`: LLM protocol and Gemini implementation.
- `app/services/parser.py`: orchestration and persistence boundary.
- `app/repository.py`: repository protocol and in-memory implementation.
- `app/api.py`: HTTP routes, validation, and status-code mapping.
- `app/main.py`: application composition and startup configuration.
- `ui/streamlit_app.py`: thin client of the REST API.

The LLM service is injected into the parser. Tests can provide a fake extractor, which makes validation and API behavior deterministic without network access or credentials.

## 4. Extraction rules

The normalized schema includes contact information, professional summary, work experience, education, technical and soft skills, certifications, and an `additional_information` field for useful details such as links or languages. The prompt requires dates and years to remain faithful to the source and forbids invented facts.

## 5. Robustness choices

- File extensions and MIME types are checked, but the extension is treated as the canonical user-facing error because browser MIME values are inconsistent.
- Upload size is enforced while streaming chunks, avoiding an unbounded `read()`.
- Temporary upload bytes are processed in memory and are not persisted by default; only normalized extracted data is retained in the repository.
- LLM failures are logged with context and returned as a generic 502 response rather than leaking provider details.
- Pydantic validates both LLM output and API serialization.
- Logs include event names, document IDs, and filenames without logging resume contents or secrets.

## 6. Running and extending it

Set `GEMINI_API_KEY` and `GEMINI_MODEL` (default `gemini-3.5-flash-lite`), install `requirements.txt`, run Uvicorn, and optionally run Streamlit. For a multi-instance deployment, replace `InMemoryResumeRepository` with a database-backed implementation and add authentication, malware scanning, rate limiting, and encrypted object storage before accepting untrusted production traffic.


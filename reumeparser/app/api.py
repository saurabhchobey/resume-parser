"""FastAPI routes for resume parsing."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.models import HealthResponse, ResumeRecord
from app.services.document_extractor import DocumentExtractionError
from app.services.llm_service import LLMExtractionError
from app.services.parser import ResumeParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


def get_parser() -> ResumeParser:
    """Dependency replaced by the application composition in `main.py`."""

    raise RuntimeError("Parser dependency has not been configured")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report service liveness."""

    return HealthResponse()


@router.post("/upload", response_model=ResumeRecord, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    parser: ResumeParser = Depends(get_parser),
    settings: Settings = Depends(get_settings),
) -> ResumeRecord:
    """Upload and parse one PDF or DOCX resume."""

    filename = file.filename or "unnamed"
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix not in {"pdf", "docx"}:
        raise HTTPException(status_code=415, detail="Only PDF and DOCX files are supported.")

    content = bytearray()
    while chunk := await file.read(1024 * 1024):
        content.extend(chunk)
        if len(content) > settings.max_upload_size_bytes:
            raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb} MB limit.")

    try:
        return parser.parse(filename, bytes(content))
    except DocumentExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMExtractionError as exc:
        logger.exception("resume_llm_failure", extra={"source_filename": filename})
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("resume_unexpected_failure", extra={"source_filename": filename})
        raise HTTPException(status_code=500, detail="Unexpected resume processing failure.") from exc


@router.get("/resume/{document_id}", response_model=ResumeRecord)
def get_resume(document_id: UUID, parser: ResumeParser = Depends(get_parser)) -> ResumeRecord:
    """Retrieve a parsed resume by document ID."""

    record = parser.get(document_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Resume document not found.")
    return record


"""Resume parsing orchestration."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models import ResumeRecord
from app.repository import ResumeRepository
from app.services.document_extractor import extract_text
from app.services.llm_service import ResumeExtractor

logger = logging.getLogger(__name__)


class ResumeParser:
    """Coordinates document extraction, LLM extraction, and persistence."""

    def __init__(self, extractor: ResumeExtractor, repository: ResumeRepository) -> None:
        self.extractor = extractor
        self.repository = repository

    def parse(self, filename: str, content: bytes) -> ResumeRecord:
        """Parse and persist one uploaded resume."""

        text = extract_text(filename, content)
        logger.info(
            "resume_text_extracted",
            extra={"source_filename": filename, "character_count": len(text)},
        )
        data = self.extractor.extract(text)
        record = ResumeRecord(
            **data.model_dump(),
            document_id=uuid4(),
            filename=filename,
            created_at=datetime.now(timezone.utc),
        )
        self.repository.save(record)
        logger.info(
            "resume_parsed",
            extra={"document_id": str(record.document_id), "source_filename": filename},
        )
        return record

    def get(self, document_id: UUID) -> ResumeRecord | None:
        """Retrieve one persisted result."""

        return self.repository.get(document_id)


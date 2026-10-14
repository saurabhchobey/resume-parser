"""Persistence abstractions for parsed resumes."""

from typing import Protocol
from uuid import UUID

from app.models import ResumeRecord


class ResumeRepository(Protocol):
    """Storage contract used by the parser and API."""

    def save(self, record: ResumeRecord) -> ResumeRecord: ...

    def get(self, document_id: UUID) -> ResumeRecord | None: ...


class InMemoryResumeRepository:
    """Process-local repository for the take-home deployment."""

    def __init__(self) -> None:
        self._records: dict[UUID, ResumeRecord] = {}

    def save(self, record: ResumeRecord) -> ResumeRecord:
        self._records[record.document_id] = record
        return record

    def get(self, document_id: UUID) -> ResumeRecord | None:
        return self._records.get(document_id)


"""Validated domain and API models."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ContactInformation(BaseModel):
    """Resume contact details."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None


class WorkExperience(BaseModel):
    """One employment entry."""

    company: str
    role: str
    duration: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """One education entry."""

    degree: str
    institution: str
    year: str | None = None


class ResumeData(BaseModel):
    """Schema emitted by the LLM and returned to clients."""

    contact_information: ContactInformation = Field(default_factory=ContactInformation)
    professional_summary: str | None = None
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    additional_information: list[str] = Field(default_factory=list)


class ResumeRecord(ResumeData):
    """Persisted resume result."""

    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    filename: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


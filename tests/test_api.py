"""API behavior tests with a deterministic fake extractor."""

from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from docx import Document

from app.api import get_parser
from app.main import app
from app.models import ContactInformation, ResumeData
from app.repository import InMemoryResumeRepository
from app.services.parser import ResumeParser


class FakeExtractor:
    def extract(self, resume_text: str) -> ResumeData:
        return ResumeData(contact_information=ContactInformation(name="Ada Lovelace"), technical_skills=["Python"])


def client() -> tuple[TestClient, InMemoryResumeRepository]:
    repository = InMemoryResumeRepository()
    app.dependency_overrides[get_parser] = lambda: ResumeParser(FakeExtractor(), repository)
    return TestClient(app), repository


def docx_bytes() -> bytes:
    document = Document()
    document.add_paragraph("Ada Lovelace\nPython")
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def test_upload_and_get_resume() -> None:
    http, _ = client()
    response = http.post("/api/upload", files={"file": ("resume.docx", docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert response.status_code == 201
    payload = response.json()
    assert payload["contact_information"]["name"] == "Ada Lovelace"
    fetched = http.get(f"/api/resume/{payload['document_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["filename"] == "resume.docx"


def test_rejects_unsupported_extension() -> None:
    http, _ = client()
    response = http.post("/api/upload", files={"file": ("resume.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_missing_document_is_404() -> None:
    http, _ = client()
    response = http.get(f"/api/resume/{uuid4()}")
    assert response.status_code == 404


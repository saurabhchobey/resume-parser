"""LLM integration for schema-constrained resume extraction."""

from typing import Protocol

from google import genai
from google.genai import types

from app.models import ResumeData


class LLMExtractionError(RuntimeError):
    """Raised when the configured LLM cannot return valid resume data."""


class ResumeExtractor(Protocol):
    """Protocol allowing the parser to be tested without a provider."""

    def extract(self, resume_text: str) -> ResumeData: ...


SYSTEM_PROMPT = """You extract structured data from resumes. Use only facts explicitly present in the resume.
Never infer or invent an employer, date, degree, skill, contact detail, or certification.
Return null for unknown scalar values and [] for unknown lists. Preserve date wording from the source.
Separate technical skills from interpersonal/soft skills. Keep responsibilities as concise bullet statements.
The output must match the supplied ResumeData schema exactly."""


class GeminiResumeExtractor:
    """Gemini structured-output extractor using the official Google GenAI SDK."""

    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract(self, resume_text: str) -> ResumeData:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{SYSTEM_PROMPT}\n\nResume text:\n\n{resume_text}",
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=ResumeData,
                ),
            )
            if not response.text:
                raise ValueError("Provider returned no parsed result")
            return ResumeData.model_validate_json(response.text)
        except Exception as exc:
            raise LLMExtractionError(
                f"Gemini request failed for model '{self.model}'. "
                "Verify GEMINI_MODEL and that this model is available to your API key."
            ) from exc


class UnavailableResumeExtractor:
    """Extractor used when deployment credentials have not been configured."""

    def extract(self, resume_text: str) -> ResumeData:
        """Raise a provider error that the API maps to HTTP 502."""

        raise LLMExtractionError("Resume extraction is not configured. Set GEMINI_API_KEY.")


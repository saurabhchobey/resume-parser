"""Application factory and dependency composition."""

import logging
import sys

from fastapi import FastAPI

from app.api import get_parser, router
from app.config import get_settings
from app.repository import InMemoryResumeRepository
from app.services.llm_service import GeminiResumeExtractor, UnavailableResumeExtractor
from app.services.parser import ResumeParser


def configure_logging(level: str) -> None:
    """Configure concise structured key/value logging."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )


def create_app() -> FastAPI:
    """Build the FastAPI application and its dependencies."""

    settings = get_settings()
    configure_logging(settings.log_level)
    repository = InMemoryResumeRepository()
    extractor = GeminiResumeExtractor(settings.gemini_api_key, settings.gemini_model) if settings.gemini_api_key else UnavailableResumeExtractor()

    app = FastAPI(title="Resume Parser API", version="1.0.0", description="LLM-powered resume parsing service")
    parser = ResumeParser(extractor, repository)
    app.dependency_overrides[get_parser] = lambda: parser
    app.include_router(router)
    return app
app = create_app()


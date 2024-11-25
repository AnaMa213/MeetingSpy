# app/__init__.py
from .routes.diarization_controller import router as diarization_router
from .routes.main_controller import router as main_router
from .routes.transcription_controller import router as transcription_router

__all__ = ["diarization_router", "transcription_router", "main_router"]

# app/__init__.py

# Importer le module FastAPI de l'application
from .main_controller import app  # On garde l'import relatif pour assurer l'accessibilité depuis app

# Importer les fonctions principales des autres modules
from .diarization import diarize_audio
from .transcription import transcribe_audio
from .separation import separate_sources

# Liste des éléments disponibles pour import
__all__ = [
    "app",
    "diarize_audio",
    "transcribe_audio",
    "separate_sources"
]

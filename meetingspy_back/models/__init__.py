# models/__init__.py

# Importer les configurations et fonctions de chargement de modèles
from .models_config import DIARIZATION_MODEL_PATH, TRANSCRIPTION_MODEL,SEPARATION_MODEL_PATH
from .load_model import load_diarization_model, load_transcription_model

# Liste des éléments disponibles pour import
__all__ = [
    "DIARIZATION_MODEL_PATH",
    "TRANSCRIPTION_MODEL",
    "SEPARATION_MODEL_PATH",
    "load_diarization_model",
    "load_transcription_model"
]

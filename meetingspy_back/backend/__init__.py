# app/__init__.py

# Importer le module FastAPI de l'application
from .main_controller import app  # On garde l'import relatif pour assurer l'accessibilité depuis app

# Importer les fonctions principales des autres modules
from .diarization import SpeakerDiarizer
from .transcription import assign_speaker_name, transcript_to_dictionary
from .separation import separate_audio_sources
from .post_processing import merge_close_segments
from .post_processing import generate_combined_transcriptions

# Liste des éléments disponibles pour import
__all__ = [
    "app",
    "SpeakerDiarizer",
    "assign_speaker_name",
    "transcript_to_dictionary",
    "separate_audio_sources",
    "merge_close_segments",
    "generate_combined_transcriptions"
]

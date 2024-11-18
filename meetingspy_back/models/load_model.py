import whisper
from pyannote.audio import Pipeline

from meetingspy_back.models.models_config import DIARIZATION_MODEL_PATH, TRANSCRIPTION_MODEL


def load_diarization_model():
    """
    Returns a Pyannote Pipeline for speaker diarization.

    The returned pipeline is loaded from the "pyannote/speaker-diarization" model.

    Returns
    -------
    pyannote.audio.Pipeline
    """
    return Pipeline.from_pretrained(DIARIZATION_MODEL_PATH, use_auth_token="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")

def load_transcription_model():
    """
    Returns a Whisper model for audio transcription.

    The returned model is the Whisper "base" model.

    Returns
    -------
    whisper.model.Whisper
    """
    return whisper.load_model(TRANSCRIPTION_MODEL)

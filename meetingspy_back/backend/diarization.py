import os, torch
from meetingspy_back.models.load_model import load_diarization_model
from meetingspy_back.services.audio_utils import get_audio_segment

pipeline = load_diarization_model()
pipeline.to(torch.device("cuda"))

def diarize_audio(audio_path, num_speakers):
    # Diarisation de l'audio
    """
    Diarize an audio file and return the path to the RTTM file.

    Parameters
    ----------
    audio_path : str
        The path to the audio file to diarize.
    num_speakers : int
        The number of speakers in the audio file.

    Returns
    -------
    str
        The path to the RTTM file containing the diarization result.
    """
    try:
        # Diarisation avec PyAnnote
        if num_speakers:
            diarization = pipeline(audio_path, num_speakers=num_speakers)
        else:
            diarization = pipeline(audio_path)
        
        # Sauvegarder la sortie RTTM dans un fichier
        rttm_file_path = "temp/audio.rttm"
        os.makedirs("temp", exist_ok=True)  # Crée le dossier temporaire s'il n'existe pas
        with open(rttm_file_path, "w", encoding="utf-8") as rttm:
            diarization.write_rttm(rttm)
        
        segments = get_audio_segment(diarization)
        return  segments, rttm_file_path

    except Exception as e:
        raise RuntimeError(f"Erreur lors de la diarisation : {e}") from e

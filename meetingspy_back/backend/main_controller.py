import os
import logging
from fastapi import FastAPI, File, UploadFile
from meetingspy_back.backend.logging_config import setup_logging
from meetingspy_back.services.audio_utils import  convert_to_wav
from .diarization import SpeakerDiarizer


# Configurer les logs
setup_logging()
logger = logging.getLogger("main_controller")

app = FastAPI()

@app.post("/process_audio")
async def process_audio_pyannote(file: UploadFile = File(...), num_speakers: int = 4):
    """
    Traitement d'un fichier audio pour diarisation et transcription.

    La diarisation est faite en utilisant la bibliothèque pyannote et la transcription est faite en utilisant la bibliothèque whisper.

    :param file: Fichier audio à traiter
    :type file: UploadFile
    :param num_speakers: Nombre de locuteurs dans l'audio, par défaut 2
    :type num_speakers: int
    :return: Un dictionnaire avec la transcription de l'audio
    :rtype: dict
    """
    # Sauvegarde temporaire du fichier audio
    temp_dir = "temp/uploads"
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, file.filename)
    
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Remplacer les espaces par des underscores dans le chemin du fichier
    sanitized_audio_path = audio_path.replace(" ", "_")
    os.rename(audio_path, sanitized_audio_path)
    
    # Conversion en WAV si nécessaire
    wav_path = convert_to_wav(sanitized_audio_path)
    
    logger.info("Initializing SpeakerDiarizer...")
    diarizer = SpeakerDiarizer(num_speakers=num_speakers)
    
    logger.info("Running diarization...")
    transcript = diarizer.diarize(wav_path, temp_dir)
    
    # Retourner toutes les transcriptions combinées
    return {"transcription": transcript}

if __name__ == "__main__":
    import uvicorn
    logging.getLogger("main_controller").info("Starting FastAPI server...")
    uvicorn.run(
        "meetingspy_back.backend.main_controller:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Désactive la configuration de log par défaut d'Uvicorn
        log_level="debug"
    )



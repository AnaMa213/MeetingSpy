import os
from fastapi import FastAPI, File, UploadFile
from meetingspy_back.services.audio_utils import convert_to_wav
from .diarization import diarize_audio
from .transcription import transcribe_audio

app = FastAPI()

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...), num_speakers: int = 2):
    # Sauvegarde temporaire du fichier audio
    """
    Traitement d'un fichier audio pour diarisation et transcription.

    La diarisation est faite en utilisant la bibliothèque pyannote et la transcription est faite en utilisant la bibliothèque whisper.

    :param file: Fichier audio  traiter
    :type file: UploadFile
    :param num_speakers: Nombre de locuteurs dans l'audio, par d faut 2
    :type num_speakers: int
    :return: Un dictionnaire avec la transcription de l'audio
    :rtype: dict
    """
    audio_path = f"temp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Remplacer les espaces par des underscores dans le chemin du fichier
    sanitized_audio_path = audio_path.replace(" ", "_")
    os.rename(audio_path, sanitized_audio_path)
    # Conversion en WAV si nécessaire
    wav_path = convert_to_wav(sanitized_audio_path)

    # Diarisation de l'audio
    segments, rttm_path = diarize_audio(wav_path, num_speakers)

    # Transcription de l'audio avec les segments du fichier RTTM
    transcription = transcribe_audio(segments, rttm_path, wav_path)

    # Nettoyage des fichiers temporaires
    os.remove(wav_path)
    os.remove(rttm_path)

    return {"transcription": transcription}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
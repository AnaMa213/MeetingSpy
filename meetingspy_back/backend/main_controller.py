import os
import shutil
from fastapi import FastAPI, File, UploadFile
from meetingspy_back.backend.transcription import assign_speaker_name, transcript_to_dictionary
from meetingspy_back.services.audio_utils import compress_wav, convert_to_wav
from .diarization import SpeakerDiarizer

app = FastAPI()

@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...), num_speakers: int = 2):
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
    # Conversion en WAV si nécessaire
    compress_path = compress_wav(wav_path)
    
    print("Initializing SpeakerDiarizer...")
    diarizer = SpeakerDiarizer(num_speakers=num_speakers)
    
    print("Running diarization...")
    transcript = diarizer.diarize(compress_path, temp_dir)
    
    # Retourner toutes les transcriptions combinées
    return {"transcription": transcript}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

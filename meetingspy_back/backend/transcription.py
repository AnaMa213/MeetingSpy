
import os
from io import BytesIO
import numpy as np
from scipy.io import wavfile
# Charger le fichier audio et extraire le segment spécifié
from pydub import AudioSegment
from meetingspy_back.models.load_model import load_transcription_model

# Charger le modèle Whisper pour la transcription
model = load_transcription_model()

def transcribe_audio(segments, rttm_path, audio_path):
    # Lire les segments de l'audio à partir du fichier RTTM
    """
    Transcribe an audio file using segments from an RTTM file.

    Parameters
    ----------
    audio_path : str
        The path to the audio file to transcribe.
    rttm_path : str
        The path to the RTTM file containing segment information.

    Returns
    -------
    str
        The transcription of the audio file.
    """

    if not segments:
        print("Aucun segment audio trouvé pour la transcription.")
        return "Aucun segment audio disponible pour la transcription."

    transcription = ""

    try:
        with open(rttm_path, "r", encoding="utf-8") as rttm:
            for line in rttm:
                parts = line.strip().split()
                start_time = float(parts[3])
                duration = float(parts[4])
                speaker = parts[7]
                end_time = start_time + duration

                # Transcrire chaque segment (à adapter avec un vrai modèle)
                audio = AudioSegment.from_wav(audio_path)
                segment = audio[start_time * 1000:end_time * 1000]  # Conversion en millisecondes

                # Sauvegarder le segment temporairement
                segment_path = "temp/segment.wav"
                segment.export(segment_path, format="wav")
                
                result = model.transcribe(segment_path)
                # Supprimer le segment temporaire
                os.remove(segment_path)
                
                transcription += f"{speaker}: {result["text"]}\n"
    
    except Exception as e:
        print(f"Erreur lors de la transcription du segment: {str(e)}")

    return transcription

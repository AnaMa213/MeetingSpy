import os, torch
from whisper import load_model
# Charger le fichier audio et extraire le segment spécifié
from pydub import AudioSegment

model = load_model("large")
def transcribe_segments(file_path, start_time, end_time):
    """
    Transcrit un segment spécifique d'un fichier audio.
    :param file_path: Chemin du fichier audio
    :param start_time: Temps de début du segment à transcrire (en secondes)
    :param end_time: Temps de fin du segment à transcrire (en secondes)
    :return: Transcription du segment
    """
    
    audio = AudioSegment.from_wav(file_path)
    segment = audio[start_time * 1000:end_time * 1000]  # Conversion en millisecondes

    # Sauvegarder le segment temporairement
    segment_path = "temp/segment.wav"
    segment.export(segment_path, format="wav")

    result = model.transcribe(segment_path)

    # Supprimer le segment temporaire
    os.remove(segment_path)

    return result["text"]

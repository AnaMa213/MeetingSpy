import os
from pyannote.audio import Pipeline
import torch

print("Tentative de chargement du modèle avec le token : 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")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="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")
if pipeline is None:
    print("Erreur : Impossible de charger le pipeline PyAnnote.")
pipeline.to(torch.device("cuda"))
    
def diarize_audio(file_path, num_speakers=None):
    """
    Effectue la diarisation sur un fichier audio et renvoie les segments identifiés.
    :param file_path: Chemin du fichier audio
    :param num_speakers: (Optionnel) Nombre d'intervenants attendu
    :return: Une liste de segments et le chemin du fichier RTTM généré
    """
    try:
        # Diarisation avec PyAnnote
        if num_speakers:
            diarization = pipeline(file_path, num_speakers=num_speakers)
        else:
            diarization = pipeline(file_path)
        # Sauvegarder la sortie RTTM dans un fichier
        rttm_file_path = "temp/audio.rttm"
        os.makedirs("temp", exist_ok=True)  # Crée le dossier temporaire s'il n'existe pas
        with open(rttm_file_path, "w", encoding="utf-8") as rttm:
            diarization.write_rttm(rttm)

        # Construire la liste des segments à partir de la sortie du pipeline
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })

        return segments, rttm_file_path

    except Exception as e:
        raise RuntimeError(f"Erreur lors de la diarisation : {e}") from e
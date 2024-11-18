import os
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model
import torchaudio

def separate_sources(audio_path):
    # Charger le modèle pré-entraîné
    """
    Sépare les sources audio d'un fichier audio.

    Parameters
    ----------
    audio_path : str
        Chemin du fichier audio à traiter.

    Returns
    -------
    str
        Chemin du répertoire contenant les sources séparées.
    """
    
    model = get_model("htdemucs")  # Utilise le modèle pré-entraîné nommé "htdemucs"

    # Charger l'audio avec torchaudio
    waveform, sample_rate = torchaudio.load(audio_path)

    # Déplacer le modèle et les données sur GPU si disponible
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    waveform = waveform.to(device)

    # Effectuer la séparation sans spécifier sample_rate (corrige l'erreur)
    with torch.no_grad():
        sources = apply_model(model, waveform)

    # Créer le répertoire de sortie si nécessaire
    demucs_output_dir = "temp/demucs_output"
    os.makedirs(demucs_output_dir, exist_ok=True)

    # Sauvegarder chaque source séparée
    for i, source in enumerate(sources):
        source_path = os.path.join(demucs_output_dir, f"source_{i}.wav")
        torchaudio.save(source_path, source.cpu(), sample_rate)

    return demucs_output_dir

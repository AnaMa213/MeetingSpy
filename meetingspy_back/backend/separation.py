import torch, os, torchaudio
from asteroid.models import ConvTasNet
from meetingspy_back.models.models_config import SEPARATION_MODEL_PATH

def separate_audio_sources(wav_path):
    """
    Sépare les sources audio (par exemple la musique et les voix) d'un fichier wav donné.

    Args:
        wav_path (str): Le chemin vers le fichier wav à traiter.

    Returns:
        str: Le chemin du répertoire où les sources séparées ont été enregistrées.
    """
    try:
        # Charger le fichier audio
        waveform, sr = torchaudio.load(wav_path)
        print(f"Chargement du fichier audio: {wav_path}, Fréquence d'échantillonnage: {sr} Hz")
        target_sr = 16000  # Réduction de la fréquence d'échantillonnage à 16 kHz
        if sr != target_sr:
            waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)(waveform)
            sr = target_sr
        
         # Si le fichier est stéréo, le convertir en mono
        if waveform.ndim == 2 and waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)  # Assurer la forme (1, num_samples)

        # Si le fichier est mono et que la dimension est 1D, ajoutez une dimension pour représenter le canal
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)  # Assurer la forme (1, num_samples)

        
        # Charger le modèle Conv-TasNet pré-entraîné
        model = ConvTasNet.from_pretrained(SEPARATION_MODEL_PATH)
        model.eval()  # Mode évaluation
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        print(f"Modèle Conv-TasNet chargé et placé sur le périphérique: {device}")

        # Déplacer le waveform sur le périphérique
        waveform = waveform.to(device)
        waveform = waveform.unsqueeze(0)

        # Appliquer le modèle pour séparer les sources
        with torch.no_grad():  # Désactiver le gradient pour économiser de la mémoire
            estimates = model(waveform)  # Ajouter une dimension batch pour Conv-TasNet
        print("Séparation des sources effectuée avec succès.")

        # Supprimer la dimension batch
        estimates = estimates.squeeze(0)
        # Créer un répertoire pour sauvegarder les résultats
        separated_dir = os.path.join(os.path.dirname(wav_path), "separated_sources")
        os.makedirs(separated_dir, exist_ok=True)

        # Enregistrer chaque source séparée en tant que fichier wav
        for idx, source in enumerate(estimates):
            # Ajuster la forme du tensor source pour être (num_channels, num_samples)
            if source.ndim == 1:
                source = source.unsqueeze(0)  # Ajouter une dimension de canal pour être (1, num_samples)

            # Normaliser l'audio pour s'assurer qu'il est dans la plage -1 à 1
            max_amplitude = torch.max(torch.abs(source))
            if max_amplitude > 0:
                source = source / max_amplitude
            
            print(f"Forme du tensor source à sauvegarder : {source.shape}")  # Debugging pour vérifier la forme
            output_path = os.path.join(separated_dir, f"source_{idx}.wav")
            torchaudio.save(output_path, source.cpu(), sr)
            print(f"Source {idx} enregistrée dans: {output_path}")

        return separated_dir

    except FileNotFoundError:
        print(f"Erreur: Le fichier {wav_path} est introuvable.")
        return None
    except Exception as e:
        print(f"Une erreur s'est produite pendant la séparation des sources: {e}")
        return None
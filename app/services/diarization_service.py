import logging

import torch
from pyannote.audio import Pipeline as PyannotePipeline

# Utiliser le logger globalement configuré
module_logger = logging.getLogger("diarization_service")


def load_diarizer():
    """
    Charge le pipeline PyAnnote pour la diarisation.

    Le pipeline est chargé à partir du modèle pré-entrainé "pyannote/speaker-diarization-3.1"

    Si un GPU est disponible, le pipeline est transféré sur le GPU. Sinon,
    le CPU est utilisé pour la diarisation.

    Retourne
    -------
    pyannote.audio.Pipeline
        Le pipeline PyAnnote chargé.
    """
    pyannote_pipeline = PyannotePipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token="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",
    )
    if torch.cuda.is_available():
        module_logger.info("Transfert du pipeline PyAnnote sur GPU...")
        pyannote_pipeline = pyannote_pipeline.to(torch.device("cuda"))
    else:
        module_logger.warning("GPU non disponible, utilisation du CPU pour PyAnnote.")
    return pyannote_pipeline


def diarize(path, num_speakers, pipeline):
    """
    Effectue la diarisation d'un fichier audio en utilisant le pipeline PyAnnote.

    Ce processus identifie les locuteurs dans l'enregistrement audio et étiquette
    leurs segments de parole correspondants.

    Paramètres
    ----------
    path : str
        Chemin vers le fichier audio à traiter.
    num_speakers : int
        Nombre attendu de locuteurs dans l'audio.
    pipeline : pyannote.audio.Pipeline
        Le pipeline PyAnnote chargé.

    Retourne
    -------
    tuple
        Un tuple contenant l'objet de diarisation et le chemin du fichier audio.
    """
    module_logger.info("Starting diarization pyannote process.")
    try:
        module_logger.info("Diarizing audio: %s...", path)

        diarization = pipeline(path, num_speakers=num_speakers)
        return diarization, path

    except Exception as e:
        module_logger.error("Error during diarization: %s", str(e))
        raise

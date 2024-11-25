import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.audio_utils_service import convert_to_wav
from app.services.diarization_service import diarize

# import shutil


router = APIRouter()

# Utiliser le logger globalement configuré
module_logger = logging.getLogger("diarization_controller")


@router.post("/process_diarize", summary="Perform speaker diarization")
async def diarization_endpoint(request: Request, path: str, num_speakers: int = 2):
    """
    Endpoint pour effectuer la diarization d'un fichier audio.

    Args:
        file (UploadFile): Le fichier audio téléchargé.
        num_speakers (int): Nombre attendu de locuteurs dans l'audio.
        background_tasks (BackgroundTasks): Permet la gestion des tâches en arrière-plan.

    Returns:
        dict: Résultat de la diarization, y compris les segments par locuteur.
    """

    # Récupérer le fichier
    audio_path = convert_to_wav(path)

    # Utiliser le fichier pour un traitement
    print("Fichier récupéré et sauvegardé avec succès.")

    module_logger.info("Traitement du fichier %s", audio_path)

    try:

        pipeline_diarization = request.app.state.diarization_pipeline

        module_logger.info(
            "Diarization with %d speakers and PyAnnote pipeline.", num_speakers
        )

        # Appeler la fonction de diarization
        diarization_result, processed_audio_path = diarize(
            path=audio_path,
            num_speakers=num_speakers,
            pipeline=pipeline_diarization,
        )
        module_logger.info(
            "Diarization result: %d segments for %d speakers.",
            len(diarization_result),
            num_speakers,
        )

        # Formater le résultat pour le client
        segments = [
            {"start": turn.start, "end": turn.end, "speaker": speaker}
            for turn, _, speaker in diarization_result.itertracks(yield_label=True)
        ]

        # Retourner la réponse en JSONResponse
        return JSONResponse(
            status_code=200,
            content={
                "num_speakers": num_speakers,
                "segments": segments,
                "audio_path": processed_audio_path,
            },
        )
    except (ValueError, TypeError) as e:
        module_logger.error("Erreur de diarization: %s", str(e))
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid input: {str(e)}"},
        )

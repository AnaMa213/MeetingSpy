"""_summary_

Raises:
    HTTPException: _description_
    HTTPException: _description_
    HTTPException: _description_

Returns:
    _type_: _description_
"""

import logging
import os
import shutil

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.transcription_service import transcribe_diarization

router = APIRouter()

logger = logging.getLogger("transcription_controller")


@router.post("/process_transcribe", summary="Transcribe an audio file with diarization")
async def transcription_endpoint(
    request: Request,
    path: str,  # Chemin vers le fichier audio
    segments: list[dict] = None,  # Segments déjà fournis par le service de diarization
):
    """
    Endpoint pour transcrire un fichier audio avec diarisation.

    Args:
        file (UploadFile): Le fichier audio téléchargé.
        segments (list[dict]): Segments de locuteurs avec start, end et speaker.
        background_tasks (BackgroundTasks): Gestionnaire pour effectuer des tâches en arrière-plan.

    Returns:
        dict: Résultat de la transcription avec locuteurs.
    """
    if not os.path.isfile(path):
        raise HTTPException(
            status_code=404, detail=("Fichier non trouvé au chemin : %s" % path)
        )

    # Vérifier les segments
    if not segments:
        raise HTTPException(
            status_code=400, detail="Segments non fournis pour la transcription."
        )

    try:

        logger.debug("Segments reçus pour la transcription : %s", segments)

        transcribe_model = request.app.state.transcription_model
        # Appeler la fonction de transcription
        logger.info("Appel de la fonction de transcription...")
        transcription_result = transcribe_diarization(
            segments=segments, audio_path=path, transcribe_model=transcribe_model
        )

        # Retourner la réponse avec les transcriptions
        logger.info("Transcription réussie : %s", transcription_result)
        return JSONResponse(
            status_code=200,
            content={"transcription": transcription_result},
            media_type="application/json",
        )
    except HTTPException as http_exc:
        original_exc = http_exc.__cause__
        logger.error("Original exception: %s", original_exc)
        logger.error("HTTPException: %s", http_exc)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=("Erreur pendant la transcription : %s" % str(e))
        ) from e

    finally:
        # Nettoyer les fichiers temporaires
        logger.debug("Nettoyage des fichiers temporaires...")
        shutil.rmtree("tmp/", ignore_errors=True)

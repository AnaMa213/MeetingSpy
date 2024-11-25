import logging
import shutil

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.services.audio_utils_service import convert_to_wav
from app.services.diarization_service import diarize
from app.services.transcription_service import transcribe_diarization

router = APIRouter()

module_logger = logging.getLogger("main_controller")


@router.post(
    "/process_audio", summary="Traite un fichier audio en diarisation et transcription."
)
async def process_audio_to_text(request: Request, path: str, num_speakers: int = 2):
    """
    Traite un fichier audio pour effectuer la diarisation et la transcription.

    Args:
        request (Request): La requête FastAPI.
        file (UploadFile): Le fichier audio téléchargé.
        num_speakers (int): Nombre attendu de locuteurs dans l'audio.

    Returns:
        JSONResponse: Réponse JSON contenant le résultat de la transcription.
    """
    # Récupérer le fichier
    audio_path = convert_to_wav(path)

    # Utiliser le fichier pour un traitement
    module_logger.info("Traitement du fichier %s", audio_path)

    try:

        pipeline_diarization = request.app.state.diarization_pipeline

        module_logger.info(
            "Diarization avec %d speakers et PyAnnote pipeline.", num_speakers
        )

        diarization_result, processed_audio_path = diarize(
            path=audio_path,
            num_speakers=num_speakers,
            pipeline=pipeline_diarization,
        )
        module_logger.info(
            "Résultat de la diarization : %d segments pour %d speakers.",
            len(diarization_result),
            num_speakers,
        )

        segments = [
            {"start": turn.start, "end": turn.end, "speaker": speaker}
            for turn, _, speaker in diarization_result.itertracks(yield_label=True)
        ]

        if not segments:
            raise HTTPException(
                status_code=400, detail="Segments non fournis pour la transcription."
            )
        module_logger.debug("Segments reçus pour la transcription : %s", segments)

        transcribe_model = request.app.state.transcription_model
        module_logger.info("Appel de la fonction de transcription...")
        transcription_result = transcribe_diarization(
            segments=segments,
            audio_path=processed_audio_path,
            transcribe_model=transcribe_model,
        )

        module_logger.info("Transcription réussie : %s", transcription_result)
        return JSONResponse(
            status_code=200,
            content={"transcription": transcription_result},
            media_type="application/json",
        )
    except (ValueError, TypeError) as e:
        module_logger.error("Erreur de diarization: %s", str(e))
        return JSONResponse(
            status_code=400,
            content={"detail": f"Entrée invalide: {str(e)}"},
        )
    except HTTPException as http_exc:
        original_exc = http_exc.__cause__
        module_logger.error("Original exception: %s", original_exc)
        module_logger.error("HTTPException: %s", http_exc)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur pendant la transcription : {str(e)}"
        ) from e

    finally:
        module_logger.debug("Nettoyage des fichiers temporaires...")
        shutil.rmtree("tmp/", ignore_errors=True)

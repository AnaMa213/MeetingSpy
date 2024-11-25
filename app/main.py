"""_summary_

Returns:
    _type_: _description_

Yields:
    _type_: _description_
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    diarization_controller,
    main_controller,
    transcription_controller,
)
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.services.diarization_service import load_diarizer
from app.services.transcription_service import load_transcription_model

# Configurer les logs
setup_logging()
logger = logging.getLogger("main_controller")


# Événement au démarrage de l'application
# Handler de cycle de vie pour FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion des événements de cycle de vie de l'application.
    """
    # Code exécuté au démarrage de l'application
    logger.info("Démarrage de l'application...")
    try:
        # Charger les modèles IA au démarrage

        transcription_model = load_transcription_model()
        diarization_pipeline = load_diarizer()
        logger.info("Modèles chargés avec succès.")

        # Stocker les modèles dans app.state
        app.state.transcription_model = transcription_model
        app.state.diarization_pipeline = diarization_pipeline

        yield  # Permet à l'application de s'exécuter

    finally:
        # Code exécuté à l'arrêt de l'application
        logger.info("Arrêt de l'application...")
        app.state.transcription_model = None
        app.state.diarization_pipeline = None


application = FastAPI(
    title=settings.APP_NAME,
    description="API pour diarization, transcription et interaction avec la BDD.",
    version=settings.APP_VERSION,
    docs_url="/docs",  # URL pour la documentation Swagger
    redoc_url="/redoc",  # URL pour la documentation ReDoc
    lifespan=lifespan,  # Gestionnaire de cycle de vie
)

# Inclusion des routes
application.include_router(
    diarization_controller.router, prefix="/diarization", tags=["Diarization"]
)
application.include_router(
    transcription_controller.router, prefix="/transcription", tags=["Transcription"]
)

application.include_router(
    main_controller.router, prefix="/main_process", tags=["Process Audio"]
)

# Configuration CORS
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exemple d'une route pour vérifier l'état de l'application
@application.get("/health", tags=["Health"])
async def health_check():
    """
    Vérifie que l'application est opérationnelle.
    """
    return {"status": "healthy", "app_name": settings.APP_NAME}


# Exemple de route pour vérifier les modèles chargés
@application.get("/status", tags=["Health"])
async def status_check():
    """
    Vérifie l'état des modèles chargés.
    """
    return {
        "transcription_model": bool(application.state.transcription_model),
        "diarization_pipeline": bool(application.state.diarization_pipeline),
    }


# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn

    logger.info(settings.model_dump())
    uvicorn.run(
        "app.main:application",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recharge automatique en mode développement
        log_level="debug",  # Utiliser la valeur de settings.LOG_LEVEL,
    )

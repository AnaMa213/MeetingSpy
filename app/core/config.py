from typing import Optional

import cloudinary
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Backend"  # Nom de l'application
    APP_VERSION: str = "1.0.0"  # Version de l'application
    ENVIRONMENT: str = "DEV"  # Environnement : DEV ou PROD

    # Base de données
    POSTGRES_URL: Optional[str] = None  # URL de connexion à PostgreSQL

    # Logging
    LOG_LEVEL: str = "DEBUG"  # Niveau de log par défaut
    LOG_FILE: str = "application"

    # Modèles IA
    AI_MODEL_PATH: str = "/path/to/your/model"  # Chemin vers le modèle IA
    DIARIZATION_MODEL_PATH: str = (
        "/path/to/diarization/pipeline"  # Chemin vers le pipeline de diarisation
    )

    # Fichiers temporaires
    AUDIO_TEMP_DIR: str = (
        "/tmp/audio_files"  # Répertoire temporaire pour les fichiers audio
    )
    # Configurations Cloudinary
    CLOUDINARY_CLOUD_NAME: str  # Nom du cloud Cloudinary, doit être fourni dans `.env`
    CLOUDINARY_API_KEY: str  # API Key Cloudinary, doit être fourni dans `.env`
    CLOUDINARY_API_SECRET: str  # API Secret Cloudinary, doit être fourni dans `.env`

    # Configuration de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env"
    )  # Charger les variables d'environnement depuis .env


# Instancier les paramètres une seule fois pour l'ensemble du projet
settings = Settings()
# Configurer Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

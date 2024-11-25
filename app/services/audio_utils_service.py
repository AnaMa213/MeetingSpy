import logging
import os
from io import BytesIO

import ffmpeg
import requests
from pydub import AudioSegment

logger = logging.getLogger("audio_utils")


def download_audio_from_cloudinary(url: str) -> BytesIO:
    """
    Télécharge un fichier audio depuis Cloudinary en utilisant l'URL fournie.

    Args:
        url (str): URL du fichier audio sur Cloudinary.

    Returns:
        BytesIO: Flux de données du fichier audio téléchargé.

    Raises:
        requests.exceptions.RequestException: Si une erreur survient lors de la requête.
    """
    try:
        logger.debug("Début du téléchargement de l'audio depuis Cloudinary: %s", url)
        # Télécharger le fichier audio depuis Cloudinary
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Vérifier si la requête est réussie

        logger.info("Téléchargement réussi, conversion en BytesIO de %s", url)
        # Lire le contenu dans un BytesIO
        return BytesIO(response.content)
    except requests.Timeout:
        logger.error("Timeout error: the server did not respond within 10 seconds")
    except requests.exceptions.RequestException as e:
        logger.error(
            "Erreur lors de la récupération du fichier depuis Cloudinary: %s", e
        )
        raise


def convert_to_wav(audio_url: str) -> str:
    """
    Convert an audio file from Cloudinary to a WAV file with a sample rate of 16 kHz and mono using FFmpeg.

    Parameters
    ----------
    audio_url : str
        The URL to the audio file to be downloaded and converted.

    Returns
    -------
    str
        The path to the converted WAV file.
    """
    # Télécharger l'audio depuis Cloudinary
    audio_data = download_audio_from_cloudinary(audio_url)

    # Charger le fichier audio dans pydub
    audio = AudioSegment.from_file(audio_data)

    # Temporary directory for audio segments
    temp_dir = "tmp/"
    os.makedirs(temp_dir, exist_ok=True)
    wav_path = os.path.join(temp_dir, "tmp_audio_file_16000_mono.wav")
    logger.debug("Starting conversion of audio file from URL: %s", audio_url)

    # Sauvegarder le fichier audio téléchargé dans un fichier temporaire
    temp_audio_path = os.path.join(temp_dir, "tmp_audio_file.wav")
    audio.export(temp_audio_path, format="mp3")

    # Conversion en WAV avec FFmpeg
    if not temp_audio_path.endswith(".wav") or not is_16000_mono(temp_audio_path):
        logger.info("Converting file to 16 kHz mono WAV: %s", temp_audio_path)
        (
            ffmpeg.input(temp_audio_path)
            .output(wav_path, ar=16000, ac=1, format="wav")
            .overwrite_output()
            .run()
        )
        logger.debug("Conversion completed. Output file: %s", wav_path)
    else:
        logger.info("File is already 16 kHz mono WAV: %s", temp_audio_path)
        wav_path = temp_audio_path

    return wav_path


def is_16000_mono(audio_path: str) -> bool:
    """
    Vérifie si un fichier audio est en 16 kHz et mono.

    Parameters
    ----------
    audio_path : str
        The path to the audio file.

    Returns
    -------
    bool
        True si le fichier est en 16 kHz et mono, False sinon.
    """
    try:
        probe = ffmpeg.probe(audio_path)
        sample_rate = int(probe["streams"][0]["sample_rate"])
        channels = int(probe["streams"][0]["channels"])
        return sample_rate == 16000 and channels == 1
    except ffmpeg.Error as e:
        logger.error("Erreur lors de la vérification des propriétés audio : %s", e)
        return False

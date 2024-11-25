import logging
import os

import ffmpeg

logger = logging.getLogger("audio_utils")


def delete_temp_file(file_path: str):
    """
    Supprime un fichier temporaire.

    Args:
        file_path (str): Chemin du fichier temporaire à supprimer.

    Returns:
        None
    """
    try:
        if os.path.exists(file_path):  # Vérifie si le fichier existe
            os.remove(file_path)  # Supprime le fichier
            logger.info("Fichier temporaire supprimé : %s", file_path)
        else:
            logger.warning("Fichier temporaire non trouvé : %s", file_path)
    except FileNotFoundError:
        logger.error("Fichier non trouvé : %s", file_path)
    except PermissionError:
        logger.error(
            "Erreur de permission lors de la suppression du fichier %s", file_path
        )
    except OSError as e:
        logger.error(
            "Erreur lors de la suppression du fichier %s : %s", file_path, str(e)
        )


def convert_to_wav(audio_path):
    """
    Convert an audio file to a WAV file with a sample rate of 16 kHz and mono using FFmpeg.

    Parameters
    ----------
    audio_path : str
        The path to the audio file to be converted.

    Returns
    -------
    str
        The path to the converted WAV file.
    """
    # Temporary directory for audio segments
    temp_dir = "tmp/"
    os.makedirs(temp_dir, exist_ok=True)
    wav_path = os.path.join(temp_dir, "tmp_audio_file_16000_mono.wav")
    logger.debug("Starting conversion of audio file: %s", audio_path)

    if not audio_path.endswith(".wav") or not is_16000_mono(audio_path):
        logger.info("Converting file to 16 kHz mono WAV: %s", audio_path)
        (
            ffmpeg.input(audio_path)
            .output(wav_path, ar=16000, ac=1, format="wav")
            .overwrite_output()
            .run()
        )
        logger.debug("Conversion completed. Output file: %s", wav_path)
    else:
        logger.info("File is already 16 kHz mono WAV: %s", audio_path)
        wav_path = audio_path

    return wav_path


def is_16000_mono(audio_path):
    """
    Check if an audio file is already in 16 kHz and mono.

    Parameters
    ----------
    audio_path : str
        Path to the audio file.

    Returns
    -------
    bool
        True if the audio file is in 16 kHz and mono, False otherwise.
    """
    try:
        logger.debug("Starting analysis of audio file: %s", audio_path)
        probe = ffmpeg.probe(audio_path)
        streams = probe.get("streams", [])
        for stream in streams:
            if stream.get("codec_type") == "audio":
                sample_rate = int(stream.get("sample_rate", 0))
                channels = int(stream.get("channels", 0))
                logger.info(
                    "Audio file: %s, sample rate: %d, channels: %d",
                    audio_path,
                    sample_rate,
                    channels,
                )
                return sample_rate == 16000 and channels == 1
        logger.info("No audio stream found in file: %s", audio_path)
        return False
    except ffmpeg.Error as e:
        logger.error("Erreur lors de la vérification du fichier audio : %s", e)
        return False

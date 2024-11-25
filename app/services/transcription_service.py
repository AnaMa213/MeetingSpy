import logging
import os
import shutil

import torch
import whisper
from pydub import AudioSegment

from app.services.utils_service import convert_seconds

# Utiliser le logger globalement configuré
module_logger = logging.getLogger("transcription_service")


def load_transcription_model():
    """
    Charge et retourne le modèle de transcription Whisper.

    Cette fonction vérifie la disponibilité du GPU et transfère le modèle sur le GPU si possible.
    Sinon, le modèle reste sur le CPU.

    Returns
    -------
    whisper.model.Whisper
        Le modèle de transcription chargé.
    """
    transcribe_model = whisper.load_model(
        "large", device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )
    return transcribe_model


def transcribe_diarization(segments, audio_path, transcribe_model):
    """
    Effectue la transcription de diarisation pour un fichier audio.

    Parameters
    ----------
    diarization : pyannote.audio.Pipeline
        Le pipeline de diarisation initialisé avec les paramètres souhaités.
    audio_path : str
        Le chemin vers le fichier audio à traiter.
    transcribe_model : whisper.model.Whisper
        Le modèle de transcription chargé.

    Returns
    -------
    str
        La transcription de diarisation sous forme de texte, avec les noms des
        locuteurs entre crochets.
    """
    module_logger.info("Starting transcription of diarization for %s", audio_path)

    try:

        # Temporary directory for audio segments
        segment_temp_dir = "tmp/temp_segments"
        os.makedirs(segment_temp_dir, exist_ok=True)

        # Step 3: Transcribe Each Segment
        merged_transcripts = []
        audio = AudioSegment.from_file(audio_path)

        current_speaker = None
        current_start = None
        current_text = ""

        for segment in segments:
            start = segment["start"]
            end = segment["end"]
            speaker = segment["speaker"]

            # Vérification des durées et cohérences
            segment_duration = end - start
            if segment_duration < 0.5:
                module_logger.warning(
                    "Skipping segment for %s: too short (%.2f s).",
                    speaker,
                    segment_duration,
                )
                continue
            if start >= end or start < 0:
                module_logger.error(
                    "Skipping segment for %s: invalid start (%.2f s) or end (%.2f s).",
                    speaker,
                    start,
                    end,
                )
                continue

            module_logger.debug(
                "Extracting segment for %s from %.2f s to %.2f s", speaker, start, end
            )

            # Extract the segment
            segment_path = os.path.join(
                segment_temp_dir, f"{speaker}_{start:.2f}_{end:.2f}.wav"
            )
            audio_segment = audio[
                start * 1000 : end * 1000
            ]  # PyDub works in milliseconds
            audio_segment.export(segment_path, format="wav")

            # Transcribe the segment
            result = transcribe_model.transcribe(segment_path, language="fr")
            text = result["text"].strip()

            # Merge logic: Combine consecutive segments of the same speaker
            if speaker == current_speaker:
                # Extend the text and update the end time
                current_text += " " + text
                current_end = convert_seconds(end)
            else:
                # Save the current speaker's text before switching
                if current_speaker is not None:
                    merged_transcripts.append(
                        f"{current_speaker} [{current_start} - {current_end}]: {current_text}"
                    )
                # Start a new speaker
                current_speaker = speaker
                current_start = convert_seconds(start)
                current_end = convert_seconds(end)
                current_text = text

        # Add the final speaker's segment
        if current_speaker is not None:
            merged_transcripts.append(
                f"{current_speaker} [{current_start}- {current_end}]: {current_text}"
            )

        # Return the merged transcripts as a single string
        merged_transcript = "\n\n".join(merged_transcripts)

        module_logger.info("Transcription completed: %s", audio_path)
        return merged_transcript

    finally:
        module_logger.info("Cleaning up temporary directory.")
        shutil.rmtree(segment_temp_dir)

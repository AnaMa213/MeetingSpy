import os
import logging
import shutil
import subprocess
from pyannote.audio import Pipeline as PyannotePipeline
import torch
from pydub import AudioSegment



from meetingspy_back.models.load_model import load_transcription_model

# Utiliser le logger globalement configuré
module_logger = logging.getLogger("diarization")

class SpeakerDiarizer:
    """
    A class for performing speaker diarization on audio files.

    Speaker diarization is the process of identifying the speakers in an audio recording
    and labeling their corresponding speech segments.

    Attributes:
        num_speakers (int): The number of speakers to identify in the diarization process.
        model (object): The transcription model used for diarization.
        embedding_model (object): The speaker embedding model used for diarization.

    Methods:
        __init__(num_speakers): Initializes the SpeakerDiarizer with a specified number of speakers.
        diarize(path, tmp_dir): Performs speaker diarization on an audio file.
    """
    def __init__(self, num_speakers=2):
        """
        Initialize the SpeakerDiarizer with a specified number of speakers.

        Parameters
        ----------
        num_speakers : int, optional
            The number of speakers to identify in the diarization process, by default 2.
        """
        module_logger.info("Initialisation du SpeakerDiarizer avec %d locuteurs", num_speakers)
        self.num_speakers = num_speakers
        self.transcription_model = load_transcription_model()
        if torch.cuda.is_available():
            module_logger.info("Transfert du modèle de transcription sur GPU...")
            self.transcription_model = self.transcription_model.to(torch.device("cuda"))
        else:
            module_logger.warning("GPU non disponible, utilisation du CPU pour la transcription.")

        self.pyannote_pipeline = PyannotePipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="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"
        )
        if torch.cuda.is_available():
            module_logger.info("Transfert du pipeline PyAnnote sur GPU...")
            self.pyannote_pipeline = self.pyannote_pipeline.to(torch.device("cuda"))
        else:
            module_logger.warning("GPU non disponible, utilisation du CPU pour PyAnnote.")


    def convertir_secondes(self, secondes):
        if secondes < 60:
            return f"{secondes:.2f} s"
        else:
            minutes = secondes // 60
            secondes_restantes = secondes % 60
            return f"{minutes:.0f}min{secondes_restantes:.2f}s"  

    def diarize(self, path, tmp_dir):
        """
        Perform speaker diarization on an audio file.

        Parameters
        ----------
        path : str
            The path to the audio file to be processed.

        Returns
        -------
        str
            The transcribed text with speaker labels.
        """
        module_logger.info("Starting diarization pyannote process.")
        try:
            # Copier l'audio original dans le dossier temporaire
            audio_path = os.path.join(tmp_dir, 'audio.wav')
            if path[-3:] != 'wav':
                module_logger.debug("Converting audio to WAV format. (%s)", path)
                subprocess.call(['ffmpeg', '-i', path, audio_path, '-y'])
            else:
                module_logger.debug("Copying WAV audio to temporary directory. (%s)", path)
                shutil.copy(path, audio_path)

            # Charger le pipeline pré-entraîné
            print("Chargement du pipeline PyAnnote...")
            pipeline = PyannotePipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="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")
            
            print(f"Diarizing audio: {audio_path}...")
            diarization = pipeline(audio_path, num_speakers=self.num_speakers)
            transcribe_model = load_transcription_model()

            # Temporary directory for audio segments
            segment_temp_dir = "temp_segments"
            os.makedirs(segment_temp_dir, exist_ok=True)

            # Step 3: Transcribe Each Segment
            merged_transcripts = []
            audio = AudioSegment.from_file(audio_path)

            current_speaker = None
            current_start = None
            current_text = ""
            
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                start = turn.start
                end = turn.end

                # Vérification des durées et cohérences
                segment_duration = end - start
                if segment_duration < 0.5:
                    module_logger.warning("Skipping segment for %s: too short (%.2f s).", speaker, segment_duration)
                    continue
                if start >= end or start < 0:
                    module_logger.error("Skipping segment for %s: invalid start (%.2f s) or end (%.2f s).", speaker, start, end)
                    continue
                # Extract the segment
                segment_path = os.path.join(segment_temp_dir, f"{speaker}_{start:.2f}_{end:.2f}.wav")
                audio_segment = audio[start * 1000:end * 1000]  # PyDub works in milliseconds
                audio_segment.export(segment_path, format="wav")

                # Transcribe the segment
                result = transcribe_model.transcribe(segment_path, language="fr")
                text = result["text"].strip()

                # Merge logic: Combine consecutive segments of the same speaker
                if speaker == current_speaker:
                    # Extend the text and update the end time
                    current_text += " " + text
                    current_end = self.convertir_secondes(end)
                else:
                    # Save the current speaker's text before switching
                    if current_speaker is not None:
                        merged_transcripts.append(
                            f"{current_speaker} [{current_start} - {current_end}]: {current_text}"
                        )
                    # Start a new speaker
                    current_speaker = speaker
                    current_start = self.convertir_secondes(start)
                    current_end = self.convertir_secondes(end)
                    current_text = text
                        
            # Add the final speaker's segment
            if current_speaker is not None:
                merged_transcripts.append(
                    f"{current_speaker} [{current_start}- {current_end}]: {current_text}"
                )

            # Return the merged transcripts as a single string
            return "\n\n".join(merged_transcripts)

        finally:
            module_logger.info("Cleaning up temporary directory.")
            shutil.rmtree(tmp_dir)
            shutil.rmtree(segment_temp_dir)
            


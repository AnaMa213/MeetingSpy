import os
import shutil
import datetime
import subprocess
import contextlib
import wave
import torch
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment

import numpy as np
from sklearn.cluster import AgglomerativeClustering


from meetingspy_back.models.load_model import load_transcription_model


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
        self.num_speakers = num_speakers
        self.model = load_transcription_model()
        self.embedding_model = PretrainedSpeakerEmbedding(
            "speechbrain/spkrec-ecapa-voxceleb",
            device=torch.device("cuda")
        )

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
    
        try:
            # Copier l'audio original dans le dossier temporaire
            audio_path = os.path.join(tmp_dir, 'audio.wav')
            if path[-3:] != 'wav':
                subprocess.call(['ffmpeg', '-i', path, audio_path, '-y'])
            else:
                shutil.copy(path, audio_path)

            # Utiliser le dossier temporaire pour les traitements
            result = self.model.transcribe(audio_path)
            segments = result["segments"]

            with contextlib.closing(wave.open(audio_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)

            embeddings = np.zeros((len(segments), 192))
            for i, segment in enumerate(segments):
                embeddings[i] = self.segment_embedding(segment, audio_path, duration)

            embeddings = np.nan_to_num(embeddings)
            clustering = AgglomerativeClustering(self.num_speakers).fit(embeddings)
            labels = clustering.labels_

            for i, segment in enumerate(segments):
                segment["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

            transcript = self.generate_transcript(segments)
            return transcript

        finally:
            # Supprimer le dossier temporaire
            shutil.rmtree(tmp_dir)

    def segment_embedding(self, segment, path, duration):
        """
        Extract the embedding for a given audio segment.

        Parameters
        ----------
        segment : dict
            A dictionary containing 'start' and 'end' times of the segment.
        path : str
            The path to the audio file.
        duration : float
            The total duration of the audio file.

        Returns
        -------
        numpy.ndarray
            The embedding of the audio segment.
        """
        start = segment["start"]
        end = min(duration, segment["end"])
        clip = Segment(start, end)
        audio = Audio()
        waveform, _ = audio.crop(path, clip)
        return self.embedding_model(waveform[None])

    def generate_transcript(self, segments):
        """
        Generate a transcript from the segments with speaker labels.

        Parameters
        ----------
        segments : list
            A list of dictionaries containing segment information including speaker labels.

        Returns
        -------
        str
            The formatted transcript with speaker labels.
        """
        def time(secs): 
            """
            Format a time in seconds as a datetime.timedelta object.

            Parameters
            ----------
            secs : float
                The time in seconds to be formatted.

            Returns
            -------
            datetime.timedelta
                The formatted time as a datetime.timedelta object.
            """
            return datetime.timedelta(seconds=round(secs))

        transcript = ""
        for i, segment in enumerate(segments):
            if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
                transcript += f"\n{segment['speaker']} {time(segment['start'])}\n"
            transcript += segment["text"][1:] + ' '

        return transcript
